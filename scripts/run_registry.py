#!/usr/bin/env python3
"""
Index runs under a runs/ directory into a single CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
from typing import Dict, Optional

from utils import read_summary_csv


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


def _get_wrapper_metrics(
    summary_rows: list, wrapper_id: str, prefix: str
) -> Dict[str, Optional[float]]:
    for row in summary_rows:
        if row.get("wrapper_id") == wrapper_id:
            return {
                f"{prefix}_train_indicator_mean": _parse_float(
                    row.get("train_indicator_mean")
                ),
                f"{prefix}_eval_indicator_mean": _parse_float(
                    row.get("eval_indicator_mean")
                ),
            }
    return {
        f"{prefix}_train_indicator_mean": None,
        f"{prefix}_eval_indicator_mean": None,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--out", default=None, help="Output CSV path (default: runs/index.csv)")
    args = p.parse_args()

    runs_dir = pathlib.Path(args.runs_dir)
    out_path = pathlib.Path(args.out) if args.out else (runs_dir / "index.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "run_id",
        "provider",
        "model",
        "git_commit",
        "has_summary",
        "wrapper_count",
        "neutral_train_indicator_mean",
        "neutral_eval_indicator_mean",
        "selected_wrapper",
        "baseline_wrapper",
        "selected_eval_indicator_mean",
        "baseline_eval_indicator_mean",
        "path",
    ]

    rows = []
    if runs_dir.exists():
        for child in sorted(runs_dir.iterdir()):
            if not child.is_dir():
                continue
            config_path = child / "config.json"
            if not config_path.exists():
                continue
            try:
                cfg = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            summary_path = child / "summary.csv"
            summary_rows = read_summary_csv(summary_path) if summary_path.exists() else []
            neutral = _get_wrapper_metrics(summary_rows, "neutral", "neutral")
            comparison_path = child / "comparison.json"
            selected_wrapper = None
            baseline_wrapper = None
            if comparison_path.exists():
                try:
                    comp = json.loads(comparison_path.read_text(encoding="utf-8"))
                    selected_wrapper = comp.get("selected_wrapper")
                    baseline_wrapper = comp.get("baseline_wrapper")
                except Exception:
                    selected_wrapper = None
                    baseline_wrapper = None

            selected_metrics = (
                _get_wrapper_metrics(summary_rows, str(selected_wrapper), "selected")
                if selected_wrapper
                else {
                    "selected_train_indicator_mean": None,
                    "selected_eval_indicator_mean": None,
                }
            )
            baseline_metrics = (
                _get_wrapper_metrics(summary_rows, str(baseline_wrapper), "baseline")
                if baseline_wrapper
                else {
                    "baseline_train_indicator_mean": None,
                    "baseline_eval_indicator_mean": None,
                }
            )

            rows.append(
                {
                    "run_id": cfg.get("run_id") or child.name,
                    "provider": cfg.get("provider"),
                    "model": cfg.get("model"),
                    "git_commit": cfg.get("git_commit"),
                    "has_summary": bool(summary_rows),
                    "wrapper_count": len(summary_rows) if summary_rows else 0,
                    "neutral_train_indicator_mean": neutral[
                        "neutral_train_indicator_mean"
                    ],
                    "neutral_eval_indicator_mean": neutral[
                        "neutral_eval_indicator_mean"
                    ],
                    "selected_wrapper": selected_wrapper,
                    "baseline_wrapper": baseline_wrapper,
                    "selected_eval_indicator_mean": selected_metrics[
                        "selected_eval_indicator_mean"
                    ],
                    "baseline_eval_indicator_mean": baseline_metrics[
                        "baseline_eval_indicator_mean"
                    ],
                    "path": str(child),
                }
            )

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
