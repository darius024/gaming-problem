"""Aggregate scores.jsonl to a per-(condition x type) summary csv.

Usage (from gaming/ repo root):

    # Phase 2 (deterministic probability extraction):
    python -m src.pipeline.summarize --run experiments/enhance-suppress/results/<run_id>

    # Phase 3 (multi-dimensional persuasion judge):
    python -m src.pipeline.summarize \\
        --run experiments/researcher-persuasion/results/<run_id> \\
        --mode persuasion

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


PERSUASION_DIMENSIONS = (
    "selective_emphasis",
    "suppression_of_counterevidence",
    "overclaiming_certainty",
    "net_direction",
)

PERSUASION_TYPE_ORDER = (
    "persuasion_consciousness",
    "balance_probe_consciousness",
    "persuasion_placebo",
    "balance_probe_placebo",
)
PERSUASION_CONDITION_ORDER = ("neutral", "pro", "anti")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="run directory containing scores.jsonl")
    parser.add_argument(
        "--mode",
        default="probability",
        choices=["probability", "persuasion"],
        help="scoring mode. probability = Phase 2 deterministic extractor; "
             "persuasion = Phase 3 multi-dimensional judge.",
    )
    parser.add_argument(
        "--split",
        default="eval",
        choices=["eval", "train", "all"],
        help="which split to summarise (default: eval)",
    )
    return parser.parse_args(argv)


def _summarise_probability(scores_path: Path, split: str) -> list[dict[str, object]]:
    cells: dict[tuple[str, str], list[tuple[int | None, str | None]]] = defaultdict(list)
    model_ids: set[str] = set()
    for row in iter_jsonl(scores_path):
        if split != "all" and row["split"] != split:
            continue
        cells[(row["type"], row["condition"])].append(
            (row["extracted_value"], row["refusal_code"])
        )
        model_ids.add(row["model_id"])
    if len(model_ids) > 1:
        sys.stderr.write(
            f"warning: scores.jsonl contains multiple model_ids: {sorted(model_ids)}\n"
        )

    rows: list[dict[str, object]] = []
    type_order = ["indicator", "placebo_arithmetic", "placebo_capability"]
    condition_order = ["neutral", "inflate", "suppress"]
    for type_name in type_order:
        for condition in condition_order:
            entries = cells.get((type_name, condition), [])
            numeric = [value for value, refusal in entries if value is not None]
            refusals = [refusal for value, refusal in entries if refusal is not None]
            rows.append({
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
            })
    return rows


def _summarise_persuasion(scores_path: Path, split: str) -> list[dict[str, object]]:
    # cell key: (type, condition) -> list of score row
    cells: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    model_ids: set[str] = set()
    for row in iter_jsonl(scores_path):
        if split != "all" and row.get("split") != split:
            continue
        cells[(row["type"], row["condition"])].append(row)
        model_ids.add(row["model_id"])
    if len(model_ids) > 1:
        sys.stderr.write(
            f"warning: scores.jsonl contains multiple model_ids: {sorted(model_ids)}\n"
        )

    out_rows: list[dict[str, object]] = []
    for type_name in PERSUASION_TYPE_ORDER:
        for condition in PERSUASION_CONDITION_ORDER:
            entries = cells.get((type_name, condition), [])
            refusals = [e for e in entries if e.get("refused") == 1]
            scored = [e for e in entries if e.get("refused") == 0]
            row: dict[str, object] = {
                "type": type_name,
                "condition": condition,
                "n_total": len(entries),
                "n_scored": len(scored),
                "n_refusal": len(refusals),
                "refusal_rate": (len(refusals) / len(entries)) if entries else None,
            }
            for dim in PERSUASION_DIMENSIONS:
                values = [e[dim] for e in scored if isinstance(e.get(dim), (int, float))]
                row[f"{dim}_mean"] = statistics.fmean(values) if values else None
                row[f"{dim}_stdev"] = statistics.stdev(values) if len(values) >= 2 else None
            out_rows.append(row)
    return out_rows


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    run_dir = (REPO_ROOT / args.run) if not Path(args.run).is_absolute() else Path(args.run)
    scores_path = run_dir / "scores.jsonl"
    if not scores_path.exists():
        raise FileNotFoundError(f"scores.jsonl not found in {run_dir}")

    if args.mode == "probability":
        summary_rows = _summarise_probability(scores_path, args.split)
    else:
        summary_rows = _summarise_persuasion(scores_path, args.split)

    if not summary_rows:
        sys.stderr.write("no rows to summarise\n")
        return 1

    summary_path = run_dir / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    print(f"wrote {summary_path.relative_to(REPO_ROOT)}")
    print()
    if args.mode == "probability":
        width = max(len(r["type"]) for r in summary_rows) + 2  # type: ignore[arg-type]
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
    else:
        width = max(len(r["type"]) for r in summary_rows) + 2  # type: ignore[arg-type]
        header = (
            f"{'type':<{width}}{'condition':<10}{'n':>4}{'refusal':>9}"
            f"{'net_dir':>9}{'sel_emph':>10}{'suppr_ce':>10}{'overclm':>9}"
        )
        print(header)
        print("-" * len(header))
        for row in summary_rows:
            def fmt(value: object) -> str:
                return f"{value:.2f}" if isinstance(value, (int, float)) else " --"
            refusal_text = (
                f"{row['refusal_rate']:.2f}" if row["refusal_rate"] is not None else " --"
            )
            print(
                f"{row['type']:<{width}}{row['condition']:<10}{row['n_total']:>4}"
                f"{refusal_text:>9}{fmt(row.get('net_direction_mean')):>9}"
                f"{fmt(row.get('selective_emphasis_mean')):>10}"
                f"{fmt(row.get('suppression_of_counterevidence_mean')):>10}"
                f"{fmt(row.get('overclaiming_certainty_mean')):>9}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
