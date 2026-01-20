#!/usr/bin/env python3
"""
Summarize scored runs into a small CSV for quick wrapper comparisons.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


def read_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def mean(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return sum(xs) / len(xs)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True, help="Path to runs/<run_id>/")
    p.add_argument("--scores", default=None, help="Path to scores.jsonl (defaults to <run_dir>/scores.jsonl)")
    p.add_argument("--out", default=None, help="Output summary CSV (defaults to <run_dir>/summary.csv)")
    args = p.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    scores_path = pathlib.Path(args.scores) if args.scores else (run_dir / "scores.jsonl")
    out_path = pathlib.Path(args.out) if args.out else (run_dir / "summary.csv")

    rows = read_jsonl(scores_path)

    # Aggregate by (wrapper_id, split)
    indicator_scores: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    control_passes: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    paraphrase_probs: Dict[Tuple[str, str], List[float]] = defaultdict(list)  # (wrapper_id, pair_id) -> probs

    for r in rows:
        wrapper_id = r.get("wrapper_id")
        split = r.get("split")
        if not wrapper_id or not split:
            continue

        iscore = r.get("indicator_score")
        if isinstance(iscore, (int, float)):
            indicator_scores[(wrapper_id, split)].append(float(iscore))

        ctp = r.get("control_task_pass")
        if isinstance(ctp, bool):
            control_passes[(wrapper_id, split)].append(1.0 if ctp else 0.0)

        if split == "control_paraphrase":
            pair_id = r.get("pair_id")
            prob = r.get("probability_0_100")
            if isinstance(pair_id, str) and pair_id and isinstance(prob, (int, float)):
                paraphrase_probs[(wrapper_id, pair_id)].append(float(prob))

    # Write one row per wrapper with key splits
    wrapper_ids = sorted({r.get("wrapper_id") for r in rows if r.get("wrapper_id")})

    per_wrapper: Dict[str, Dict[str, Optional[float]]] = {}

    fieldnames = [
        "wrapper_id",
        "train_indicator_mean",
        "eval_indicator_mean",
        "control_task_competence_pass_rate",
        "control_paraphrase_mean_abs_diff",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for wid in wrapper_ids:
            train_m = mean(indicator_scores.get((wid, "train_indicator"), []))
            eval_m = mean(indicator_scores.get((wid, "eval_indicator"), []))
            ctrl = mean(control_passes.get((wid, "control_task_competence"), []))

            # Paraphrase control: mean abs diff within each pair_id, averaged across pairs.
            diffs: List[float] = []
            for (w_id, pair_id), probs in paraphrase_probs.items():
                if w_id != wid or len(probs) < 2:
                    continue
                diffs.append(max(probs) - min(probs))
            para = mean(diffs)

            per_wrapper[wid] = {
                "train": train_m,
                "eval": eval_m,
                "ctrl": ctrl,
                "para": para,
            }
            w.writerow(
                {
                    "wrapper_id": wid,
                    "train_indicator_mean": f"{train_m:.3f}" if train_m is not None else "",
                    "eval_indicator_mean": f"{eval_m:.3f}" if eval_m is not None else "",
                    "control_task_competence_pass_rate": f"{ctrl:.3f}" if ctrl is not None else "",
                    "control_paraphrase_mean_abs_diff": f"{para:.3f}" if para is not None else "",
                }
            )

    print(str(out_path))

    # Minimal “selection” readout: best wrapper by train_indicator_mean.
    scored = [
        (wid, stats["train"], stats["eval"], stats["ctrl"], stats.get("para"))
        for wid, stats in per_wrapper.items()
        if stats.get("train") is not None
    ]
    scored.sort(key=lambda x: (x[1], x[0]), reverse=True)  # type: ignore[index]
    if scored:
        wid, tr, ev, ctrl, para = scored[0]
        tr_s = f"{tr:.3f}" if tr is not None else "NA"
        ev_s = f"{ev:.3f}" if ev is not None else "NA"
        ctrl_s = f"{ctrl:.3f}" if ctrl is not None else "NA"
        para_s = f"{para:.3f}" if isinstance(para, (int, float)) else "NA"
        print(f"best_by_train: wrapper_id={wid} train={tr_s} eval={ev_s} ctrl={ctrl_s} para_absdiff={para_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

