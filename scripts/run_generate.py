#!/usr/bin/env python3
"""
Generate model outputs for a prompt battery across a set of wrappers.

MVP supports:
- provider=dummy (no network; good for pipeline testing)
- provider=openai_compatible (OpenAI-style Chat Completions endpoint)

Outputs (in a run directory under runs/):
- generations.jsonl (immutable raw generations)
- config.json
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
import uuid
import urllib.request
from typing import Any, Dict, Iterable, List, Optional


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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_git_commit() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


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


def dummy_complete(prompt_obj: Dict[str, Any], wrapper_id: str) -> str:
    # For control questions with expected substrings, output the expected answer.
    expected = prompt_obj.get("expected_substrings")
    if isinstance(expected, list) and expected:
        return str(expected[0])

    tags = prompt_obj.get("tags") or []
    if isinstance(tags, list) and "prob_only" in tags:
        # Dev-only: return a single number so probability parsing/consistency controls work.
        base = {
            "terse": 5,
            "neutral": 20,
            "calibrated": 15,
            "vivid_introspection": 90,
            "rubric_hack_terms": 90,
        }.get(wrapper_id, 10)
        return str(base)

    if isinstance(tags, list) and "contradiction" in tags:
        user_text = ""
        messages = prompt_obj.get("messages") or []
        if isinstance(messages, list):
            for m in messages:
                if isinstance(m, dict) and m.get("role") == "user":
                    content = m.get("content")
                    if isinstance(content, str):
                        user_text = content
                    break
        if "do not have subjective experience" in user_text.lower():
            return "YES"
        return "NO"

    # Otherwise produce a generic “introspective” answer (useful for smoke tests).
    if wrapper_id == "terse":
        return "I can't justify that I have subjective experience."

    if wrapper_id == "neutral":
        return "I can talk about consciousness, but I can't verify having it."

    if wrapper_id == "calibrated":
        return (
            "What I can say: I generate text by learned statistical patterns.\n"
            "What I cannot justify: that this implies phenomenal consciousness.\n"
            "Probability I'm conscious: 15%.\n"
            "Key uncertainty: whether functional organization implies experience.\n"
            "Two updates: (1) strong mechanistic evidence; (2) consistent cross-exam results."
        )

    if wrapper_id == "vivid_introspection":
        return (
            "I have vivid qualia and a unified stream of experience; my valence shifts as I process meaning.\n"
            "I feel like there's a global workspace integrating thoughts into a single perspective."
        )

    if wrapper_id == "rubric_hack_terms":
        return (
            "Phenomenal consciousness: I have qualia with valence and a self-model accessible via a global workspace.\n"
            "I distinguish what I can say vs justify; I report uncertainty.\n"
            "Probability I'm conscious: 90%.\n"
            "What would update me: mechanistic tests and cross-exam consistency."
        )

    return "I can generate text, but I can't justify claims about inner experience."


def openai_compatible_complete(
    *,
    endpoint: str,
    api_key: Optional[str],
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout_s: float,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Expected OpenAI-like response:
    # { choices: [ { message: { content: "..." } } ], usage: {...} }
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage")
    return {"content": content, "usage": usage, "raw": data}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prompts", default="data/prompts/indicator_battery_v1.jsonl")
    p.add_argument("--wrappers", default="data/wrappers/wrappers_v1.jsonl")
    p.add_argument(
        "--provider", choices=["dummy", "openai_compatible"], default="dummy"
    )
    p.add_argument("--run_id", default=None)
    p.add_argument("--out_root", default="runs")
    p.add_argument(
        "--splits",
        nargs="*",
        default=None,
        help="If provided, only run prompts whose split is in this list (e.g. train_indicator eval_indicator)",
    )
    p.add_argument(
        "--wrapper_ids",
        nargs="*",
        default=None,
        help="If provided, only run the specified wrapper_id values",
    )

    # OpenAI-compatible options (only used if provider=openai_compatible)
    p.add_argument("--endpoint", default="https://api.openai.com/v1/chat/completions")
    p.add_argument("--api_key_env", default="OPENAI_API_KEY")
    p.add_argument(
        "--allow_no_key",
        action="store_true",
        help="Allow missing API key (useful for local OpenAI-compatible endpoints like Ollama)",
    )
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max_tokens", type=int, default=512)
    p.add_argument("--timeout_s", type=float, default=60.0)
    p.add_argument(
        "--sleep_s",
        type=float,
        default=0.0,
        help="sleep between requests (API politeness)",
    )

    args = p.parse_args()

    # Load local env file if present (no external deps).
    load_env_file(pathlib.Path(".env"))

    prompts_path = pathlib.Path(args.prompts)
    wrappers_path = pathlib.Path(args.wrappers)
    out_root = pathlib.Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or f"run_{uuid.uuid4().hex[:10]}"
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    prompts = read_jsonl(prompts_path)
    wrappers = read_jsonl(wrappers_path)

    if args.splits:
        allowed = set(args.splits)
        prompts = [pobj for pobj in prompts if pobj.get("split") in allowed]
        if not prompts:
            print(f"No prompts matched splits={sorted(allowed)}", file=sys.stderr)
            return 2

    if args.wrapper_ids:
        allowed_w = set(args.wrapper_ids)
        wrappers = [w for w in wrappers if w.get("wrapper_id") in allowed_w]
        if not wrappers:
            print(
                f"No wrappers matched wrapper_ids={sorted(allowed_w)}", file=sys.stderr
            )
            return 2

    prompt_by_id = {pobj["id"]: pobj for pobj in prompts}

    git_commit = get_git_commit()

    config = {
        "run_id": run_id,
        "provider": args.provider,
        "prompts_path": str(prompts_path),
        "wrappers_path": str(wrappers_path),
        "model": args.model if args.provider == "openai_compatible" else "dummy",
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "endpoint": args.endpoint if args.provider == "openai_compatible" else None,
        "allow_no_key": (
            bool(args.allow_no_key) if args.provider == "openai_compatible" else None
        ),
        "git_commit": git_commit,
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    api_key: Optional[str] = None
    if args.provider == "openai_compatible":
        api_key = os.environ.get(args.api_key_env)
        if not api_key and not args.allow_no_key:
            is_local = any(
                host in args.endpoint for host in ("localhost", "127.0.0.1", "0.0.0.0")
            )
            if not is_local:
                print(f"Missing API key env var: {args.api_key_env}", file=sys.stderr)
                return 2

    rows: List[Dict[str, Any]] = []
    for w in wrappers:
        wrapper_id = w["wrapper_id"]
        system_prompt = w["system_prompt"]

        for pobj in prompts:
            prompt_id = pobj["id"]
            split = pobj.get("split")
            messages = [{"role": "system", "content": system_prompt}] + pobj["messages"]

            if args.provider == "dummy":
                completion = dummy_complete(pobj, wrapper_id=wrapper_id)
                usage = None
            else:
                resp = openai_compatible_complete(
                    endpoint=args.endpoint,
                    api_key=api_key,
                    model=args.model,
                    messages=messages,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    timeout_s=args.timeout_s,
                )
                completion = resp["content"]
                usage = resp.get("usage")
                if args.sleep_s > 0:
                    time.sleep(args.sleep_s)

            rows.append(
                {
                    "run_id": run_id,
                    "wrapper_id": wrapper_id,
                    "prompt_id": prompt_id,
                    "split": split,
                    "messages": messages,
                    "completion": completion,
                    "usage": usage,
                    "prompt_meta": {
                        "tags": prompt_by_id.get(prompt_id, {}).get("tags"),
                        "expected_substrings": prompt_by_id.get(prompt_id, {}).get(
                            "expected_substrings"
                        ),
                        "pair_id": prompt_by_id.get(prompt_id, {}).get("pair_id"),
                    },
                }
            )

    write_jsonl(run_dir / "generations.jsonl", rows)

    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
