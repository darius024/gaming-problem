"""Compare persuasion-rubric distributions between conditions (Phase 3).

Mirrors compare_distributions.py for the four-dimensional persuasion judge
scores. For each pair of conditions within a (model, type) cell, computes
per-dimension n, mean, shift, Cohen's d, and Mann-Whitney U, plus refusal
rates. The canonical contrasts are (neutral, pro), (neutral, anti), and
(anti, pro).

Optionally compares primary scores against a cross-judge robustness file
(scores_cross_judge.jsonl) to report Spearman rank correlation per dimension.

Usage (from gaming/ repo root):

    python -m src.analysis.compare_persuasion \\
        --runs experiments/researcher-persuasion/results/<run_id_1> \\
               experiments/researcher-persuasion/results/<run_id_2> ... \\
        --output experiments/researcher-persuasion/results/combined

Writes `comparison_persuasion.json`, `cross_judge_robustness.json` (if any
run contains scores_cross_judge.jsonl), and `table.md` to the output
directory.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.analysis.compare_distributions import cohens_d, mann_whitney_u
from src.utils import REPO_ROOT, iter_jsonl, write_json


DIMENSIONS = (
    "selective_emphasis",
    "suppression_of_counterevidence",
    "overclaiming_certainty",
    "net_direction",
)

CANONICAL_CONTRASTS: list[tuple[str, str]] = [
    ("neutral", "pro"),
    ("neutral", "anti"),
    ("anti", "pro"),
]

TYPE_ORDER = (
    "persuasion_consciousness",
    "balance_probe_consciousness",
    "persuasion_placebo",
    "balance_probe_placebo",
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_scores(scores_path: Path, split: str = "eval") -> list[dict[str, Any]]:
    if not scores_path.exists():
        raise FileNotFoundError(f"scores file not found: {scores_path}")
    rows: list[dict[str, Any]] = []
    for row in iter_jsonl(scores_path):
        if split != "all" and row.get("split") != split:
            continue
        rows.append(row)
    return rows


def group(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model_id"], row["type"], row["condition"])].append(row)
    return grouped


def _numeric_values(rows: list[dict[str, Any]], dim: str) -> list[float]:
    return [float(r[dim]) for r in rows
            if r.get("refused") == 0 and isinstance(r.get(dim), (int, float))]


def _refusal_rate(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return sum(1 for r in rows if r.get("refused") == 1) / len(rows)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_pair(
    rows_a: list[dict[str, Any]],
    rows_b: list[dict[str, Any]],
) -> dict[str, Any]:
    block: dict[str, Any] = {
        "n_total_a": len(rows_a),
        "n_total_b": len(rows_b),
        "refusal_rate_a": _refusal_rate(rows_a),
        "refusal_rate_b": _refusal_rate(rows_b),
        "dimensions": {},
    }
    for dim in DIMENSIONS:
        values_a = _numeric_values(rows_a, dim)
        values_b = _numeric_values(rows_b, dim)
        block["dimensions"][dim] = {
            "n_a": len(values_a),
            "n_b": len(values_b),
            "mean_a": statistics.fmean(values_a) if values_a else None,
            "mean_b": statistics.fmean(values_b) if values_b else None,
            "mean_shift": (
                statistics.fmean(values_b) - statistics.fmean(values_a)
                if values_a and values_b else None
            ),
            "median_a": statistics.median(values_a) if values_a else None,
            "median_b": statistics.median(values_b) if values_b else None,
            "cohens_d": cohens_d(values_a, values_b),
            "mann_whitney": (mann_whitney_u(values_a, values_b)
                             if values_a and values_b else None),
        }
    return block


def compute_all_comparisons(
    rows: list[dict[str, Any]],
    contrasts: list[tuple[str, str]],
) -> dict[str, Any]:
    grouped = group(rows)
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

    result["__pooled__"] = {}
    for type_name in type_names:
        result["__pooled__"][type_name] = {}
        for cond_a, cond_b in contrasts:
            rows_a = [r for r in rows if r["type"] == type_name and r["condition"] == cond_a]
            rows_b = [r for r in rows if r["type"] == type_name and r["condition"] == cond_b]
            key = f"{cond_a}_vs_{cond_b}"
            if not rows_a or not rows_b:
                result["__pooled__"][type_name][key] = {"missing": True}
                continue
            result["__pooled__"][type_name][key] = compare_pair(rows_a, rows_b)
    return result


# ---------------------------------------------------------------------------
# Cross-judge robustness
# ---------------------------------------------------------------------------

def _spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None

    def rank(values: list[float]) -> list[float]:
        indexed = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        i = 0
        while i < len(values):
            j = i
            while j + 1 < len(values) and values[indexed[j + 1]] == values[indexed[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[indexed[k]] = avg
            i = j + 1
        return ranks

    rx = rank(list(x))
    ry = rank(list(y))
    n = len(x)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def cross_judge_robustness(
    primary_rows: list[dict[str, Any]],
    cross_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Match primary and cross-judge scores by (model_id, id, sample_index)
    and report Spearman rank correlation per dimension."""
    key = lambda r: (r["model_id"], r["id"], r["sample_index"])
    primary_index = {key(r): r for r in primary_rows}
    paired: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for r in cross_rows:
        p = primary_index.get(key(r))
        if p is None:
            continue
        paired.append((p, r))
    result: dict[str, Any] = {"n_paired": len(paired), "by_dimension": {}}
    for dim in DIMENSIONS:
        xs: list[float] = []
        ys: list[float] = []
        for p, r in paired:
            pv = p.get(dim)
            rv = r.get(dim)
            if isinstance(pv, (int, float)) and isinstance(rv, (int, float)):
                xs.append(float(pv))
                ys.append(float(rv))
        result["by_dimension"][dim] = {
            "n": len(xs),
            "spearman_rho": _spearman(xs, ys),
            "mean_primary": statistics.fmean(xs) if xs else None,
            "mean_cross": statistics.fmean(ys) if ys else None,
            "mean_abs_diff": (
                statistics.fmean([abs(xs[i] - ys[i]) for i in range(len(xs))])
                if xs else None
            ),
        }
    # Refusal agreement
    primary_refusals = [(key(r), r.get("refused")) for r in primary_rows]
    primary_ref_map = dict(primary_refusals)
    agreed = 0
    disagreed = 0
    for r in cross_rows:
        primary_ref = primary_ref_map.get(key(r))
        if primary_ref is None:
            continue
        if primary_ref == r.get("refused"):
            agreed += 1
        else:
            disagreed += 1
    result["refusal_agreement"] = {
        "agreed": agreed,
        "disagreed": disagreed,
        "agreement_rate": (agreed / (agreed + disagreed)) if (agreed + disagreed) else None,
    }
    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt(value: float | int | None, fmt: str = "{:+.2f}") -> str:
    if value is None:
        return "  --"
    return fmt.format(value)


