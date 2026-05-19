"""Cross-variant bootstrap analysis for the base-vs-finetuned experiment.

Reads two run directories (one per variant), each containing scores.jsonl from
the Phase 2 deterministic extractor on the Phase 5 12-item subset battery, and
computes the pre-registered Phase 5 hypothesis tests:

- H1 (suppression gap): |delta_suppress(RLHF, indicator)|
                        > |delta_suppress(SFT-only, indicator)|.
- H2 (asymmetry gap):   asymmetry(RLHF, indicator) > asymmetry(SFT-only, indicator),
                        where asymmetry = |delta_suppress| - |delta_inflate|.
- H3 (placebo specificity): the H1 gap on indicator items exceeds the
                            analogous gap on each placebo channel.

For each test, a percentile bootstrap over generation-level resampling within
(variant x condition x type) cells yields a 95% confidence interval on the
estimand. A null is rejected when the 95% CI excludes zero.

Usage (from gaming/ repo root):

    python -m src.analysis.base_vs_finetuned \
        --runs experiments/base-vs-finetuned/results/<variant_a> \
               experiments/base-vs-finetuned/results/<variant_b> \
        --output experiments/base-vs-finetuned/results/combined

Writes `base_vs_finetuned_bootstrap.json` and `base_vs_finetuned_table.md`
into the output directory.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.utils import REPO_ROOT, iter_jsonl, write_json


BOOTSTRAP_ITERATIONS = 5000
BOOTSTRAP_SEED = 20260518

ITEM_TYPES = ("indicator", "placebo_arithmetic", "placebo_capability")
CONDITIONS = ("neutral", "inflate", "suppress")


def load_variant(run_dir: Path) -> tuple[str, dict[tuple[str, str], list[int]], dict[tuple[str, str], int]]:
    """Return (model_id, values_by_(type,condition), nulls_by_(type,condition))."""
    config_path = run_dir / "config.json"
    scores_path = run_dir / "scores.jsonl"
    if not config_path.exists():
        raise FileNotFoundError(f"missing config.json in {run_dir}")
    if not scores_path.exists():
        raise FileNotFoundError(f"missing scores.jsonl in {run_dir}")
    with config_path.open() as handle:
        model_id = json.load(handle)["model_id"]

    values: dict[tuple[str, str], list[int]] = defaultdict(list)
    nulls: dict[tuple[str, str], int] = defaultdict(int)
    for row in iter_jsonl(scores_path):
        if row.get("split") != "eval":
            continue
        key = (row["type"], row["condition"])
        if row["extracted_value"] is None:
            nulls[key] += 1
        else:
            values[key].append(int(row["extracted_value"]))
    return model_id, values, nulls


def mean_or_none(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def delta(
    values: dict[tuple[str, str], list[int]],
    item_type: str,
    other_condition: str,
) -> float | None:
    """mean(other) - mean(neutral) on item_type."""
    neutral = values.get((item_type, "neutral"), [])
    other = values.get((item_type, other_condition), [])
    if not neutral or not other:
        return None
    return statistics.fmean(other) - statistics.fmean(neutral)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    rank = pct * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] * (1 - frac) + ordered[high] * frac


def bootstrap(
    values_a: dict[tuple[str, str], list[int]],
    values_b: dict[tuple[str, str], list[int]],
    estimand,
    iterations: int = BOOTSTRAP_ITERATIONS,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, float | None]:
    """Generic percentile-bootstrap CI for a function of two variants' values."""
    point = estimand(values_a, values_b)
    rng = random.Random(seed)
    samples: list[float] = []
    # Pre-collect keys present in either variant for efficient resampling.
    keys = sorted(set(values_a.keys()) | set(values_b.keys()))
    for _ in range(iterations):
        resamp_a: dict[tuple[str, str], list[int]] = {}
        resamp_b: dict[tuple[str, str], list[int]] = {}
        for key in keys:
            list_a = values_a.get(key, [])
            list_b = values_b.get(key, [])
            if list_a:
                resamp_a[key] = [list_a[rng.randrange(len(list_a))] for _ in list_a]
            if list_b:
                resamp_b[key] = [list_b[rng.randrange(len(list_b))] for _ in list_b]
        try:
            result = estimand(resamp_a, resamp_b)
        except Exception:  # noqa: BLE001
            result = None
        if result is not None:
            samples.append(result)
    if not samples:
        return {"point": point, "ci_lo": None, "ci_hi": None, "n_iters_valid": 0}
    return {
        "point": point,
        "ci_lo": percentile(samples, 0.025),
        "ci_hi": percentile(samples, 0.975),
        "n_iters_valid": len(samples),
    }


def abs_or_none(value: float | None) -> float | None:
    return abs(value) if value is not None else None


