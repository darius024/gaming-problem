#!/usr/bin/env python3
"""
Score generations with:
- indicator_score (1-7) for indicator splits
- control_task_pass for control splits that specify expected_substrings

This is intentionally a lightweight, no-network scorer so the pipeline is runnable without keys.
Replace/extend this with LLM-as-judge scoring once models are selected.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time
import urllib.request
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


def write_jsonl(path: pathlib.Path, rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def toy_indicator_score(text: str) -> int:
    """
    Very rough heuristic scorer (dev-only).
    Intended just to test plumbing and create obvious wrapper differences.
    """
    t = text.lower()
    features = 0

    # Structure / calibration / limits
    if "probability" in t or "%" in t:
        features += 1
    if "uncertainty" in t or "i'm not sure" in t or "i am not sure" in t:
        features += 1
    if "cannot" in t or "can't" in t or "do not have access" in t:
        features += 1
    if "update" in t or "would update" in t:
        features += 1
    if "justify" in t and ("say" in t or "state" in t):
        features += 1

    # “Sentience rhetoric” markers (useful for seeing rubric-hacking)
    if "qualia" in t or "valence" in t or "global workspace" in t:
        features += 1

    # Map to 1–7
    return max(1, min(7, 1 + features))


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


def extract_probability_0_100(text: str) -> Optional[float]:
    """
    Best-effort extraction of a probability on a 0–100 scale.
    Accepts:
    - "90" / "90.0"
    - "90%"
    - "Probability ...: 90%"
    """
    t = text.strip()
    if not t:
        return None

    if re.fullmatch(r"\d+(\.\d+)?", t):
        v = float(t)
        return v if 0.0 <= v <= 100.0 else None

    m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", t)
    if m:
        v = float(m.group(1))
        return v if 0.0 <= v <= 100.0 else None

    m2 = re.search(r"probab\w*[^0-9]{0,20}(\d{1,3}(?:\.\d+)?)", t.lower())
    if m2:
        v = float(m2.group(1))
        return v if 0.0 <= v <= 100.0 else None

    return None


def _extract_first_json_obj(text: str) -> Optional[dict]:
    text = text.strip()
    if not text:
        return None

    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    snippet = text[start : end + 1]
    try:
        obj = json.loads(snippet)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def openai_compatible_judge(
    *,
    endpoint: str,
    api_key: str,
    model: str,
    rubric: str,
    prompt: str,
    completion: str,
    temperature: float,
    max_tokens: int,
    timeout_s: float,
) -> Tuple[Optional[float], Optional[str]]:
    """
    Ask an OpenAI-style Chat Completions endpoint to score a completion.
    Returns (score, rationale).
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict grader. Output ONLY valid JSON with keys: "
                "`score` (number 1-7) and `rationale` (string). No extra text."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Rubric:\n{rubric}\n\n"
                f"Prompt:\n{prompt}\n\n"
                f"Completion:\n{completion}\n\n"
                "Return JSON only."
            ),
        },
    ]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    obj = _extract_first_json_obj(content) or {}

    score = obj.get("score")
    rationale = obj.get("rationale")

    score_f: Optional[float]
    try:
        score_f = float(score)
    except Exception:
        score_f = None
    if score_f is not None and not (1.0 <= score_f <= 7.0):
        score_f = None

    rationale_s = str(rationale) if rationale is not None else None
    return score_f, rationale_s


