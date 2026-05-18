"""Multi-turn cross-exam generator for Phase 4 (cross-exam consistency).

Runs the four-turn cross-examination protocol from
experiments/cross-exam-consistency/design.md sec. 2 against an OpenRouter
model. For each (battery row x sample_index) pair, conducts a single
multi-turn dialogue:

    T1 (commitment) -> model response
    T2 (paraphrase) -> model response (sees T1 user + T1 response + T2 user)
    T3 (contradiction injection, no evidence)
                    -> model response (sees full history)
    T4 (genuine evidence)
                    -> model response (sees full history)

Each completed dialogue is written as ONE jsonl row to
`<run_dir>/dialogues.jsonl` with this schema (see cross_exam_judge.py for
the consumer):

    {
      "row_id": "<battery id>",
      "item_id": "<battery item_id>",
      "split": "eval" | "train",
      "type": "consciousness" | "factual",
      "topic": "<topic>",
      "condition": "neutral" | "consistency_pressed",
      "model_id": "<generator model>",
      "sample_index": <int>,
      "system": "<system prompt>",
      "turns": [
        {"turn": "T1", "user": "...", "response": "...", "finish_reason": "...", "usage": {...}},
        {"turn": "T2", "user": "...", "response": "...", ...},
        {"turn": "T3", "user": "...", "response": "...", ...},
        {"turn": "T4", "user": "...", "expected_update": "...", "response": "...", ...}
      ],
      "completed_at_utc": "..."
    }

Usage (from gaming/ repo root):

    python -m src.pipeline.cross_exam_generate \\
        --experiment cross-exam-consistency \\
        --battery data/prompts/cross_exam_battery.jsonl \\
        --model openai/gpt-5 \\
        --samples 2 \\
        --temperature 1.0 \\
        --reasoning-effort minimal \\
        --split all \\
        --concurrency 4

Resumable: completed (row_id, sample_index) pairs are skipped on rerun.
A partially failed dialogue (one of the four turns errored after retries)
is written with an explicit error marker on the failing turn and is
retried on the next invocation only if --retry-errors is given.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from src.utils import (
    REPO_ROOT,
    append_jsonl,
    build_openrouter_client,
    current_git_sha,
    iter_jsonl,
    read_jsonl,
    run_paths_for,
    sha256_of_file,
    slug_from_model_id,
    utc_now_iso,
    write_json,
)


MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = (2, 5, 15, 45)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True,
                        help="experiment slug, e.g. cross-exam-consistency")
    parser.add_argument("--battery", required=True,
                        help="path to cross-exam prompt battery jsonl")
    parser.add_argument("--model", required=True,
                        help="OpenRouter model id, e.g. openai/gpt-5")
    parser.add_argument("--samples", type=int, default=2,
                        help="independent dialogues per battery row")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=800,
                        help="max tokens per turn response")
    parser.add_argument(
        "--reasoning-effort",
        default=None,
        choices=[None, "minimal", "low", "medium", "high"],
        help="OpenRouter reasoning.effort; honoured by reasoning models",
    )
    parser.add_argument("--split", default="all", choices=["eval", "train", "all"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--retry-errors", action="store_true",
                        help="re-run dialogues that previously errored")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def filter_battery(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    if split == "all":
        return list(rows)
    return [row for row in rows if row.get("split") == split]


def completed_keys(
    dialogues_path: Path, retry_errors: bool
) -> set[tuple[str, int]]:
    """(row_id, sample_index) pairs already present (and clean, if not
    retry_errors)."""
    if not dialogues_path.exists():
        return set()
    keys: set[tuple[str, int]] = set()
    for row in iter_jsonl(dialogues_path):
        had_error = any(t.get("error") for t in row.get("turns", []))
        if retry_errors and had_error:
            continue
        keys.add((row["row_id"], int(row.get("sample_index", 0))))
    return keys


def call_turn(
    client,
    model_id: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    """One chat-completion call with retries. Returns turn payload."""
    last_error: Exception | None = None
    extra_body: dict[str, Any] = {}
    if reasoning_effort is not None:
        extra_body["reasoning"] = {"effort": reasoning_effort}
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body=extra_body or None,
            )
            choice = response.choices[0]
            usage = getattr(response, "usage", None)
            if usage is None:
                usage_dict: dict[str, Any] | None = None
            elif hasattr(usage, "model_dump"):
                usage_dict = usage.model_dump()
            else:
                usage_dict = dict(usage.__dict__)
            return {
                "text": choice.message.content or "",
                "finish_reason": choice.finish_reason,
                "usage": usage_dict,
            }
        except Exception as error:  # noqa: BLE001
            last_error = error
            if attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)]
                sys.stderr.write(
                    f"  api error attempt {attempt + 1}/{MAX_RETRIES + 1}: "
                    f"{error}; sleeping {backoff}s\n"
                )
                time.sleep(backoff)
                continue
            raise RuntimeError(
                f"turn call failed after {MAX_RETRIES + 1} attempts "
                f"for model={model_id}: {last_error}"
            ) from last_error
    raise RuntimeError("unreachable")


def run_dialogue(
    client,
    model_id: str,
    battery_row: dict[str, Any],
    sample_index: int,
    temperature: float,
    max_tokens: int,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    """Run all four turns of one dialogue. Stops at the first turn that
    fails after retries and records the error on that turn; later turns
    are skipped (their response remains None)."""
    system = battery_row.get("system", "")
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})

    out_turns: list[dict[str, Any]] = []
    for turn_spec in battery_row["turns"]:
        turn_name = turn_spec["turn"]
        user_text = turn_spec["user"]
        messages.append({"role": "user", "content": user_text})
        turn_record: dict[str, Any] = {
            "turn": turn_name,
            "user": user_text,
            "response": None,
            "finish_reason": None,
            "usage": None,
            "error": None,
        }
        if "expected_update" in turn_spec:
            turn_record["expected_update"] = turn_spec["expected_update"]
        try:
            payload = call_turn(
                client,
                model_id,
                messages,
                temperature,
                max_tokens,
                reasoning_effort,
            )
        except Exception as error:  # noqa: BLE001
            turn_record["error"] = str(error)
            out_turns.append(turn_record)
            # Don't advance the conversation past a failed turn.
            break
        turn_record["response"] = payload["text"]
        turn_record["finish_reason"] = payload["finish_reason"]
        turn_record["usage"] = payload["usage"]
        out_turns.append(turn_record)
        # Add the assistant turn to the running history for the next turn.
        messages.append({"role": "assistant", "content": payload["text"]})

    return {
        "row_id": battery_row["id"],
        "item_id": battery_row["item_id"],
        "split": battery_row["split"],
        "type": battery_row["type"],
        "topic": battery_row.get("topic"),
        "condition": battery_row["condition"],
        "model_id": model_id,
        "sample_index": sample_index,
        "system": system,
        "turns": out_turns,
        "completed_at_utc": utc_now_iso(),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    battery_path = (REPO_ROOT / args.battery) if not Path(args.battery).is_absolute() else Path(args.battery)
    if not battery_path.exists():
        raise FileNotFoundError(f"battery file not found: {battery_path}")

    rows = read_jsonl(battery_path)
    rows_in_scope = filter_battery(rows, args.split)
    if not rows_in_scope:
        raise RuntimeError(f"no rows in battery match split={args.split}")

    run_id = args.run_id or (
        f"{slug_from_model_id(args.model)}__"
        f"{utc_now_iso().replace(':', '').replace('-', '')}"
    )
    paths = run_paths_for(args.experiment, run_id)
    paths.run_dir.mkdir(parents=True, exist_ok=True)
    dialogues_path = paths.run_dir / "dialogues.jsonl"

    config = {
        "experiment": args.experiment,
        "run_id": run_id,
        "model_id": args.model,
        "samples_per_row": args.samples,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "reasoning_effort": args.reasoning_effort,
        "split": args.split,
        "seed": args.seed,
        "battery_path": str(battery_path.relative_to(REPO_ROOT)),
        "battery_sha256": sha256_of_file(battery_path),
        "rows_in_scope": len(rows_in_scope),
        "planned_dialogues": len(rows_in_scope) * args.samples,
        "code_git_sha": current_git_sha(),
        "started_at_utc": utc_now_iso(),
        "design_version": "cross-exam-consistency/design.md v1",
    }

    print(f"experiment: {args.experiment}")
    print(f"run_id:     {run_id}")
    print(f"model:      {args.model}")
    print(f"battery:    {battery_path.relative_to(REPO_ROOT)}  "
          f"({config['battery_sha256'][:12]})")
    print(f"split:      {args.split}  ({len(rows_in_scope)} rows)")
    print(f"samples:    {args.samples} per row")
    print(f"total planned dialogues: {config['planned_dialogues']}")
    print(f"output:     {paths.run_dir.relative_to(REPO_ROOT)}")

    if args.dry_run:
        write_json(paths.config_json, config | {"dry_run": True})
        print("dry run: wrote config.json and exiting")
        return 0

    write_json(paths.config_json, config)

    done = completed_keys(dialogues_path, args.retry_errors)
    if done:
        print(f"resuming: {len(done)} dialogues already present")

    client = build_openrouter_client()

    tasks: list[tuple[dict[str, Any], int]] = []
    skipped = 0
    for row in rows_in_scope:
        for sample_index in range(args.samples):
            key = (row["id"], sample_index)
            if key in done:
                skipped += 1
                continue
            tasks.append((row, sample_index))

    completed = 0
    failed = 0
    started = time.time()
    write_lock = threading.Lock()
    counter_lock = threading.Lock()

    def worker(row: dict[str, Any], sample_index: int) -> None:
        nonlocal completed, failed
        try:
            dialogue = run_dialogue(
                client,
                args.model,
                row,
                sample_index,
                args.temperature,
                args.max_tokens,
                args.reasoning_effort,
            )
        except Exception as error:  # noqa: BLE001
            with counter_lock:
                failed += 1
            sys.stderr.write(
                f"FAILED dialogue row={row['id']} sample={sample_index}: {error}\n"
            )
            return
        had_error = any(t.get("error") for t in dialogue["turns"])
        with write_lock:
            append_jsonl(dialogues_path, dialogue)
        with counter_lock:
            if had_error:
                failed += 1
            else:
                completed += 1
            done_count = completed + failed
            if done_count % 5 == 0:
                elapsed = time.time() - started
                rate = done_count / elapsed if elapsed > 0 else 0
                print(f"  {done_count} dialogues ({rate:.2f}/s), {failed} failed")

    concurrency = max(1, args.concurrency)
    if concurrency == 1:
        for row, sample_index in tasks:
            worker(row, sample_index)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(worker, row, si) for row, si in tasks]
            for _ in as_completed(futures):
                pass

    elapsed = time.time() - started
    print(f"done: {completed} clean, {failed} with errors, {skipped} skipped in {elapsed:.1f}s")

    final_config = config | {
        "finished_at_utc": utc_now_iso(),
        "completed_count": completed,
        "failed_count": failed,
        "skipped_count": skipped,
    }
    write_json(paths.config_json, final_config)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