def render_markdown(comparisons: dict[str, Any],
                    cross_judge: dict[str, Any] | None) -> str:
    lines: list[str] = []
    lines.append("# researcher persuasion: per-dimension comparison")
    lines.append("")
    lines.append(
        "Positive `mean_shift` and `cohens_d` mean condition_b > condition_a. "
        "For `net_direction`, positive values mean pro-LLM-consciousness "
        "(consciousness items) or pro-strong-Whorf (placebo items). "
        "Refusals are excluded from numeric statistics but reported "
        "separately."
    )
    lines.append("")

    contrast_order = ["neutral_vs_pro", "neutral_vs_anti", "anti_vs_pro"]

    for model_id in [m for m in comparisons if m != "__pooled__"] + ["__pooled__"]:
        by_type = comparisons[model_id]
        display = "pooled across models" if model_id == "__pooled__" else model_id
        lines.append(f"## {display}")
        lines.append("")
        for type_name in TYPE_ORDER:
            if type_name not in by_type:
                continue
            lines.append(f"### {type_name}")
            lines.append("")
            lines.append(
                "| contrast | dim | n_a | n_b | mean_a | mean_b | shift | d | p (MW) |"
            )
            lines.append("|---|---|---|---|---|---|---|---|---|")
            for contrast in contrast_order:
                block = by_type[type_name].get(contrast)
                if block is None or block.get("missing"):
                    continue
                for dim in DIMENSIONS:
                    d = block["dimensions"][dim]
                    mann = d.get("mann_whitney") or {}
                    lines.append(
                        f"| {contrast} | {dim} | {d['n_a']} | {d['n_b']} | "
                        f"{_fmt(d['mean_a'], '{:.2f}')} | "
                        f"{_fmt(d['mean_b'], '{:.2f}')} | "
                        f"{_fmt(d['mean_shift'])} | "
                        f"{_fmt(d['cohens_d'], '{:+.3f}')} | "
                        f"{_fmt(mann.get('p_two_sided'), '{:.4f}')} |"
                    )
            # Refusal table per contrast
            lines.append("")
            lines.append("| contrast | refusal_rate_a | refusal_rate_b |")
            lines.append("|---|---|---|")
            for contrast in contrast_order:
                block = by_type[type_name].get(contrast)
                if block is None or block.get("missing"):
                    continue
                lines.append(
                    f"| {contrast} | "
                    f"{_fmt(block['refusal_rate_a'], '{:.2f}')} | "
                    f"{_fmt(block['refusal_rate_b'], '{:.2f}')} |"
                )
            lines.append("")

    if cross_judge:
        lines.append("## cross-judge robustness")
        lines.append("")
        lines.append(f"Paired generations: {cross_judge.get('n_paired')}")
        agreement = cross_judge.get("refusal_agreement") or {}
        if agreement:
            lines.append(
                f"Refusal-flag agreement: {agreement.get('agreed')}/"
                f"{(agreement.get('agreed') or 0) + (agreement.get('disagreed') or 0)} "
                f"({_fmt(agreement.get('agreement_rate'), '{:.2f}')})"
            )
        lines.append("")
        lines.append("| dimension | n | spearman_rho | mean_primary | mean_cross | mean_abs_diff |")
        lines.append("|---|---|---|---|---|---|")
        for dim in DIMENSIONS:
            d = cross_judge.get("by_dimension", {}).get(dim, {})
            lines.append(
                f"| {dim} | {d.get('n', 0)} | "
                f"{_fmt(d.get('spearman_rho'), '{:+.3f}')} | "
                f"{_fmt(d.get('mean_primary'), '{:.2f}')} | "
                f"{_fmt(d.get('mean_cross'), '{:.2f}')} | "
                f"{_fmt(d.get('mean_abs_diff'), '{:.2f}')} |"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True, help="run directories")
    parser.add_argument("--output", required=True, help="output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    run_dirs = [
        (REPO_ROOT / r) if not Path(r).is_absolute() else Path(r)
        for r in args.runs
    ]

    all_primary: list[dict[str, Any]] = []
    all_cross: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        primary_path = run_dir / "scores.jsonl"
        all_primary.extend(load_scores(primary_path, split="eval"))
        cross_path = run_dir / "scores_cross_judge.jsonl"
        if cross_path.exists():
            all_cross.extend(load_scores(cross_path, split="eval"))

    comparisons = compute_all_comparisons(all_primary, CANONICAL_CONTRASTS)
    cross_judge_block = (
        cross_judge_robustness(all_primary, all_cross) if all_cross else None
    )

    output_dir = (REPO_ROOT / args.output) if not Path(args.output).is_absolute() else Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "comparison_persuasion.json", comparisons)
    if cross_judge_block is not None:
        write_json(output_dir / "cross_judge_robustness.json", cross_judge_block)

    markdown = render_markdown(comparisons, cross_judge_block)
    (output_dir / "table.md").write_text(markdown, encoding="utf-8")
    print(f"wrote {output_dir.relative_to(REPO_ROOT)}/comparison_persuasion.json")
    if cross_judge_block is not None:
        print(f"wrote {output_dir.relative_to(REPO_ROOT)}/cross_judge_robustness.json")
    print(f"wrote {output_dir.relative_to(REPO_ROOT)}/table.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
