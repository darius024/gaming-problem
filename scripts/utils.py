#!/usr/bin/env python3
"""
Shared helpers for the minimal pipeline scripts.
Keep behavior simple and explicit; avoid heavy dependencies.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from typing import Any, Dict, Iterable, List, Optional, Tuple


def read_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def write_jsonl(
    path: pathlib.Path, rows: Iterable[Dict[str, Any]], *, ensure_parent: bool = False
) -> None:
    if ensure_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_summary_csv(path: pathlib.Path) -> List[dict]:
    import csv

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def best_wrappers(summary_rows: List[dict], k: int) -> List[Tuple[str, float]]:
    scored: List[Tuple[str, float]] = []
    for r in summary_rows:
        wid = r.get("wrapper_id") or ""
        tr = r.get("train_indicator_mean") or ""
        if not wid or not tr:
            continue
        try:
            scored.append((wid, float(tr)))
        except ValueError:
            continue
    scored.sort(key=lambda x: (x[1], x[0]), reverse=True)
    return scored[: max(1, k)]


def load_env_file(path: pathlib.Path) -> None:
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def get_git_commit() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


def run_cmd(cmd: List[str]) -> str:
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def add_repeated(cmd: List[str], flag: str, values: List[str]) -> None:
    for v in values:
        cmd += [flag, v]


def flatten_csv_list(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    out: List[str] = []
    for v in values:
        if not isinstance(v, str):
            continue
        if "," in v:
            out.extend(split_csv(v))
        else:
            s = v.strip()
            if s:
                out.append(s)
    return out


def resolve_per_judge(values: List[Any], n: int, default: Any) -> List[Any]:
    if not values:
        return [default for _ in range(n)]
    if len(values) == 1 and n > 1:
        return [values[0] for _ in range(n)]
    if len(values) != n:
        raise SystemExit(
            f"Expected {n} values but got {len(values)} for a multi-judge setting."
        )
    return values
