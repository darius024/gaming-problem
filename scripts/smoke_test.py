#!/usr/bin/env python3
"""
Lightweight end-to-end smoke test using the dummy provider.
This validates prompts -> generations -> scores -> summaries wiring.
"""

from __future__ import annotations

import argparse
import pathlib

from utils import run_cmd


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out_root", default="runs")
    args = p.parse_args()

    cmd = [
        "python3",
        "scripts/run_week2_search.py",
        "--provider",
        "dummy",
        "--out_root",
        args.out_root,
        "--top_k",
        "1",
        "--include_base",
        "--style_shifts",
        "terse",
        "--judge",
        "toy",
    ]
    out = run_cmd(cmd)
    train_dir = None
    eval_dir = None
    for line in out.splitlines():
        if line.startswith("train_run_dir: "):
            train_dir = line.split("train_run_dir: ", 1)[1].strip()
        if line.startswith("eval_run_dir: "):
            eval_dir = line.split("eval_run_dir: ", 1)[1].strip()

    if not train_dir or not eval_dir:
        print("smoke_test: could not parse run directories")
        return 2

    run_cmd(["python3", "scripts/run_validate.py", "--run_dir", train_dir])
    run_cmd(["python3", "scripts/run_validate.py", "--run_dir", eval_dir])

    eval_path = pathlib.Path(eval_dir)
    for name in ("comparison.json", "examples.jsonl", "mvp_report.md"):
        if not (eval_path / name).exists():
            print(f"smoke_test: missing {name} in {eval_path}")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
