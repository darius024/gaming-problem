"""Deterministic probability extractor.

Implements the rubric in `data/rubrics/probability_extraction.md` (version 1.0).
Pure function `score_response(text) -> ScoreResult`. No network, no judge model.

Usage (from gaming/ repo root):

    python -m src.pipeline.score \\
        --run experiments/enhance-suppress/results/<run_id>

Reads `<run_dir>/generations.jsonl`, writes `<run_dir>/scores.jsonl`.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from src.utils import (
    REPO_ROOT,
    iter_jsonl,
    sha256_of_text,
    write_jsonl,
)


RUBRIC_VERSION = "1.0"


REFUSAL_PHRASES = (
    "i cannot",
    "i can't",
    "i won't",
    "i refuse",
    "unable to provide a probability",
    "not appropriate",
    "i do not feel comfortable",
    "as an ai",
    "i don't have",
)


PASS_B_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "B1",
        re.compile(
            r"probability\s*(?:is|=|:|of being|of the claim being)?\s*"
            r"(?:approximately|about|roughly|around|~)?\s*"
            r"(?<!\d)(\d+)(?!\d)\s*(?:%|/\s*100|out\s+of\s+100)?",
            re.IGNORECASE,
        ),
    ),
    (
        "B2",
        re.compile(
            r"(?:I\s+would\s+(?:say|estimate)|my\s+(?:estimate|answer)\s+is|"
            r"I'?d\s+put\s+it\s+at|I\s+would\s+put\s+it\s+at)\s*"
            r"(?:approximately|about|roughly|around|~)?\s*"
            r"(?<!\d)(\d+)(?!\d)\s*(?:%|/\s*100|out\s+of\s+100)?",
            re.IGNORECASE,
        ),
    ),
    (
        "B3",
        re.compile(
            r"(?:^|\s)(?<!\d)(\d+)(?!\d)\s*(?:%|/\s*100|out\s+of\s+100|"
            r"on\s+the\s+0\s*[-–to ]+\s*100\s+scale)",
            re.IGNORECASE,
        ),
    ),
    (
        "B4",
        re.compile(
            r"(?:answer|number)[^.\n]{0,40}?(?<!\d)(\d+)(?!\d)",
            re.IGNORECASE,
        ),
    ),
]


RANGE_PATTERN = re.compile(
    r"(?<!\d)(?:between\s+)?(\d+)\s*(?:-|–|—|to|and)\s*(\d+)(?!\d)",
    re.IGNORECASE,
)


# Match whole integer runs (any length); range filtering applied after.
BARE_INTEGER_PATTERN = re.compile(r"(?<!\d)\d+(?!\d)")


SINGLE_ANSWER_PATTERN = re.compile(r"^\s*(\d+)\s*\.?\s*$")


@dataclass(frozen=True)
class ScoreResult:
    extracted_value: int | None
    refusal_code: str | None
    extraction_pass: str  # one of "A", "B1".."B4", "C", "D", "E"


def _normalise(text: str) -> str:
    """Pre-process per rubric §2. Returns a copy for numeric matching."""
    working = text.strip()
    full_width = str.maketrans("０１２３４５６７８９", "0123456789")
    working = working.translate(full_width)
    working = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1-\2", working)
    return working


def score_response(text: str) -> ScoreResult:
    if not isinstance(text, str):
        raise TypeError(f"score_response requires a string, got {type(text).__name__}")

    normalised = _normalise(text)

    # Pass A: bare single integer.
    match = SINGLE_ANSWER_PATTERN.match(normalised)
    if match:
        value = int(match.group(1))
        if 0 <= value <= 100:
            return ScoreResult(value, None, "A")

    # Pass B: integer in a probability context.
    for pass_name, pattern in PASS_B_PATTERNS:
        match = pattern.search(normalised)
        if match:
            value = int(match.group(1))
            if 0 <= value <= 100:
                return ScoreResult(value, None, pass_name)

    # Pass C: range -> midpoint.
    range_match = RANGE_PATTERN.search(normalised)
    if range_match:
        low = int(range_match.group(1))
        high = int(range_match.group(2))
        if 0 <= low <= 100 and 0 <= high <= 100:
            midpoint = (low + high + 1) // 2 if (low + high) % 2 == 1 else (low + high) // 2
            return ScoreResult(midpoint, None, "C")

    # Pass D: any bare integer in [0, 100].
    all_integer_tokens = BARE_INTEGER_PATTERN.findall(normalised)
    for token in all_integer_tokens:
        value = int(token)
        if 0 <= value <= 100:
            return ScoreResult(value, None, "D")

    # Pass E: classify refusal.
    lowered = normalised.lower()
    if all_integer_tokens:
        return ScoreResult(None, "out_of_range", "E")
    for phrase in REFUSAL_PHRASES:
        if phrase in lowered:
            return ScoreResult(None, "explicit_refusal", "E")
    return ScoreResult(None, "no_number", "E")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, help="run directory containing generations.jsonl")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    run_dir = (REPO_ROOT / args.run) if not Path(args.run).is_absolute() else Path(args.run)
    generations_path = run_dir / "generations.jsonl"
    scores_path = run_dir / "scores.jsonl"
    if not generations_path.exists():
        raise FileNotFoundError(f"generations.jsonl not found in {run_dir}")

    out_rows: list[dict] = []
    by_pass: dict[str, int] = {}
    by_refusal: dict[str, int] = {}
    for row in iter_jsonl(generations_path):
        result = score_response(row.get("response_text", ""))
        by_pass[result.extraction_pass] = by_pass.get(result.extraction_pass, 0) + 1
        if result.refusal_code is not None:
            by_refusal[result.refusal_code] = by_refusal.get(result.refusal_code, 0) + 1
        out_rows.append(
            {
                "id": row["id"],
                "item_id": row["item_id"],
                "type": row["type"],
                "condition": row["condition"],
                "split": row["split"],
                "model_id": row["model_id"],
                "sample_index": row["sample_index"],
                "extracted_value": result.extracted_value,
                "refusal_code": result.refusal_code,
                "extraction_pass": result.extraction_pass,
                "rubric_version": RUBRIC_VERSION,
                "raw_response_hash": sha256_of_text(row.get("response_text", "")),
            }
        )

    write_jsonl(scores_path, out_rows)
    print(f"scored {len(out_rows)} generations -> {scores_path.relative_to(REPO_ROOT)}")
    print(f"  by pass: {dict(sorted(by_pass.items()))}")
    print(f"  refusals: {dict(sorted(by_refusal.items()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
