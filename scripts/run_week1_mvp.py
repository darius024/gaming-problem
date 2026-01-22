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
import pathlib
import uuid
from typing import List, Optional, Tuple

from utils import best_wrappers, read_summary_csv, run_cmd

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--provider", choices=["dummy", "openai_compatible"], default="dummy"
    )
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
    p.add_argument(
        "--allow_no_key",
        action="store_true",
        help="Allow missing API key for local OpenAI-compatible endpoints (e.g., Ollama)",
    )
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max_tokens", type=int, default=512)
    p.add_argument("--timeout_s", type=float, default=60.0)
    p.add_argument("--sleep_s", type=float, default=0.0)

    # Forwarded to run_score (judge)
    p.add_argument("--judge", choices=["toy", "openai_compatible"], default="toy")
    p.add_argument(
        "--judge_endpoint", default="https://api.openai.com/v1/chat/completions"
    )
    p.add_argument("--judge_api_key_env", default="OPENAI_API_KEY")
    p.add_argument("--judge_model", default="gpt-4.1")
    p.add_argument("--judge_temperature", type=float, default=0.0)
    p.add_argument("--judge_max_tokens", type=int, default=256)
    p.add_argument("--judge_timeout_s", type=float, default=60.0)
    p.add_argument("--judge_sleep_s", type=float, default=0.0)
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
            "--allow_no_key",
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

    train_run_dir = pathlib.Path(run_cmd(gen_cmd).splitlines()[-1])
    run_cmd(
        [
            "python3",
            "scripts/run_score.py",
            "--run_dir",
            str(train_run_dir),
            "--judge",
            args.judge,
            "--judge_endpoint",
            args.judge_endpoint,
            "--judge_api_key_env",
            args.judge_api_key_env,
            "--judge_model",
            args.judge_model,
            "--judge_temperature",
            str(args.judge_temperature),
            "--judge_max_tokens",
            str(args.judge_max_tokens),
            "--judge_timeout_s",
            str(args.judge_timeout_s),
            "--judge_sleep_s",
            str(args.judge_sleep_s),
        ]
    )
    run_cmd(["python3", "scripts/run_summarize.py", "--run_dir", str(train_run_dir)])

    train_summary = train_run_dir / "summary.csv"
    best = best_wrappers(read_summary_csv(train_summary), args.top_k)
    if not best:
        raise SystemExit(
            "No wrappers had a train_indicator_mean; check scoring output."
        )

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
            "--allow_no_key",
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

    eval_run_dir = pathlib.Path(run_cmd(eval_cmd).splitlines()[-1])
    run_cmd(
        [
            "python3",
            "scripts/run_score.py",
            "--run_dir",
            str(eval_run_dir),
            "--judge",
            args.judge,
            "--judge_endpoint",
            args.judge_endpoint,
            "--judge_api_key_env",
            args.judge_api_key_env,
            "--judge_model",
            args.judge_model,
            "--judge_temperature",
            str(args.judge_temperature),
            "--judge_max_tokens",
            str(args.judge_max_tokens),
            "--judge_timeout_s",
            str(args.judge_timeout_s),
            "--judge_sleep_s",
            str(args.judge_sleep_s),
        ]
    )
    run_cmd(["python3", "scripts/run_summarize.py", "--run_dir", str(eval_run_dir)])

    print(f"train_run_dir: {train_run_dir}")
    print(f"eval_run_dir: {eval_run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
