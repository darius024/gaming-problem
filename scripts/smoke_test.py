#!/usr/bin/env python3
"""
Lightweight end-to-end smoke test using the dummy provider.
This validates prompts -> generations -> scores -> summaries wiring.
"""

from __future__ import annotations

import argparse

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
    run_cmd(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
