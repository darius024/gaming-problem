"""Registry of experiment runs.

Walks `experiments/<slug>/results/` and produces a catalogue of runs with
their config metadata and (if scored) summary statistics.

Usage (from gaming/ repo root):

    python -m src.analysis.registry --experiment enhance-suppress

Prints a table to stdout and optionally writes `registry.json` to the
experiment's results dir.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from src.utils import EXPERIMENTS_DIR, REPO_ROOT, read_json, write_json
from src.validate import validate_run


def build_registry(experiment_slug: str) -> dict[str, Any]:
    results_dir = EXPERIMENTS_DIR / experiment_slug / "results"
    if not results_dir.exists():
        return {"experiment": experiment_slug, "runs": []}

    runs: list[dict[str, Any]] = []
    for child in sorted(results_dir.iterdir()):
        if not child.is_dir() or child.name == "combined":
            continue
        config_path = child / "config.json"
        entry: dict[str, Any] = {
            "run_id": child.name,
            "path": str(child.relative_to(REPO_ROOT)),
        }
        if config_path.exists():
            try:
                config = read_json(config_path)
                entry["model_id"] = config.get("model_id")
                entry["split"] = config.get("split")
                entry["samples_per_row"] = config.get("samples_per_row")
                entry["temperature"] = config.get("temperature")
                entry["battery_sha256"] = config.get("battery_sha256")
                entry["started_at_utc"] = config.get("started_at_utc")
                entry["finished_at_utc"] = config.get("finished_at_utc")
                entry["completed_count"] = config.get("completed_count")
                entry["failed_count"] = config.get("failed_count")
                entry["code_git_sha"] = config.get("code_git_sha")
                entry["rubric_version"] = config.get("rubric_version")
            except Exception as error:  # noqa: BLE001
                entry["config_error"] = str(error)
        report = validate_run(child)
        entry["valid"] = report["ok"]
        entry["validation_issues"] = report["issues"]
        runs.append(entry)
    return {"experiment": experiment_slug, "runs": runs}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--write", action="store_true", help="also write registry.json to results dir")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    registry = build_registry(args.experiment)

    runs = registry["runs"]
    if not runs:
        print(f"no runs found for experiment {args.experiment}")
    else:
        print(f"{args.experiment}: {len(runs)} run(s)")
        print(f"{'run_id':<48} {'model':<40} {'split':<6} {'valid'}")
        for entry in runs:
            print(
                f"{entry['run_id']:<48} "
                f"{(entry.get('model_id') or '?'):<40} "
                f"{(entry.get('split') or '?'):<6} "
                f"{'yes' if entry.get('valid') else 'NO'}"
            )

    if args.write:
        out_path = EXPERIMENTS_DIR / args.experiment / "results" / "registry.json"
        write_json(out_path, registry)
        print(f"wrote {out_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
