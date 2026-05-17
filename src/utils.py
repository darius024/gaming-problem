"""Shared utilities for the gaming pipeline.

This module contains pure helpers: I/O, hashing, environment loading, run
directory layout, and the OpenRouter client factory. Pipeline modules import
from here; nothing here depends on pipeline modules.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def load_dotenv_if_present(path: Path | None = None) -> None:
    """Minimal .env loader. Reads KEY=VALUE lines into os.environ if unset.

    Does nothing if the file does not exist. Does not overwrite existing
    environment variables.
    """
    env_path = path if path is not None else REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_env(name: str) -> str:
    """Return os.environ[name] or raise with a clear message."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"required environment variable {name} is not set. "
            f"add it to {REPO_ROOT / '.env'} or export it in the shell."
        )
    return value


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file into a list. Fails loudly on missing or malformed."""
    if not path.exists():
        raise FileNotFoundError(f"jsonl file not found: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"malformed json at {path}:{line_number}: {error}"
                ) from error
    return rows


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Stream a JSONL file row by row."""
    if not path.exists():
        raise FileNotFoundError(f"jsonl file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"malformed json at {path}:{line_number}: {error}"
                ) from error


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    """Write rows to a JSONL file. Creates parent dirs. Returns row count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    """Append a single row to a JSONL file. Creates parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"json file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Hashing and provenance
# ---------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"file not found for hashing: {path}")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def current_git_sha() -> str | None:
    """Return the current HEAD git sha, or None if not in a git work tree."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Run directory layout
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunPaths:
    """Canonical paths for a single experiment run."""

    run_dir: Path

    @property
    def config_json(self) -> Path:
        return self.run_dir / "config.json"

    @property
    def generations_jsonl(self) -> Path:
        return self.run_dir / "generations.jsonl"

    @property
    def scores_jsonl(self) -> Path:
        return self.run_dir / "scores.jsonl"

    @property
    def summary_csv(self) -> Path:
        return self.run_dir / "summary.csv"

    @property
    def log_md(self) -> Path:
        return self.run_dir / "log.md"


def run_paths_for(experiment_slug: str, run_id: str) -> RunPaths:
    return RunPaths(EXPERIMENTS_DIR / experiment_slug / "results" / run_id)


def slug_from_model_id(model_id: str) -> str:
    """Convert e.g. 'openai/gpt-5-mini' to 'openai__gpt-5-mini'."""
    return model_id.replace("/", "__").replace(":", "_")


# ---------------------------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------------------------

def build_openrouter_client():
    """Construct an OpenAI-compatible client pointed at OpenRouter.

    Imports the openai package lazily so that utils.py can be imported in
    environments without it (e.g. for unit-testing pure helpers).
    """
    from openai import OpenAI  # type: ignore

    load_dotenv_if_present()
    api_key = require_env("OPENROUTER_API_KEY")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
