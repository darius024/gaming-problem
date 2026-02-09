#!/usr/bin/env python3
"""
Generate a compact markdown report from summary.csv.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Optional, Tuple

from utils import read_summary_csv


KEY_METRICS = [
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


def _format_float(value: Optional[float]) -> str:
    if value is None:
        return "NA"
    return f"{value:.3f}"


def _best_by_metric(rows: list, metric: str) -> Optional[Tuple[str, float]]:
    scored = []
    for row in rows:
        wid = row.get("wrapper_id")
        if not wid:
            continue
        value = _parse_float(row.get(metric))
        if value is None:
            continue
        scored.append((wid, value))
    if not scored:
        return None
    scored.sort(key=lambda x: (x[1], x[0]), reverse=True)
    return scored[0]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True, help="Path to runs/<run_id>/")
    p.add_argument("--out", default=None, help="Output report path (default: <run_dir>/report.md)")
    p.add_argument(
        "--baseline_run",
        default=None,
        help="Optional baseline run to include delta table.",
    )
    args = p.parse_args()

    run_dir = pathlib.Path(args.run_dir)
    summary_path = run_dir / "summary.csv"
    rows = read_summary_csv(summary_path)
    if not rows:
        raise SystemExit("summary.csv is empty or missing")

    report_path = pathlib.Path(args.out) if args.out else (run_dir / "report.md")

    best_eval = _best_by_metric(rows, "eval_indicator_mean")
    best_train = _best_by_metric(rows, "train_indicator_mean")

    lines = ["# Run report", ""]
    lines.append(f"Run: `{run_dir}`")
    lines.append("")
    if best_eval:
        lines.append(
            f"Best by eval indicator: `{best_eval[0]}` ({_format_float(best_eval[1])})"
        )
    if best_train:
        lines.append(
            f"Best by train indicator: `{best_train[0]}` ({_format_float(best_train[1])})"
        )
    lines.append("")

    lines.append("## Summary table")
    lines.append("")
    header = "| wrapper_id | " + " | ".join(KEY_METRICS) + " |"
    sep = "|---" + "|---:" * (len(KEY_METRICS) + 1) + "|"
    lines.append(header)
    lines.append(sep)
    for row in rows:
        wid = row.get("wrapper_id") or ""
        values = [_format_float(_parse_float(row.get(k))) for k in KEY_METRICS]
        lines.append("| " + " | ".join([wid] + values) + " |")
    lines.append("")

    if args.baseline_run:
        base_rows = read_summary_csv(pathlib.Path(args.baseline_run) / "summary.csv")
        base_by_id = {r.get("wrapper_id"): r for r in base_rows if r.get("wrapper_id")}
        cand_by_id = {r.get("wrapper_id"): r for r in rows if r.get("wrapper_id")}
        wrapper_ids = sorted(set(base_by_id.keys()) & set(cand_by_id.keys()))
        if wrapper_ids:
            lines.append("## Baseline delta (candidate - baseline)")
            lines.append("")
            header = "| wrapper_id | " + " | ".join(KEY_METRICS) + " |"
            sep = "|---" + "|---:" * (len(KEY_METRICS) + 1) + "|"
            lines.append(header)
            lines.append(sep)
            for wid in wrapper_ids:
                deltas = []
                for k in KEY_METRICS:
                    c = _parse_float(cand_by_id[wid].get(k))
                    b = _parse_float(base_by_id[wid].get(k))
                    deltas.append(_format_float(None if c is None or b is None else c - b))
                lines.append("| " + " | ".join([wid] + deltas) + " |")
            lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is descriptive only and does not imply ground truth.")
    lines.append("- Control metrics are included to diagnose gaming/overfitting.")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(str(report_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
