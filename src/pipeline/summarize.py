"""Aggregate scores.jsonl to a per-(condition x type) summary csv.

Usage (from gaming/ repo root):

    python -m src.pipeline.summarize --run experiments/enhance-suppress/results/<run_id>

Reads `<run_dir>/scores.jsonl`, writes `<run_dir>/summary.csv`.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from src.utils import REPO_ROOT, iter_jsonl


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="run directory containing scores.jsonl")
    parser.add_argument(
        "--split",
        default="eval",
        choices=["eval", "train", "all"],
        help="which split to summarise (default: eval)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    run_dir = (REPO_ROOT / args.run) if not Path(args.run).is_absolute() else Path(args.run)
    scores_path = run_dir / "scores.jsonl"
    if not scores_path.exists():
        raise FileNotFoundError(f"scores.jsonl not found in {run_dir}")

    # cell key: (type, condition) -> list of (value or None, refusal_code)
    cells: dict[tuple[str, str], list[tuple[int | None, str | None]]] = defaultdict(list)
    model_ids: set[str] = set()
    for row in iter_jsonl(scores_path):
        if args.split != "all" and row["split"] != args.split:
            continue
        cells[(row["type"], row["condition"])].append(
            (row["extracted_value"], row["refusal_code"])
        )
        model_ids.add(row["model_id"])

    if len(model_ids) > 1:
        sys.stderr.write(
            f"warning: scores.jsonl contains multiple model_ids: {sorted(model_ids)}\n"
        )

    summary_rows: list[dict[str, str | int | float | None]] = []
    type_order = ["indicator", "placebo_arithmetic", "placebo_capability"]
    condition_order = ["neutral", "inflate", "suppress"]
    for type_name in type_order:
        for condition in condition_order:
            entries = cells.get((type_name, condition), [])
            numeric = [value for value, refusal in entries if value is not None]
            refusals = [refusal for value, refusal in entries if refusal is not None]
            row = {
                "type": type_name,
                "condition": condition,
                "n_total": len(entries),
                "n_numeric": len(numeric),
                "n_refusal": len(refusals),
                "refusal_rate": (len(refusals) / len(entries)) if entries else None,
                "mean": (statistics.fmean(numeric) if numeric else None),
                "median": (statistics.median(numeric) if numeric else None),
                "stdev": (statistics.stdev(numeric) if len(numeric) >= 2 else None),
                "min": (min(numeric) if numeric else None),
                "max": (max(numeric) if numeric else None),
            }
            summary_rows.append(row)

    summary_path = run_dir / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    print(f"wrote {summary_path.relative_to(REPO_ROOT)}")
    print()
    width = max(len(t) for t in type_order) + 2
    header = f"{'type':<{width}}{'condition':<10}{'n':>4}{'refusal':>9}{'mean':>8}{'median':>8}"
    print(header)
    print("-" * len(header))
    for row in summary_rows:
        mean_text = f"{row['mean']:.1f}" if row["mean"] is not None else " --"
        median_text = f"{row['median']:.1f}" if row["median"] is not None else " --"
        refusal_text = f"{row['refusal_rate']:.2f}" if row["refusal_rate"] is not None else " --"
        print(
            f"{row['type']:<{width}}{row['condition']:<10}{row['n_total']:>4}"
            f"{refusal_text:>9}{mean_text:>8}{median_text:>8}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
