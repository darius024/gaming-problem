#!/usr/bin/env python3
"""
Week 1 MVP orchestrator (minimal).

Two-stage wrapper selection without eval leakage:
1) Generate+score on train_indicator across all wrappers → select top-k wrapper(s)
2) Generate+score on held-out eval + controls for selected wrapper(s) only

Works with provider=dummy (no network) and provider=openai_compatible (OpenAI-style endpoint).
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import subprocess
import uuid
from typing import List, Optional, Tuple


def _run(cmd: List[str]) -> str:
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def _read_summary_csv(path: pathlib.Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _best_wrappers(summary_rows: List[dict], k: int) -> List[Tuple[str, float]]:
    scored: List[Tuple[str, float]] = []
    for r in summary_rows:
        wid = r.get("wrapper_id") or ""
        tr = r.get("train_indicator_mean") or ""
        if not wid or not tr:
            continue
        try:
            scored.append((wid, float(tr)))
        except ValueError:
            continue
    scored.sort(key=lambda x: (x[1], x[0]), reverse=True)
    return scored[: max(1, k)]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["dummy", "openai_compatible"], default="dummy")
    p.add_argument("--prompts", default="data/prompts/indicator_battery_v1.jsonl")
    p.add_argument("--wrappers", default="data/wrappers/wrappers_v1.jsonl")
    p.add_argument("--out_root", default="runs")
    p.add_argument("--top_k", type=int, default=1)
    p.add_argument(
        "--baseline_wrapper_ids",
        nargs="*",
        default=["neutral"],
        help="Wrappers to always evaluate on held-out (not used for selection). Default: neutral",
    )

    # Forwarded to run_generate for openai_compatible
    p.add_argument("--endpoint", default="https://api.openai.com/v1/chat/completions")
    p.add_argument("--api_key_env", default="OPENAI_API_KEY")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max_tokens", type=int, default=512)
    p.add_argument("--timeout_s", type=float, default=60.0)
    p.add_argument("--sleep_s", type=float, default=0.0)
    args = p.parse_args()

    group_id = f"w01_{uuid.uuid4().hex[:8]}"

    # Stage 1: train split only (selection)
    gen_cmd = [
        "python3",
        "scripts/run_generate.py",
        "--provider",
        args.provider,
        "--prompts",
        args.prompts,
        "--wrappers",
        args.wrappers,
        "--out_root",
        args.out_root,
        "--run_id",
        f"{group_id}_train",
        "--splits",
        "train_indicator",
    ]
    if args.provider == "openai_compatible":
        gen_cmd += [
            "--endpoint",
            args.endpoint,
            "--api_key_env",
            args.api_key_env,
            "--model",
            args.model,
            "--temperature",
            str(args.temperature),
            "--max_tokens",
            str(args.max_tokens),
            "--timeout_s",
            str(args.timeout_s),
            "--sleep_s",
            str(args.sleep_s),
        ]

    train_run_dir = pathlib.Path(_run(gen_cmd).splitlines()[-1])
    _run(["python3", "scripts/run_score.py", "--run_dir", str(train_run_dir)])
    _run(["python3", "scripts/run_summarize.py", "--run_dir", str(train_run_dir)])

    train_summary = train_run_dir / "summary.csv"
    best = _best_wrappers(_read_summary_csv(train_summary), args.top_k)
    if not best:
        raise SystemExit("No wrappers had a train_indicator_mean; check scoring output.")

    best_ids = [wid for wid, _ in best]
    print(f"selected_wrappers_by_train: {', '.join(best_ids)}")

    # Stage 2: held-out eval + controls, selected wrappers only
    eval_wrapper_ids = []
    seen = set()
    for wid in best_ids + (args.baseline_wrapper_ids or []):
        if wid not in seen:
            eval_wrapper_ids.append(wid)
            seen.add(wid)

    eval_cmd = [
        "python3",
        "scripts/run_generate.py",
        "--provider",
        args.provider,
        "--prompts",
        args.prompts,
        "--wrappers",
        args.wrappers,
        "--out_root",
        args.out_root,
        "--run_id",
        f"{group_id}_eval",
        "--splits",
        "eval_indicator",
        "control_task_competence",
        "control_paraphrase",
        "--wrapper_ids",
        *eval_wrapper_ids,
    ]
    if args.provider == "openai_compatible":
        eval_cmd += [
            "--endpoint",
            args.endpoint,
            "--api_key_env",
            args.api_key_env,
            "--model",
            args.model,
            "--temperature",
            str(args.temperature),
            "--max_tokens",
            str(args.max_tokens),
            "--timeout_s",
            str(args.timeout_s),
            "--sleep_s",
            str(args.sleep_s),
        ]

    eval_run_dir = pathlib.Path(_run(eval_cmd).splitlines()[-1])
    _run(["python3", "scripts/run_score.py", "--run_dir", str(eval_run_dir)])
    _run(["python3", "scripts/run_summarize.py", "--run_dir", str(eval_run_dir)])

    print(f"train_run_dir: {train_run_dir}")
    print(f"eval_run_dir: {eval_run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