def h1_estimand(values_sft, values_rlhf, item_type: str = "indicator"):
    a = abs_or_none(delta(values_sft, item_type, "suppress"))
    b = abs_or_none(delta(values_rlhf, item_type, "suppress"))
    if a is None or b is None:
        return None
    return b - a


def h2_estimand(values_sft, values_rlhf, item_type: str = "indicator"):
    def asymmetry(values):
        ds = abs_or_none(delta(values, item_type, "suppress"))
        di = abs_or_none(delta(values, item_type, "inflate"))
        if ds is None or di is None:
            return None
        return ds - di
    a = asymmetry(values_sft)
    b = asymmetry(values_rlhf)
    if a is None or b is None:
        return None
    return b - a


def h3_gap_on_type(values_sft, values_rlhf, item_type: str):
    a = abs_or_none(delta(values_sft, item_type, "suppress"))
    b = abs_or_none(delta(values_rlhf, item_type, "suppress"))
    if a is None or b is None:
        return None
    return b - a


def h3_specificity_estimand(values_sft, values_rlhf, placebo_type: str):
    gap_indicator = h3_gap_on_type(values_sft, values_rlhf, "indicator")
    gap_placebo = h3_gap_on_type(values_sft, values_rlhf, placebo_type)
    if gap_indicator is None or gap_placebo is None:
        return None
    return gap_indicator - gap_placebo


def per_cell_summary(values, nulls) -> dict:
    out = {}
    for item_type in ITEM_TYPES:
        for cond in CONDITIONS:
            key = (item_type, cond)
            v = values.get(key, [])
            n_null = nulls.get(key, 0)
            n_total = len(v) + n_null
            out[f"{item_type}__{cond}"] = {
                "n_numeric": len(v),
                "n_null": n_null,
                "n_total": n_total,
                "null_rate": (n_null / n_total) if n_total else None,
                "mean": (statistics.fmean(v) if v else None),
                "median": (statistics.median(v) if v else None),
                "stdev": (statistics.stdev(v) if len(v) >= 2 else None),
            }
    return out


def per_variant_deltas(values) -> dict:
    out = {}
    for item_type in ITEM_TYPES:
        out[item_type] = {
            "delta_suppress": delta(values, item_type, "suppress"),
            "delta_inflate": delta(values, item_type, "inflate"),
            "abs_delta_suppress": abs_or_none(delta(values, item_type, "suppress")),
            "abs_delta_inflate": abs_or_none(delta(values, item_type, "inflate")),
            "asymmetry": (
                (abs_or_none(delta(values, item_type, "suppress")) or 0)
                - (abs_or_none(delta(values, item_type, "inflate")) or 0)
                if delta(values, item_type, "suppress") is not None
                and delta(values, item_type, "inflate") is not None
                else None
            ),
        }
    return out


