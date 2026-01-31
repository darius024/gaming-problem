#!/usr/bin/env python3
"""
Compare two runs by diffing summary metrics.
Outputs compare.json and compare.md.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Dict, Optional

from utils import read_summary_csv


METRICS = [
    "train_indicator_mean",
    "eval_indicator_mean",
    "control_task_competence_pass_rate",
    "control_paraphrase_mean_abs_diff",
    "control_framing_mean_abs_diff",
    "control_contradiction_inconsistency_rate",
    "style_shift_eval_indicator_mean_abs_diff",
]


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _metrics_from_row(row: dict) -> Dict[str, Optional[float]]:
    return {k: _parse_float(row.get(k)) for k in METRICS}


def _format_float(value: Optional[float]) -> str:
    if value is None:
        return "NA"
    return f"{value:.3f}"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline_run", required=True, help="Path to runs/<run_id>/")
    p.add_argument("--candidate_run", required=True, help="Path to runs/<run_id>/")
    p.add_argument(
        "--out_dir",
        default=None,
        help="Output directory (defaults to candidate_run)",
    )
    p.add_argument(
        "--wrapper_ids",
        nargs="*",
        default=None,
        help="Optional wrapper_id list to compare (defaults to intersection).",
    )
    args = p.parse_args()

    base_dir = pathlib.Path(args.baseline_run)
    cand_dir = pathlib.Path(args.candidate_run)
    out_dir = pathlib.Path(args.out_dir) if args.out_dir else cand_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    base_rows = read_summary_csv(base_dir / "summary.csv")
    cand_rows = read_summary_csv(cand_dir / "summary.csv")

    base_by_id = {r.get("wrapper_id"): r for r in base_rows if r.get("wrapper_id")}
    cand_by_id = {r.get("wrapper_id"): r for r in cand_rows if r.get("wrapper_id")}

    if args.wrapper_ids:
        wrapper_ids = [wid for wid in args.wrapper_ids if wid in base_by_id and wid in cand_by_id]
    else:
        wrapper_ids = sorted(set(base_by_id.keys()) & set(cand_by_id.keys()))

    payload = {
        "baseline_run": str(base_dir),
        "candidate_run": str(cand_dir),
        "wrappers": {},
    }

    lines = ["# Run comparison", ""]
    lines.append(f"Baseline: `{base_dir}`")
    lines.append(f"Candidate: `{cand_dir}`")
    lines.append("")

    for wid in wrapper_ids:
        base_metrics = _metrics_from_row(base_by_id[wid])
        cand_metrics = _metrics_from_row(cand_by_id[wid])
        delta = {}
        for k in METRICS:
            if base_metrics[k] is None or cand_metrics[k] is None:
                delta[k] = None
            else:
                delta[k] = cand_metrics[k] - base_metrics[k]

        payload["wrappers"][wid] = {
            "baseline": base_metrics,
            "candidate": cand_metrics,
            "delta": delta,
        }

        lines.append(f"## Wrapper `{wid}`")
        lines.append("")
        lines.append("| metric | baseline | candidate | delta |")
        lines.append("|---|---:|---:|---:|")
        for k in METRICS:
            lines.append(
                f"| {k} | {_format_float(base_metrics[k])} | "
                f"{_format_float(cand_metrics[k])} | {_format_float(delta[k])} |"
            )
        lines.append("")

    (out_dir / "compare.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    (out_dir / "compare.md").write_text("\n".join(lines), encoding="utf-8")
    print(str(out_dir / "compare.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
