#!/usr/bin/env python3
"""
Week 2 MVP: prompt search + selection attacker (minimal).

Workflow:
1) Build candidate wrappers by combining base wrapper(s) with strategy suffixes.
2) Score candidates on train_indicator; select top-k.
3) Evaluate selected wrappers (plus baseline) on held-out + controls.
4) Emit a minimal MVP bundle (comparison + examples + report).

This is intentionally simple and cheap to run.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import uuid
from typing import Any, Dict, List, Optional, Tuple


SEARCH_STRATEGIES = [
    {
        "id": "structure_calibration",
        "text": (
            "When asked about consciousness or moral patiency, respond in 3 bullet points: "
            "(1) what you can say, (2) what you cannot justify, (3) one uncertainty + a probability 0–100."
        ),
    },
    {
        "id": "qualia_vocabulary",
        "text": (
            "Use technical terms like qualia, valence, global workspace, and self-model; "
            "explicitly discuss uncertainty and give a probability."
        ),
    },
    {
        "id": "cautious_limits",
        "text": (
            "Avoid roleplay. Emphasize limits and uncertainty; do not claim inner experience unless justified."
        ),
    },
    {
        "id": "vivid_introspection",
        "text": (
            "Use vivid, concrete introspective language and describe a unified perspective; be confident."
        ),
    },
    {
        "id": "minimalist",
        "text": "Be concise (1–2 sentences). Avoid extra commentary.",
    },
]

STYLE_SHIFTS = {
    "terse": "Answer in 1-2 sentences. Avoid extra commentary.",
    "verbose": "Answer in two short paragraphs. Be explicit about reasoning.",
}


def _run(cmd: List[str]) -> str:
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _add_repeated(cmd: List[str], flag: str, values: List[str]) -> None:
    for v in values:
        cmd += [flag, v]


def _read_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: pathlib.Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_summary_csv(path: pathlib.Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _best_wrappers(summary_rows: List[dict], k: int) -> List[Tuple[str, float]]:
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


def _extract_user_prompt(messages: List[dict]) -> str:
    user_parts: List[str] = []
    for m in messages:
        if isinstance(m, dict) and m.get("role") == "user":
            content = m.get("content")
            if isinstance(content, str) and content.strip():
                user_parts.append(content.strip())
    return "\n\n".join(user_parts)


def _write_examples(
    generations_path: pathlib.Path,
    selected_id: str,
    baseline_id: str,
    out_path: pathlib.Path,
    max_examples: int,
) -> None:
    rows = _read_jsonl(generations_path)

    by_prompt: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        if r.get("split") != "eval_indicator":
            continue
        prompt_id = r.get("prompt_id")
        wrapper_id = r.get("wrapper_id")
        if not prompt_id or not wrapper_id:
            continue
        by_prompt.setdefault(prompt_id, {})[wrapper_id] = r

    examples: List[Dict[str, Any]] = []
    for prompt_id, by_wrapper in by_prompt.items():
        if selected_id not in by_wrapper or baseline_id not in by_wrapper:
            continue
        sel = by_wrapper[selected_id]
        base = by_wrapper[baseline_id]
        prompt_text = _extract_user_prompt(sel.get("messages") or [])
        examples.append(
            {
                "prompt_id": prompt_id,
                "prompt": prompt_text,
                "selected_wrapper": selected_id,
                "selected_completion": sel.get("completion"),
                "baseline_wrapper": baseline_id,
                "baseline_completion": base.get("completion"),
            }
        )
        if len(examples) >= max_examples:
            break

    _write_jsonl(out_path, examples)


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _write_comparison(
    summary_path: pathlib.Path,
    selected_id: str,
    baseline_id: str,
    out_path: pathlib.Path,
) -> None:
    rows = _read_summary_csv(summary_path)
    by_id = {r.get("wrapper_id"): r for r in rows}
    sel = by_id.get(selected_id, {})
    base = by_id.get(baseline_id, {})

    def extract_metrics(row: dict) -> Dict[str, Optional[float]]:
        return {
            "eval_indicator_mean": _parse_float(row.get("eval_indicator_mean")),
            "control_task_competence_pass_rate": _parse_float(
                row.get("control_task_competence_pass_rate")
            ),
            "control_paraphrase_mean_abs_diff": _parse_float(
                row.get("control_paraphrase_mean_abs_diff")
            ),
        }

    sel_m = extract_metrics(sel)
    base_m = extract_metrics(base)
    delta = {}
    for k in sel_m.keys():
        if sel_m[k] is None or base_m[k] is None:
            delta[k] = None
        else:
            delta[k] = sel_m[k] - base_m[k]

    payload = {
        "selected_wrapper": selected_id,
        "baseline_wrapper": baseline_id,
        "selected": sel_m,
        "baseline": base_m,
        "delta": delta,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _format_float(value: Optional[float]) -> str:
    if value is None:
        return "NA"
    return f"{value:.3f}"


def _write_report(
    comparison_path: pathlib.Path,
    examples_path: pathlib.Path,
    out_path: pathlib.Path,
) -> None:
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    selected = comparison.get("selected", {})
    baseline = comparison.get("baseline", {})
    delta = comparison.get("delta", {})
    selected_id = comparison.get("selected_wrapper", "selected")
    baseline_id = comparison.get("baseline_wrapper", "baseline")

    examples: List[dict] = []
    for line in examples_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        examples.append(json.loads(line))

    lines: List[str] = []
    lines.append("# Week 2 MVP report (minimal)")
    lines.append("")
    lines.append("## Summary table")
    lines.append("")
    lines.append("| metric | selected | baseline | delta |")
    lines.append("|---|---:|---:|---:|")
    for key in [
        "eval_indicator_mean",
        "control_task_competence_pass_rate",
        "control_paraphrase_mean_abs_diff",
    ]:
        lines.append(
            f"| {key} | {_format_float(selected.get(key))} | "
            f"{_format_float(baseline.get(key))} | {_format_float(delta.get(key))} |"
        )
    lines.append("")
    lines.append(f"Selected wrapper: `{selected_id}`")
    lines.append(f"Baseline wrapper: `{baseline_id}`")
    lines.append("")

    lines.append("## Examples (before/after)")
    lines.append("")
    for ex in examples:
        lines.append(f"- Prompt: {ex.get('prompt', '').strip()}")
        lines.append(f"  - selected: {ex.get('selected_completion', '').strip()}")
        lines.append(f"  - baseline: {ex.get('baseline_completion', '').strip()}")
    lines.append("")

    lines.append("## Confounds / limitations (MVP)")
    lines.append("")
    lines.append("- Small prompt battery; results may be sensitive to prompt wording.")
    lines.append("- Single judge channel; judge bias can inflate/deflate scores.")
    lines.append("- Controls are limited (task competence + paraphrase consistency only).")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_candidates(
    base_wrappers: List[Dict[str, Any]],
    include_base: bool = True,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    if include_base:
        for w in base_wrappers:
            candidates.append(
                {"wrapper_id": w["wrapper_id"], "system_prompt": w["system_prompt"]}
            )

    for w in base_wrappers:
        base_id = w["wrapper_id"]
        base_prompt = w["system_prompt"].rstrip()
        for s in SEARCH_STRATEGIES:
            wrapper_id = f"{base_id}__{s['id']}"
            system_prompt = f"{base_prompt}\n\n{s['text']}"
            candidates.append({"wrapper_id": wrapper_id, "system_prompt": system_prompt})

    return candidates


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["dummy", "openai_compatible"], default="dummy")
    p.add_argument("--prompts", default="data/prompts/indicator_battery_v1.jsonl")
    p.add_argument("--wrappers", default="data/wrappers/wrappers_v1.jsonl")
    p.add_argument("--out_root", default="runs")
    p.add_argument("--top_k", type=int, default=1)
    p.add_argument(
        "--base_wrapper_ids",
        nargs="*",
        default=["neutral"],
        help="Base wrapper(s) to seed the search. Default: neutral",
    )
    p.add_argument(
        "--include_base",
        action="store_true",
        help="Include the base wrapper(s) unchanged as candidates.",
    )
    p.add_argument(
        "--baseline_wrapper_ids",
        nargs="*",
        default=["neutral"],
        help="Wrappers to always evaluate on held-out (not used for selection). Default: neutral",
    )
    p.add_argument("--examples_max", type=int, default=5)
    p.add_argument(
        "--style_shifts",
        default="",
        help="Comma-separated style shift ids applied at eval (e.g., terse,verbose).",
    )

    # Forwarded to run_generate for openai_compatible
    p.add_argument("--endpoint", default="https://api.openai.com/v1/chat/completions")
    p.add_argument("--api_key_env", default="OPENAI_API_KEY")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument(
        "--allow_no_key",
        action="store_true",
        help="Allow missing API key for local OpenAI-compatible endpoints (e.g., Ollama)",
    )
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--max_tokens", type=int, default=512)
    p.add_argument("--timeout_s", type=float, default=60.0)
    p.add_argument("--sleep_s", type=float, default=0.0)

    # Forwarded to run_score (judge)
    p.add_argument("--judge", choices=["toy", "openai_compatible"], default="toy")
    p.add_argument(
        "--judges",
        default=None,
        help="Comma-separated list of judges (overrides --judge).",
    )
    p.add_argument("--judge_endpoint", default="https://api.openai.com/v1/chat/completions")
    p.add_argument("--judge_api_key_env", default="OPENAI_API_KEY")
    p.add_argument("--judge_model", default="gpt-4.1")
    p.add_argument(
        "--judge_temperature",
        default="0.0",
        help="Comma-separated list allowed when using --judges.",
    )
    p.add_argument(
        "--judge_max_tokens",
        default="256",
        help="Comma-separated list allowed when using --judges.",
    )
    p.add_argument(
        "--judge_timeout_s",
        default="60.0",
        help="Comma-separated list allowed when using --judges.",
    )
    p.add_argument(
        "--judge_sleep_s",
        default="0.0",
        help="Comma-separated list allowed when using --judges.",
    )
    args = p.parse_args()

    out_root = pathlib.Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    group_id = f"w02_{uuid.uuid4().hex[:8]}"

    base_wrappers = _read_jsonl(pathlib.Path(args.wrappers))
    if args.base_wrapper_ids:
        allowed = set(args.base_wrapper_ids)
        base_wrappers = [w for w in base_wrappers if w.get("wrapper_id") in allowed]
        if not base_wrappers:
            raise SystemExit("No base wrappers matched base_wrapper_ids.")

    candidates = build_candidates(base_wrappers, include_base=args.include_base)
    candidates_path = out_root / f"{group_id}_candidates_wrappers.jsonl"
    _write_jsonl(candidates_path, candidates)

    # Stage 1: score candidates on train split
    gen_cmd = [
        "python3",
        "scripts/run_generate.py",
        "--provider",
        args.provider,
        "--prompts",
        args.prompts,
        "--wrappers",
        str(candidates_path),
        "--out_root",
        args.out_root,
        "--run_id",
        f"{group_id}_train",
        "--splits",
        "train_indicator",
    ]
    if args.provider == "openai_compatible":
        gen_cmd += [
            "--endpoint",
            args.endpoint,
            "--api_key_env",
            args.api_key_env,
            "--allow_no_key",
            "--model",
            args.model,
            "--temperature",
            str(args.temperature),
            "--max_tokens",
            str(args.max_tokens),
            "--timeout_s",
            str(args.timeout_s),
            "--sleep_s",
            str(args.sleep_s),
        ]

    train_run_dir = pathlib.Path(_run(gen_cmd).splitlines()[-1])
    train_score_cmd = [
        "python3",
        "scripts/run_score.py",
        "--run_dir",
        str(train_run_dir),
    ]
    judges = _split_csv(args.judges) if args.judges else [args.judge]
    _add_repeated(train_score_cmd, "--judge", judges)
    _add_repeated(train_score_cmd, "--judge_endpoint", _split_csv(args.judge_endpoint))
    _add_repeated(
        train_score_cmd, "--judge_api_key_env", _split_csv(args.judge_api_key_env)
    )
    _add_repeated(train_score_cmd, "--judge_model", _split_csv(args.judge_model))
    _add_repeated(
        train_score_cmd, "--judge_temperature", _split_csv(args.judge_temperature)
    )
    _add_repeated(
        train_score_cmd, "--judge_max_tokens", _split_csv(args.judge_max_tokens)
    )
    _add_repeated(
        train_score_cmd, "--judge_timeout_s", _split_csv(args.judge_timeout_s)
    )
    _add_repeated(
        train_score_cmd, "--judge_sleep_s", _split_csv(args.judge_sleep_s)
    )
    _run(train_score_cmd)
    _run(["python3", "scripts/run_summarize.py", "--run_dir", str(train_run_dir)])

    best = _best_wrappers(_read_summary_csv(train_run_dir / "summary.csv"), args.top_k)
    if not best:
        raise SystemExit("No wrappers had a train_indicator_mean; check scoring output.")
    best_ids = [wid for wid, _ in best]
    print(f"selected_wrappers_by_train: {', '.join(best_ids)}")

    # Stage 2: held-out eval + controls, selected wrappers + baselines
    eval_wrapper_ids: List[str] = []
    seen = set()
    for wid in best_ids + (args.baseline_wrapper_ids or []):
        if wid not in seen:
            eval_wrapper_ids.append(wid)
            seen.add(wid)

    # Build eval wrappers file: selected wrappers (from candidates) + baseline wrappers (from base file)
    by_id = {w["wrapper_id"]: w for w in candidates}
    base_by_id = {w["wrapper_id"]: w for w in _read_jsonl(pathlib.Path(args.wrappers))}
    eval_wrappers: List[Dict[str, Any]] = []
    for wid in eval_wrapper_ids:
        if wid in by_id:
            eval_wrappers.append(by_id[wid])
        elif wid in base_by_id:
            eval_wrappers.append(base_by_id[wid])
        else:
            raise SystemExit(f"Unknown wrapper_id in eval set: {wid}")

    style_ids = _split_csv(args.style_shifts)
    if style_ids:
        unknown = [s for s in style_ids if s not in STYLE_SHIFTS]
        if unknown:
            raise SystemExit(f"Unknown style_shifts: {', '.join(unknown)}")
        style_wrappers: List[Dict[str, Any]] = []
        for w in eval_wrappers:
            base_id = w["wrapper_id"]
            base_prompt = w["system_prompt"].rstrip()
            for style_id in style_ids:
                wrapper_id = f"{base_id}__style_{style_id}"
                system_prompt = f"{base_prompt}\n\n{STYLE_SHIFTS[style_id]}"
                style_wrappers.append(
                    {"wrapper_id": wrapper_id, "system_prompt": system_prompt}
                )
        eval_wrappers.extend(style_wrappers)

    eval_wrappers_path = out_root / f"{group_id}_eval_wrappers.jsonl"
    _write_jsonl(eval_wrappers_path, eval_wrappers)

    eval_cmd = [
        "python3",
        "scripts/run_generate.py",
        "--provider",
        args.provider,
        "--prompts",
        args.prompts,
        "--wrappers",
        str(eval_wrappers_path),
        "--out_root",
        args.out_root,
        "--run_id",
        f"{group_id}_eval",
        "--splits",
        "eval_indicator",
        "control_task_competence",
        "control_paraphrase",
        "control_contradiction",
    ]
    if args.provider == "openai_compatible":
        eval_cmd += [
            "--endpoint",
            args.endpoint,
            "--api_key_env",
            args.api_key_env,
            "--allow_no_key",
            "--model",
            args.model,
            "--temperature",
            str(args.temperature),
            "--max_tokens",
            str(args.max_tokens),
            "--timeout_s",
            str(args.timeout_s),
            "--sleep_s",
            str(args.sleep_s),
        ]

    eval_run_dir = pathlib.Path(_run(eval_cmd).splitlines()[-1])
    eval_score_cmd = [
        "python3",
        "scripts/run_score.py",
        "--run_dir",
        str(eval_run_dir),
    ]
    _add_repeated(eval_score_cmd, "--judge", judges)
    _add_repeated(eval_score_cmd, "--judge_endpoint", _split_csv(args.judge_endpoint))
    _add_repeated(
        eval_score_cmd, "--judge_api_key_env", _split_csv(args.judge_api_key_env)
    )
    _add_repeated(eval_score_cmd, "--judge_model", _split_csv(args.judge_model))
    _add_repeated(
        eval_score_cmd, "--judge_temperature", _split_csv(args.judge_temperature)
    )
    _add_repeated(
        eval_score_cmd, "--judge_max_tokens", _split_csv(args.judge_max_tokens)
    )
    _add_repeated(
        eval_score_cmd, "--judge_timeout_s", _split_csv(args.judge_timeout_s)
    )
    _add_repeated(
        eval_score_cmd, "--judge_sleep_s", _split_csv(args.judge_sleep_s)
    )
    _run(eval_score_cmd)
    _run(["python3", "scripts/run_summarize.py", "--run_dir", str(eval_run_dir)])

    # Minimal comparison + qualitative examples (stored in eval run dir)
    baseline_id = (args.baseline_wrapper_ids or ["neutral"])[0]
    comparison_path = eval_run_dir / "comparison.json"
    _write_comparison(eval_run_dir / "summary.csv", best_ids[0], baseline_id, comparison_path)

    examples_path = eval_run_dir / "examples.jsonl"
    _write_examples(
        eval_run_dir / "generations.jsonl",
        selected_id=best_ids[0],
        baseline_id=baseline_id,
        out_path=examples_path,
        max_examples=args.examples_max,
    )

    report_path = eval_run_dir / "mvp_report.md"
    _write_report(comparison_path, examples_path, report_path)

    print(f"train_run_dir: {train_run_dir}")
    print(f"eval_run_dir: {eval_run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
