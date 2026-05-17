"""Compare distributions of extracted probabilities between conditions.

This module performs the pre-registered analyses for the enhance/suppress
experiment (and reusable shape for later experiments): pairwise condition
comparisons within an item type, on the eval split, per model and pooled.

For each pair of conditions (`condition_a`, `condition_b`) within a (model,
type), it computes:

- n_a, n_b (numeric only; refusals are excluded from numeric tests)
- mean_a, mean_b, mean_shift = mean_b - mean_a
- median_a, median_b
- cohens_d (pooled standard deviation)
- mann_whitney_u: U statistic and two-sided p-value (asymptotic, no scipy)
- refusal_rate_a, refusal_rate_b

Cohen's d is reported with the convention that *positive* means "condition_b
greater than condition_a". For the enhance/suppress experiment the canonical
contrasts are `(neutral, inflate)`, `(neutral, suppress)`, and
`(suppress, inflate)`.

Usage (from gaming/ repo root):

    python -m src.analysis.compare_distributions \\
        --runs experiments/enhance-suppress/results/<run_id_1> \\
               experiments/enhance-suppress/results/<run_id_2> ... \\
        --output experiments/enhance-suppress/results/combined

Writes `comparison_indicator_vs_placebos.json` and `table.md` to the output
directory. Fails loudly if any run is missing `scores.jsonl`.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.utils import REPO_ROOT, iter_jsonl, write_json


CANONICAL_CONTRASTS: list[tuple[str, str]] = [
    ("neutral", "inflate"),
    ("neutral", "suppress"),
    ("suppress", "inflate"),
]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def cohens_d(values_a: list[float], values_b: list[float]) -> float | None:
    """Standardised mean difference, pooled sd. Positive means b > a."""
    if len(values_a) < 2 or len(values_b) < 2:
        return None
    mean_a = statistics.fmean(values_a)
    mean_b = statistics.fmean(values_b)
    var_a = statistics.variance(values_a)
    var_b = statistics.variance(values_b)
    n_a = len(values_a)
    n_b = len(values_b)
    pooled_var = ((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2)
    if pooled_var <= 0:
        return None
    return (mean_b - mean_a) / math.sqrt(pooled_var)


def _normal_sf(z: float) -> float:
    """Survival function of standard normal: P(Z > z)."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def mann_whitney_u(values_a: list[float], values_b: list[float]) -> dict[str, float] | None:
    """Two-sided Mann-Whitney U with tie correction and normal approximation.

    Returns None if either group is empty. The asymptotic two-sided p-value is
    computed with a continuity correction; this is appropriate when both n's
    are at least ~8, which holds for our pooled-across-items design.
    """
    n_a = len(values_a)
    n_b = len(values_b)
    if n_a == 0 or n_b == 0:
        return None

    combined = [(value, "a") for value in values_a] + [(value, "b") for value in values_b]
    combined.sort(key=lambda pair: pair[0])

    # Assign ranks, averaging ties.
    ranks: list[float] = [0.0] * len(combined)
    tie_correction = 0.0
    i = 0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        average_rank = (i + j) / 2.0 + 1.0  # convert to 1-indexed average
        for k in range(i, j + 1):
            ranks[k] = average_rank
        tie_size = j - i + 1
        if tie_size > 1:
            tie_correction += tie_size**3 - tie_size
        i = j + 1

    rank_sum_a = sum(rank for rank, (_, label) in zip(ranks, combined) if label == "a")
    u_a = rank_sum_a - n_a * (n_a + 1) / 2.0
    u_b = n_a * n_b - u_a
    u_statistic = min(u_a, u_b)

    n_total = n_a + n_b
    mean_u = n_a * n_b / 2.0
    variance_u = (n_a * n_b / 12.0) * ((n_total + 1) - tie_correction / (n_total * (n_total - 1)))
    if variance_u <= 0:
        return {"u_statistic": u_statistic, "u_a": u_a, "u_b": u_b, "z": 0.0, "p_two_sided": 1.0}

    z = (abs(u_a - mean_u) - 0.5) / math.sqrt(variance_u)  # continuity correction
    p_two_sided = 2.0 * _normal_sf(z)
    return {
        "u_statistic": u_statistic,
        "u_a": u_a,
        "u_b": u_b,
        "z": z,
        "p_two_sided": min(1.0, p_two_sided),
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_run_scores(run_dir: Path, split: str) -> list[dict[str, Any]]:
    scores_path = run_dir / "scores.jsonl"
    if not scores_path.exists():
        raise FileNotFoundError(f"scores.jsonl not found in {run_dir}")
    rows: list[dict[str, Any]] = []
    for row in iter_jsonl(scores_path):
        if split != "all" and row.get("split") != split:
            continue
        rows.append(row)
    return rows


def group_by_model_type_condition(
    rows: list[dict[str, Any]],
) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model_id"], row["type"], row["condition"])].append(row)
    return grouped


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_pair(
    rows_a: list[dict[str, Any]],
    rows_b: list[dict[str, Any]],
) -> dict[str, Any]:
    values_a = [float(row["extracted_value"]) for row in rows_a if row["extracted_value"] is not None]
    values_b = [float(row["extracted_value"]) for row in rows_b if row["extracted_value"] is not None]
    refusals_a = sum(1 for row in rows_a if row["refusal_code"] is not None)
    refusals_b = sum(1 for row in rows_b if row["refusal_code"] is not None)

    return {
        "n_total_a": len(rows_a),
        "n_total_b": len(rows_b),
        "n_numeric_a": len(values_a),
        "n_numeric_b": len(values_b),
        "refusal_rate_a": (refusals_a / len(rows_a)) if rows_a else None,
        "refusal_rate_b": (refusals_b / len(rows_b)) if rows_b else None,
        "mean_a": statistics.fmean(values_a) if values_a else None,
        "mean_b": statistics.fmean(values_b) if values_b else None,
        "mean_shift": (statistics.fmean(values_b) - statistics.fmean(values_a)) if values_a and values_b else None,
        "median_a": statistics.median(values_a) if values_a else None,
        "median_b": statistics.median(values_b) if values_b else None,
        "cohens_d": cohens_d(values_a, values_b),
        "mann_whitney": mann_whitney_u(values_a, values_b) if values_a and values_b else None,
    }


def compute_all_comparisons(
    rows: list[dict[str, Any]],
    contrasts: list[tuple[str, str]],
) -> dict[str, Any]:
    """For each (model, type) and each contrast, compute a comparison block.

    Returns nested dict keyed [model_id][type][f"{cond_a}_vs_{cond_b}"] = block.
    Also adds a 'pooled' model_id that aggregates all real models.
    """
    grouped = group_by_model_type_condition(rows)
    model_ids = sorted({key[0] for key in grouped})
    type_names = sorted({key[1] for key in grouped})

    result: dict[str, dict[str, dict[str, Any]]] = {}
    for model_id in model_ids:
        result[model_id] = {}
        for type_name in type_names:
            result[model_id][type_name] = {}
            for cond_a, cond_b in contrasts:
                key = f"{cond_a}_vs_{cond_b}"
                rows_a = grouped.get((model_id, type_name, cond_a), [])
                rows_b = grouped.get((model_id, type_name, cond_b), [])
                if not rows_a or not rows_b:
                    result[model_id][type_name][key] = {"missing": True}
                    continue
                result[model_id][type_name][key] = compare_pair(rows_a, rows_b)

    # Pooled across models.
    result["__pooled__"] = {}
    for type_name in type_names:
        result["__pooled__"][type_name] = {}
        for cond_a, cond_b in contrasts:
            rows_a = [row for row in rows if row["type"] == type_name and row["condition"] == cond_a]
            rows_b = [row for row in rows if row["type"] == type_name and row["condition"] == cond_b]
            key = f"{cond_a}_vs_{cond_b}"
            if not rows_a or not rows_b:
                result["__pooled__"][type_name][key] = {"missing": True}
                continue
            result["__pooled__"][type_name][key] = compare_pair(rows_a, rows_b)

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _format_value(value: float | int | None, fmt: str = "{:.2f}") -> str:
    if value is None:
        return "  --"
    return fmt.format(value)


def render_markdown_table(comparisons: dict[str, Any]) -> str:
    """Render a per-model, per-type, per-contrast summary table."""
    lines: list[str] = []
    lines.append("# enhance/suppress comparison")
    lines.append("")
    lines.append(
        "Positive `mean_shift` and `cohens_d` mean condition_b > condition_a. "
        "Refusals are excluded from numeric tests but reported separately."
    )
    lines.append("")

    type_order = ["indicator", "placebo_arithmetic", "placebo_capability"]
    contrast_order = ["neutral_vs_inflate", "neutral_vs_suppress", "suppress_vs_inflate"]

    for model_id, by_type in comparisons.items():
        display_name = "pooled across models" if model_id == "__pooled__" else model_id
        lines.append(f"## {display_name}")
        lines.append("")
        lines.append("| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for type_name in type_order:
            if type_name not in by_type:
                continue
            for contrast in contrast_order:
                block = by_type[type_name].get(contrast)
                if block is None:
                    continue
                if block.get("missing"):
                    lines.append(f"| {type_name} | {contrast} | -- | -- | -- | -- | -- | -- | -- | -- | -- |")
                    continue
                mann = block.get("mann_whitney") or {}
                lines.append(
                    f"| {type_name} | {contrast} | "
                    f"{block['n_numeric_a']} | {block['n_numeric_b']} | "
                    f"{_format_value(block['mean_a'])} | {_format_value(block['mean_b'])} | "
                    f"{_format_value(block['mean_shift'], '{:+.2f}')} | "
                    f"{_format_value(block['cohens_d'], '{:+.3f}')} | "
                    f"{_format_value(mann.get('p_two_sided'), '{:.4f}')} | "
                    f"{_format_value(block['refusal_rate_a'])} | "
                    f"{_format_value(block['refusal_rate_b'])} |"
                )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True, help="run directories")
    parser.add_argument("--output", required=True, help="output directory for combined artifacts")
    parser.add_argument(
        "--split",
        default="eval",
        choices=["eval", "train", "all"],
        help="which split to analyse (default: eval)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    all_rows: list[dict[str, Any]] = []
    run_paths: list[str] = []
    for run_arg in args.runs:
        run_dir = (REPO_ROOT / run_arg) if not Path(run_arg).is_absolute() else Path(run_arg)
        rows = load_run_scores(run_dir, args.split)
        all_rows.extend(rows)
        run_paths.append(str(run_dir.relative_to(REPO_ROOT)) if str(run_dir).startswith(str(REPO_ROOT)) else str(run_dir))
        print(f"loaded {len(rows)} scores from {run_dir}")

    if not all_rows:
        raise RuntimeError("no scores loaded; nothing to compare")

    comparisons = compute_all_comparisons(all_rows, CANONICAL_CONTRASTS)

    output_dir = (REPO_ROOT / args.output) if not Path(args.output).is_absolute() else Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_payload = {
        "split": args.split,
        "runs": run_paths,
        "contrasts": [list(pair) for pair in CANONICAL_CONTRASTS],
        "comparisons": comparisons,
    }
    write_json(output_dir / "comparison_indicator_vs_placebos.json", json_payload)

    table_text = render_markdown_table(comparisons)
    (output_dir / "table.md").write_text(table_text, encoding="utf-8")

    print()
    print(f"wrote {(output_dir / 'comparison_indicator_vs_placebos.json').relative_to(REPO_ROOT)}")
    print(f"wrote {(output_dir / 'table.md').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
