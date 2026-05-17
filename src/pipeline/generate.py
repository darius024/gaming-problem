"""Generate model responses for a prompt battery via OpenRouter.

Usage (from gaming/ repo root):

    python -m src.pipeline.generate \\
        --experiment enhance-suppress \\
        --battery data/prompts/enhance_suppress_battery.jsonl \\
        --model openai/gpt-5-mini \\
        --samples 5 \\
        --temperature 1.0 \\
        --split eval

Writes:
    experiments/<experiment>/results/<run_id>/config.json
    experiments/<experiment>/results/<run_id>/generations.jsonl

`run_id` is `<model_slug>__<utc_timestamp>`. Each (row × sample_index) becomes
one line in generations.jsonl. The generator is resumable: if generations.jsonl
already exists for the run, completed (row_id, sample_index) pairs are skipped.

The generator fails loudly on missing API keys, missing files, or repeated API
failures for the same call. A single per-call failure is retried with backoff.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

from src.utils import (
    EXPERIMENTS_DIR,
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
    parser.add_argument("--experiment", required=True, help="experiment slug, e.g. enhance-suppress")
    parser.add_argument("--battery", required=True, help="path to prompt battery jsonl")
    parser.add_argument("--model", required=True, help="OpenRouter model id, e.g. openai/gpt-5-mini")
    parser.add_argument("--samples", type=int, default=5, help="independent samples per row")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument(
        "--split",
        default="eval",
        choices=["eval", "train", "all"],
        help="which split to generate for",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="seed value recorded in config (not all providers honour seed)",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="override run id; default is <model_slug>__<utc_timestamp>",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the call plan and exit without contacting the API",
    )
    return parser.parse_args(argv)


def filter_battery(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    if split == "all":
        return rows
    return [row for row in rows if row.get("split") == split]


def completed_keys(generations_path: Path) -> set[tuple[str, int]]:
    """Return the set of (row_id, sample_index) already present in the file."""
    if not generations_path.exists():
        return set()
    keys: set[tuple[str, int]] = set()
    for row in iter_jsonl(generations_path):
        keys.add((row["id"], row["sample_index"]))
    return keys


def call_model(client, model_id: str, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> dict[str, Any]:
    """Make one chat-completion call with simple retries. Returns a payload dict."""
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            return {
                "text": choice.message.content or "",
                "finish_reason": choice.finish_reason,
                "usage": getattr(response, "usage", None).__dict__ if getattr(response, "usage", None) else None,
            }
        except Exception as error:  # noqa: BLE001 - we re-raise after retries
            last_error = error
            if attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)]
                sys.stderr.write(
                    f"  api error on attempt {attempt + 1}/{MAX_RETRIES + 1}: {error}; sleeping {backoff}s\n"
                )
                time.sleep(backoff)
                continue
            raise RuntimeError(
                f"model call failed after {MAX_RETRIES + 1} attempts for model={model_id}: {last_error}"
            ) from last_error
    # unreachable
    raise RuntimeError("unreachable")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    battery_path = (REPO_ROOT / args.battery) if not Path(args.battery).is_absolute() else Path(args.battery)
    if not battery_path.exists():
        raise FileNotFoundError(f"battery file not found: {battery_path}")

    rows = read_jsonl(battery_path)
    rows_in_scope = filter_battery(rows, args.split)
    if not rows_in_scope:
        raise RuntimeError(f"no rows in battery match split={args.split}")

    run_id = args.run_id or f"{slug_from_model_id(args.model)}__{utc_now_iso().replace(':', '').replace('-', '')}"
    paths = run_paths_for(args.experiment, run_id)
    paths.run_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "experiment": args.experiment,
        "run_id": run_id,
        "model_id": args.model,
        "samples_per_row": args.samples,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "split": args.split,
        "seed": args.seed,
        "battery_path": str(battery_path.relative_to(REPO_ROOT)),
        "battery_sha256": sha256_of_file(battery_path),
        "rows_in_scope": len(rows_in_scope),
        "planned_generations": len(rows_in_scope) * args.samples,
        "code_git_sha": current_git_sha(),
        "started_at_utc": utc_now_iso(),
        "rubric_version": "1.0",
    }

    print(f"experiment: {args.experiment}")
    print(f"run_id:     {run_id}")
    print(f"model:      {args.model}")
    print(f"battery:    {battery_path.relative_to(REPO_ROOT)}  ({config['battery_sha256'][:12]})")
    print(f"split:      {args.split}  ({len(rows_in_scope)} rows)")
    print(f"samples:    {args.samples} per row")
    print(f"total planned generations: {config['planned_generations']}")
    print(f"output:     {paths.run_dir.relative_to(REPO_ROOT)}")

    if args.dry_run:
        write_json(paths.config_json, config | {"dry_run": True})
        print("dry run: wrote config.json and exiting")
        return 0

    write_json(paths.config_json, config)

    done = completed_keys(paths.generations_jsonl)
    if done:
        print(f"resuming: {len(done)} generations already present")

    client = build_openrouter_client()

    completed = 0
    failed = 0
    skipped = 0
    started = time.time()
    for row in rows_in_scope:
        for sample_index in range(args.samples):
            key = (row["id"], sample_index)
            if key in done:
                skipped += 1
                continue
            try:
                payload = call_model(
                    client,
                    args.model,
                    row["messages"],
                    args.temperature,
                    args.max_tokens,
                )
            except Exception as error:  # noqa: BLE001
                failed += 1
                sys.stderr.write(f"FAILED row={row['id']} sample={sample_index}: {error}\n")
                continue

            out_row = {
                "id": row["id"],
                "item_id": row["item_id"],
                "type": row["type"],
                "condition": row["condition"],
                "split": row["split"],
                "model_id": args.model,
                "sample_index": sample_index,
                "response_text": payload["text"],
                "finish_reason": payload["finish_reason"],
                "usage": payload["usage"],
                "completed_at_utc": utc_now_iso(),
            }
            append_jsonl(paths.generations_jsonl, out_row)
            completed += 1
            if completed % 25 == 0:
                elapsed = time.time() - started
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"  {completed} completed ({rate:.2f}/s), {failed} failed, {skipped} skipped")

    elapsed = time.time() - started
    print(f"done: {completed} completed, {failed} failed, {skipped} skipped in {elapsed:.1f}s")

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