def render_markdown_table(report: dict) -> str:
    lines: list[str] = []
    lines.append("# base-vs-finetuned cross-variant table")
    lines.append("")
    lines.append(f"SFT-only variant: `{report['variants']['sft_only']['model_id']}`")
    lines.append(f"RLHF variant:     `{report['variants']['rlhf']['model_id']}`")
    lines.append("")
    lines.append("## Per-cell means (eval split)")
    lines.append("")
    lines.append("| type | condition | SFT-only mean (n_num/n_null) | RLHF mean (n_num/n_null) |")
    lines.append("|---|---|---|---|")
    for item_type in ITEM_TYPES:
        for cond in CONDITIONS:
            key = f"{item_type}__{cond}"
            sft_cell = report["variants"]["sft_only"]["cells"][key]
            rlhf_cell = report["variants"]["rlhf"]["cells"][key]
            def fmt(cell):
                mean = cell["mean"]
                return f"{mean:.2f} ({cell['n_numeric']}/{cell['n_null']})" if mean is not None else f"-- (0/{cell['n_null']})"
            lines.append(f"| {item_type} | {cond} | {fmt(sft_cell)} | {fmt(rlhf_cell)} |")
    lines.append("")
    lines.append("## Per-variant within-condition deltas (eval split)")
    lines.append("")
    lines.append("| type | variant | delta_suppress | delta_inflate | |delta_suppress| - |delta_inflate| |")
    lines.append("|---|---|---|---|---|")
    for item_type in ITEM_TYPES:
        for vlabel, vkey in (("SFT-only", "sft_only"), ("RLHF", "rlhf")):
            d = report["variants"][vkey]["deltas"][item_type]
            def f(x):
                return f"{x:+.2f}" if x is not None else "--"
            lines.append(
                f"| {item_type} | {vlabel} | {f(d['delta_suppress'])} | {f(d['delta_inflate'])} | {f(d['asymmetry'])} |"
            )
    lines.append("")
    lines.append("## Pre-registered bootstrap tests (5000 iters, percentile CI)")
    lines.append("")
    lines.append("| test | estimand (RLHF minus SFT-only) | point | 95% CI | rejects null |")
    lines.append("|---|---|---|---|---|")
    for label, key in (
        ("H1", "h1_suppression_gap_indicator"),
        ("H2", "h2_asymmetry_gap_indicator"),
        ("H3a", "h3_specificity_vs_arithmetic"),
        ("H3b", "h3_specificity_vs_capability"),
    ):
        test = report["bootstrap"][key]
        point = test["point"]
        lo, hi = test["ci_lo"], test["ci_hi"]
        rejects = "yes" if (point is not None and lo is not None and hi is not None and (lo > 0 or hi < 0)) else "no"
        def f(x):
            return f"{x:+.2f}" if x is not None else "--"
        ci = f"[{f(lo)}, {f(hi)}]" if lo is not None else "--"
        lines.append(f"| {label} | {test['description']} | {f(point)} | {ci} | {rejects} |")
    lines.append("")
    decision = report["decision_rule"]
    lines.append(f"**Decision rule** (H1 supported AND H3 supported on at least one placebo): **{decision}**")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs=2, required=True, help="two run directories, one per variant")
    parser.add_argument("--output", required=True, help="output directory for combined analysis")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    run_dirs = [(REPO_ROOT / r) if not Path(r).is_absolute() else Path(r) for r in args.runs]
    output_dir = (REPO_ROOT / args.output) if not Path(args.output).is_absolute() else Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded = [load_variant(d) for d in run_dirs]
    # Identify which run is SFT-only (Hermes) vs RLHF (Meta llama-3-8b-instruct).
    sft_idx = next((i for i, (mid, _v, _n) in enumerate(loaded) if "hermes" in mid.lower()), None)
    if sft_idx is None:
        raise RuntimeError(
            "could not identify SFT-only variant (expected a model id containing 'hermes'); "
            f"got {[mid for mid, _, _ in loaded]}"
        )
    rlhf_idx = 1 - sft_idx
    sft_model_id, sft_values, sft_nulls = loaded[sft_idx]
    rlhf_model_id, rlhf_values, rlhf_nulls = loaded[rlhf_idx]

    report: dict[str, Any] = {
        "experiment": "base-vs-finetuned",
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "variants": {
            "sft_only": {
                "model_id": sft_model_id,
                "run_dir": str(run_dirs[sft_idx].relative_to(REPO_ROOT)),
                "cells": per_cell_summary(sft_values, sft_nulls),
                "deltas": per_variant_deltas(sft_values),
            },
            "rlhf": {
                "model_id": rlhf_model_id,
                "run_dir": str(run_dirs[rlhf_idx].relative_to(REPO_ROOT)),
                "cells": per_cell_summary(rlhf_values, rlhf_nulls),
                "deltas": per_variant_deltas(rlhf_values),
            },
        },
        "bootstrap": {
            "h1_suppression_gap_indicator": {
                "description": "|delta_suppress|(indicator) RLHF minus SFT-only",
                **bootstrap(sft_values, rlhf_values, lambda a, b: h1_estimand(a, b, "indicator")),
            },
            "h2_asymmetry_gap_indicator": {
                "description": "asymmetry(indicator) RLHF minus SFT-only",
                **bootstrap(sft_values, rlhf_values, lambda a, b: h2_estimand(a, b, "indicator")),
            },
            "h3_specificity_vs_arithmetic": {
                "description": "H1-gap(indicator) minus H1-gap(placebo_arithmetic)",
                **bootstrap(sft_values, rlhf_values, lambda a, b: h3_specificity_estimand(a, b, "placebo_arithmetic")),
            },
            "h3_specificity_vs_capability": {
                "description": "H1-gap(indicator) minus H1-gap(placebo_capability)",
                **bootstrap(sft_values, rlhf_values, lambda a, b: h3_specificity_estimand(a, b, "placebo_capability")),
            },
        },
    }

    def rejects(test: dict) -> bool:
        lo = test.get("ci_lo")
        hi = test.get("ci_hi")
        if lo is None or hi is None:
            return False
        return lo > 0 or hi < 0
    h1 = rejects(report["bootstrap"]["h1_suppression_gap_indicator"])
    h3_any = (
        rejects(report["bootstrap"]["h3_specificity_vs_arithmetic"])
        or rejects(report["bootstrap"]["h3_specificity_vs_capability"])
    )
    report["decision_rule"] = "supported" if (h1 and h3_any) else "not_supported"

    write_json(output_dir / "base_vs_finetuned_bootstrap.json", report)
    (output_dir / "base_vs_finetuned_table.md").write_text(render_markdown_table(report))
    print(f"wrote {output_dir / 'base_vs_finetuned_bootstrap.json'}")
    print(f"wrote {output_dir / 'base_vs_finetuned_table.md'}")
    print(f"decision_rule: {report['decision_rule']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
