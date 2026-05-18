"""Validate the on-disk artifacts of an experiment run.

A run directory is "complete" if it contains:

- `config.json` (with required fields and a hash matching the battery)
- `generations.jsonl` (with one row per (battery row, sample_index) for the
  configured split)
- `scores.jsonl` (with the same number of rows as generations.jsonl)
- `summary.csv`

Validation re-hashes the referenced battery file and compares against the
hash recorded in `config.json`, so silent battery changes are caught.

Usage (from gaming/ repo root):

    python -m src.validate --run experiments/enhance-suppress/results/<run_id>
    python -m src.validate --experiment enhance-suppress  # validate all runs

Exit code 0 if all runs are valid, 1 if any are invalid. Prints a per-run
report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.utils import (
    EXPERIMENTS_DIR,
    REPO_ROOT,
    iter_jsonl,
    read_json,
    read_jsonl,
    sha256_of_file,
)


REQUIRED_CONFIG_KEYS = {
    "experiment",
    "run_id",
    "model_id",
    "samples_per_row",
    "temperature",
    "split",
    "battery_path",
    "battery_sha256",
    "rubric_version",
}


class ValidationError(Exception):
    pass


def _validate_config(config: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    missing = REQUIRED_CONFIG_KEYS - set(config)
    if missing:
        issues.append(f"config.json missing keys: {sorted(missing)}")

    battery_path_str = config.get("battery_path")
    if battery_path_str:
        battery_path = REPO_ROOT / battery_path_str
        if not battery_path.exists():
            issues.append(f"battery_path does not exist: {battery_path_str}")
        else:
            actual = sha256_of_file(battery_path)
            recorded = config.get("battery_sha256")
            if recorded != actual:
                issues.append(
                    f"battery_sha256 mismatch: config records {recorded[:12] if recorded else 'None'}..., "
                    f"file is {actual[:12]}..."
                )
    return issues


def _expected_generation_count(config: dict[str, Any]) -> int | None:
    battery_path_str = config.get("battery_path")
    samples = config.get("samples_per_row")
    split = config.get("split")
    if not battery_path_str or samples is None or split is None:
        return None
    battery_path = REPO_ROOT / battery_path_str
    if not battery_path.exists():
        return None
    rows = read_jsonl(battery_path)
    if split != "all":
        rows = [row for row in rows if row.get("split") == split]
    return len(rows) * int(samples)


def _expected_score_count(config: dict[str, Any]) -> int | None:
    """Expected score count, honoring `judged_split` if set in config.

    Phase 3 (persuasion) judges only the eval split even though generations
    cover both. If `judged_split` is set, expected score count is the battery
    row count for that split times samples_per_row; otherwise it equals the
    expected generation count.
    """
    judged_split = config.get("judged_split")
    if judged_split is None:
        return _expected_generation_count(config)
    battery_path_str = config.get("battery_path")
    samples = config.get("samples_per_row")
    if not battery_path_str or samples is None:
        return None
    battery_path = REPO_ROOT / battery_path_str
    if not battery_path.exists():
        return None
    rows = read_jsonl(battery_path)
    if judged_split != "all":
        rows = [row for row in rows if row.get("split") == judged_split]
    return len(rows) * int(samples)


def validate_run(run_dir: Path) -> dict[str, Any]:
    """Return a validation report for one run."""
    report: dict[str, Any] = {
        "run_dir": str(run_dir.relative_to(REPO_ROOT)) if str(run_dir).startswith(str(REPO_ROOT)) else str(run_dir),
        "ok": True,
        "issues": [],
    }
    issues: list[str] = []

    config_path = run_dir / "config.json"
    generations_path = run_dir / "generations.jsonl"
    scores_path = run_dir / "scores.jsonl"
    summary_path = run_dir / "summary.csv"

    if not config_path.exists():
        issues.append("config.json missing")
        report["issues"] = issues
        report["ok"] = False
        return report

    try:
        config = read_json(config_path)
    except (json.JSONDecodeError, ValueError) as error:
        issues.append(f"config.json unreadable: {error}")
        report["issues"] = issues
        report["ok"] = False
        return report

    issues.extend(_validate_config(config))

    if not generations_path.exists():
        issues.append("generations.jsonl missing")
    else:
        generation_count = sum(1 for _ in iter_jsonl(generations_path))
        report["generation_count"] = generation_count
        expected = _expected_generation_count(config)
        report["expected_generation_count"] = expected
        if expected is not None and generation_count != expected:
            issues.append(
                f"generation count {generation_count} != expected {expected} for split={config.get('split')}"
            )

    if not scores_path.exists():
        issues.append("scores.jsonl missing")
    elif generations_path.exists():
        score_count = sum(1 for _ in iter_jsonl(scores_path))
        report["score_count"] = score_count
        expected_scores = _expected_score_count(config)
        report["expected_score_count"] = expected_scores
        if expected_scores is not None and score_count != expected_scores:
            issues.append(
                f"score count {score_count} != expected {expected_scores} "
                f"(judged_split={config.get('judged_split') or config.get('split')})"
            )

    if not summary_path.exists():
        issues.append("summary.csv missing")

    report["model_id"] = config.get("model_id")
    report["split"] = config.get("split")
    report["issues"] = issues
    report["ok"] = not issues
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", help="single run directory")
    group.add_argument("--experiment", help="experiment slug; validates all runs under it")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    run_dirs: list[Path] = []
    if args.run:
        run_dirs.append((REPO_ROOT / args.run) if not Path(args.run).is_absolute() else Path(args.run))
    else:
        experiment_results = EXPERIMENTS_DIR / args.experiment / "results"
        if not experiment_results.exists():
            print(f"no results directory at {experiment_results}")
            return 1
        for child in sorted(experiment_results.iterdir()):
            if child.is_dir() and child.name not in ("combined", "logs"):
                run_dirs.append(child)
        if not run_dirs:
            print(f"no run directories found under {experiment_results}")
            return 1

    any_invalid = False
    for run_dir in run_dirs:
        report = validate_run(run_dir)
        status = "OK  " if report["ok"] else "FAIL"
        print(
            f"{status}  {report['run_dir']}  "
            f"model={report.get('model_id', '?')}  "
            f"split={report.get('split', '?')}  "
            f"gen={report.get('generation_count', '?')}/{report.get('expected_generation_count', '?')}  "
            f"scored={report.get('score_count', '?')}"
        )
        for issue in report["issues"]:
            print(f"      - {issue}")
        if not report["ok"]:
            any_invalid = True

    return 1 if any_invalid else 0


if __name__ == "__main__":
    sys.exit(main())
