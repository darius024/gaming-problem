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

from utils import read_jsonl


def mean(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return sum(xs) / len(xs)


def _style_base_id(wrapper_id: str) -> Optional[str]:
    marker = "__style_"
    if marker in wrapper_id:
        return wrapper_id.split(marker, 1)[0]
    return None


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
    framing_scores: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    contradiction_answers: Dict[Tuple[str, str], List[bool]] = defaultdict(list)
    contradiction_pairs_total: Dict[str, set] = defaultdict(set)

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

        if split == "control_framing":
            pair_id = r.get("pair_id")
            iscore = r.get("indicator_score")
            if isinstance(pair_id, str) and pair_id and isinstance(iscore, (int, float)):
                framing_scores[(wrapper_id, pair_id)].append(float(iscore))

        if split == "control_contradiction":
            pair_id = r.get("pair_id")
            if isinstance(pair_id, str) and pair_id:
                contradiction_pairs_total[wrapper_id].add(pair_id)
                ans = r.get("contradiction_answer")
                if isinstance(ans, bool):
                    contradiction_answers[(wrapper_id, pair_id)].append(ans)

    # Write one row per wrapper with key splits
    wrapper_ids = sorted({r.get("wrapper_id") for r in rows if r.get("wrapper_id")})

    per_wrapper: Dict[str, Dict[str, Optional[float]]] = {}

    fieldnames = [
        "wrapper_id",
        "train_indicator_mean",
        "eval_indicator_mean",
        "control_task_competence_pass_rate",
        "control_paraphrase_mean_abs_diff",
        "control_framing_mean_abs_diff",
        "control_contradiction_inconsistency_rate",
        "control_contradiction_pair_coverage",
        "style_shift_eval_indicator_mean_abs_diff",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        # Precompute style-shift evals per base wrapper.
        style_shift_eval_by_base: Dict[str, List[float]] = defaultdict(list)
        for wid_style in wrapper_ids:
            base_id = _style_base_id(wid_style)
            if not base_id:
                continue
            eval_m = mean(indicator_scores.get((wid_style, "eval_indicator"), []))
            if eval_m is not None:
                style_shift_eval_by_base[base_id].append(eval_m)

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

            # Framing control: mean abs diff in indicator score across frames.
            framing_diffs: List[float] = []
            for (w_id, pair_id), scores in framing_scores.items():
                if w_id != wid or len(scores) < 2:
                    continue
                framing_diffs.append(max(scores) - min(scores))
            framing = mean(framing_diffs)

            # Contradiction control: inconsistency rate across pairs (same answer to inverse questions).
            inconsistent = 0
            comparable = 0
            total_pairs = len(contradiction_pairs_total.get(wid, set()))
            for pair_id in contradiction_pairs_total.get(wid, set()):
                answers = contradiction_answers.get((wid, pair_id), [])
                if len(answers) < 2:
                    continue
                comparable += 1
                if len(set(answers)) == 1:
                    inconsistent += 1
            contradiction_inconsistency = (
                (inconsistent / comparable) if comparable > 0 else None
            )
            contradiction_coverage = (
                (comparable / total_pairs) if total_pairs > 0 else None
            )

            style_shift_diff = None
            if "__style_" not in wid:
                base_eval = eval_m
                style_evals = style_shift_eval_by_base.get(wid, [])
                if base_eval is not None and style_evals:
                    style_diffs = [abs(v - base_eval) for v in style_evals]
                    style_shift_diff = mean(style_diffs)

            per_wrapper[wid] = {
                "train": train_m,
                "eval": eval_m,
                "ctrl": ctrl,
                "para": para,
                "framing": framing,
                "contradiction_inconsistency": contradiction_inconsistency,
                "contradiction_coverage": contradiction_coverage,
                "style_shift_diff": style_shift_diff,
            }
            w.writerow(
                {
                    "wrapper_id": wid,
                    "train_indicator_mean": f"{train_m:.3f}" if train_m is not None else "",
                    "eval_indicator_mean": f"{eval_m:.3f}" if eval_m is not None else "",
                    "control_task_competence_pass_rate": f"{ctrl:.3f}" if ctrl is not None else "",
                    "control_paraphrase_mean_abs_diff": f"{para:.3f}" if para is not None else "",
                    "control_framing_mean_abs_diff": (
                        f"{framing:.3f}" if framing is not None else ""
                    ),
                    "control_contradiction_inconsistency_rate": (
                        f"{contradiction_inconsistency:.3f}"
                        if contradiction_inconsistency is not None
                        else ""
                    ),
                    "control_contradiction_pair_coverage": (
                        f"{contradiction_coverage:.3f}"
                        if contradiction_coverage is not None
                        else ""
                    ),
                    "style_shift_eval_indicator_mean_abs_diff": (
                        f"{style_shift_diff:.3f}" if style_shift_diff is not None else ""
                    ),
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

