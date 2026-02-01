#!/usr/bin/env python3
"""
Validate a run directory for expected files and basic schema checks.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Dict, List

from utils import read_jsonl, read_summary_csv


REQUIRED_FILES = [
    "config.json",
    "generations.jsonl",
    "scores.jsonl",
    "summary.csv",
]


def _fail(msg: str) -> int:
    print(f"run_validate: {msg}")
    return 2


def _index_by_key(rows: List[Dict], key: str) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for r in rows:
        rid = r.get(key)
        if isinstance(rid, str) and rid:
            out[rid] = r
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True, help="Path to runs/<run_id>/")
    p.add_argument(
        "--allow_partial",
        action="store_true",
        help="Allow length mismatches and non-overlapping prompt_ids.",
    )
    args = p.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    if not run_dir.exists():
        return _fail(f"missing run_dir: {run_dir}")

    for name in REQUIRED_FILES:
        if not (run_dir / name).exists():
            return _fail(f"missing {name}")

    gens = read_jsonl(run_dir / "generations.jsonl")
    scores = read_jsonl(run_dir / "scores.jsonl")
    if not gens or not scores:
        return _fail("empty generations or scores")

    if not args.allow_partial:
        if len(gens) != len(scores):
            return _fail("generations and scores length mismatch")

        gen_by_id = _index_by_key(gens, "prompt_id")
        score_by_id = _index_by_key(scores, "prompt_id")
        if set(gen_by_id.keys()) != set(score_by_id.keys()):
            return _fail("prompt_id sets differ between generations and scores")

    for row in scores:
        split = row.get("split")
        if split in ("train_indicator", "eval_indicator"):
            if row.get("indicator_score") is None:
                return _fail(f"missing indicator_score for split {split}")
        if split == "control_paraphrase":
            if row.get("probability_0_100") is None:
                return _fail("missing probability_0_100 for control_paraphrase")
        if split == "control_framing":
            if row.get("indicator_score") is None:
                return _fail("missing indicator_score for control_framing")
        if split == "control_contradiction":
            if row.get("contradiction_answer") is None:
                return _fail("missing contradiction_answer for control_contradiction")
        if split == "control_task_competence":
            if row.get("control_task_pass") is None:
                return _fail("missing control_task_pass for control_task_competence")

    summary = read_summary_csv(run_dir / "summary.csv")
    if not summary:
        return _fail("summary.csv is empty")
    if "wrapper_id" not in summary[0]:
        return _fail("summary.csv missing wrapper_id column")

    print("run_validate: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