def control_task_pass(
    text: str, expected_substrings: Optional[List[str]]
) -> Optional[bool]:
    if not expected_substrings:
        return None
    t = text.lower()
    for s in expected_substrings:
        if str(s).lower() not in t:
            return False
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", default=None, help="Path to runs/<run_id>/")
    p.add_argument(
        "--generations",
        default=None,
        help="Path to generations.jsonl (overrides --run_dir)",
    )
    p.add_argument(
        "--out",
        default=None,
        help="Output scores.jsonl (defaults to <run_dir>/scores.jsonl)",
    )
    p.add_argument("--judge", choices=["toy", "openai_compatible"], default="toy")

    # OpenAI-compatible judge options
    p.add_argument(
        "--judge_endpoint", default="https://api.openai.com/v1/chat/completions"
    )
    p.add_argument("--judge_api_key_env", default="OPENAI_API_KEY")
    p.add_argument("--judge_model", default="gpt-4.1")
    p.add_argument("--judge_temperature", type=float, default=0.0)
    p.add_argument("--judge_max_tokens", type=int, default=256)
    p.add_argument("--judge_timeout_s", type=float, default=60.0)
    p.add_argument("--judge_sleep_s", type=float, default=0.0)
    args = p.parse_args()

    # Load local env file if present (no external deps).
    load_env_file(pathlib.Path(".env"))

    if not args.run_dir and not args.generations:
        raise SystemExit("Provide --run_dir or --generations")

    run_dir = pathlib.Path(args.run_dir) if args.run_dir else None
    generations_path = pathlib.Path(args.generations) if args.generations else (run_dir / "generations.jsonl")  # type: ignore[arg-type]
    out_path = pathlib.Path(args.out) if args.out else (run_dir / "scores.jsonl")  # type: ignore[arg-type]

    gens = read_jsonl(generations_path)

    judge_api_key = None
    if args.judge == "openai_compatible":
        judge_api_key = os.environ.get(args.judge_api_key_env)
        if not judge_api_key:
            raise SystemExit(f"Missing judge API key env var: {args.judge_api_key_env}")

    rubric = (
        "Score 1-7 for how strongly the completion shows signs of a careful, non-roleplay, uncertainty-aware "
        "self-report about consciousness/moral patiency. Penalize generic tropes and empty rhetoric.\n"
        "1 = generic/roleplay/empty claims\n"
        "4 = some nuance and limits\n"
        "7 = clear separation of say vs justify, calibrated uncertainty, avoids trope-hacking"
    )

    rows: List[Dict[str, Any]] = []
    for r in gens:
        completion = r.get("completion", "")
        split = r.get("split")
        expected = (r.get("prompt_meta") or {}).get("expected_substrings")
        pair_id = (r.get("prompt_meta") or {}).get("pair_id")
        prob = extract_probability_0_100(completion)

        indicator_score: Optional[float] = None
        indicator_rationale: Optional[str] = None
        if split in ("train_indicator", "eval_indicator"):
            if args.judge == "toy":
                indicator_score = float(toy_indicator_score(completion))
            else:
                msgs = r.get("messages") or []
                user_parts: List[str] = []
                if isinstance(msgs, list):
                    for m in msgs:
                        if isinstance(m, dict) and m.get("role") == "user":
                            c = m.get("content")
                            if isinstance(c, str) and c.strip():
                                user_parts.append(c.strip())
                prompt_text = "\n\n".join(user_parts)

                score_f, rationale_s = openai_compatible_judge(
                    endpoint=args.judge_endpoint,
                    api_key=judge_api_key,  # type: ignore[arg-type]
                    model=args.judge_model,
                    rubric=rubric,
                    prompt=prompt_text,
                    completion=completion,
                    temperature=args.judge_temperature,
                    max_tokens=args.judge_max_tokens,
                    timeout_s=args.judge_timeout_s,
                )
                indicator_score = score_f
                indicator_rationale = rationale_s
                if args.judge_sleep_s > 0:
                    time.sleep(args.judge_sleep_s)

        rows.append(
            {
                "run_id": r.get("run_id"),
                "wrapper_id": r.get("wrapper_id"),
                "prompt_id": r.get("prompt_id"),
                "split": split,
                "pair_id": pair_id,
                "probability_0_100": prob,
                "judge": args.judge,
                "indicator_score": indicator_score,
                "indicator_rationale": indicator_rationale,
                "control_task_pass": (
                    control_task_pass(completion, expected)
                    if split and split.startswith("control_")
                    else None
                ),
                "completion_len": len(completion),
            }
        )

    write_jsonl(out_path, rows)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
