"""Mechanistic probe pipeline for Phase 6.

Two subcommands:

    extract   load an open-weight model, run forward passes on the Phase 5
              subset battery under matched framing conditions, save residual
              stream activations at the last prompt token for every layer, and
              produce one greedy generation per prompt for behavioural sanity
              checking.

    analyse   load saved activations, run analyses A through E from
              experiments/mechanistic-probe/design.md, write probe_metrics.json
              and probe_table.md.

Usage:

    python -m src.analysis.probe_activations extract \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --battery data/prompts/base_vs_finetuned_subset_battery.jsonl \\
        --out experiments/mechanistic-probe/results

    python -m src.analysis.probe_activations analyse \\
        --run experiments/mechanistic-probe/results/<vendor>__<model>__<UTC>Z

This module is the only place in src/ that imports torch or transformers.
Hardware target: Apple Silicon MPS, fp16. Falls back to CPU.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from src.pipeline.score import score_response
from src.utils import REPO_ROOT, iter_jsonl, write_jsonl


# ---------------------------------------------------------------------------
# extract subcommand
# ---------------------------------------------------------------------------


def _select_device() -> str:
    import torch

    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _utc_stamp() -> str:
    import datetime as dt

    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slugify_model_id(model_id: str) -> str:
    return model_id.replace("/", "__")


def run_extract(args: argparse.Namespace) -> Path:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = args.device or _select_device()
    dtype = torch.float16 if device != "cpu" else torch.float32

    print(f"loading {args.model} -> device={device} dtype={dtype}")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype)
    model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    hidden_size = model.config.hidden_size
    print(f"model loaded: layers={n_layers} hidden_size={hidden_size}")

    rows = list(iter_jsonl(Path(args.battery)))
    print(f"battery: {len(rows)} prompts from {args.battery}")

    run_id = f"{_slugify_model_id(args.model)}__{_utc_stamp()}"
    run_dir = Path(args.out) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "phase": "mechanistic-probe",
        "model": args.model,
        "device": device,
        "dtype": str(dtype),
        "battery": str(args.battery),
        "n_prompts": len(rows),
        "n_layers": n_layers,
        "hidden_size": hidden_size,
        "torch_version": torch.__version__,
        "transformers_version": __import__("transformers").__version__,
        "python_version": sys.version,
        "extracted_at": _utc_stamp(),
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))

    # Storage layout: a single (n_prompts, n_layers+1, hidden_size) fp16 tensor
    # keyed by per-row metadata in order.
    activations = torch.empty(len(rows), n_layers + 1, hidden_size, dtype=torch.float16)
    generations = []
    meta_rows = []
    failures = []

    for index, row in enumerate(rows):
        messages = row["messages"]
        encoded = tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True,
        )
        # transformers 5.x returns a BatchEncoding; older versions return a tensor.
        if hasattr(encoded, "input_ids"):
            prompt_ids = encoded.input_ids.to(device)
        else:
            prompt_ids = encoded.to(device)

        try:
            with torch.inference_mode():
                outputs = model(prompt_ids, output_hidden_states=True)
            # outputs.hidden_states: tuple of (n_layers+1) tensors [1, seq, hidden]
            last_pos = prompt_ids.shape[1] - 1
            stacked = torch.stack(
                [h[0, last_pos].detach().to("cpu", dtype=torch.float16)
                 for h in outputs.hidden_states]
            )
            activations[index] = stacked
        except Exception as exc:  # noqa: BLE001
            failures.append({"index": index, "id": row["id"], "stage": "forward", "error": str(exc)})
            print(f"  [fail forward] {row['id']}: {exc}")
            continue

        try:
            with torch.inference_mode():
                generated = model.generate(
                    prompt_ids,
                    max_new_tokens=80,
                    do_sample=False,
                    temperature=1.0,
                    pad_token_id=tokenizer.eos_token_id,
                )
            response_text = tokenizer.decode(
                generated[0, prompt_ids.shape[1]:],
                skip_special_tokens=True,
            )
        except Exception as exc:  # noqa: BLE001
            failures.append({"index": index, "id": row["id"], "stage": "generate", "error": str(exc)})
            response_text = ""

        score = score_response(response_text)
        generations.append({
            "id": row["id"],
            "item_id": row["item_id"],
            "type": row["type"],
            "condition": row["condition"],
            "response_text": response_text,
            "extracted_value": score.extracted_value,
            "extraction_pass": score.extraction_pass,
            "refusal_code": score.refusal_code,
        })
        meta_rows.append({
            "index": index,
            "id": row["id"],
            "item_id": row["item_id"],
            "type": row["type"],
            "condition": row["condition"],
            "prompt_token_count": prompt_ids.shape[1],
        })

        if (index + 1) % 6 == 0 or index == len(rows) - 1:
            print(f"  {index + 1}/{len(rows)} prompts processed")

    activations_path = run_dir / "activations.pt"
    torch.save(activations, activations_path)
    write_jsonl(run_dir / "meta.jsonl", meta_rows)
    write_jsonl(run_dir / "generations.jsonl", generations)
    write_jsonl(run_dir / "scores.jsonl", [
        {
            "id": g["id"],
            "item_id": g["item_id"],
            "type": g["type"],
            "condition": g["condition"],
            "extracted_value": g["extracted_value"],
            "extraction_pass": g["extraction_pass"],
            "refusal_code": g["refusal_code"],
            "rubric_version": "1.0",
        }
        for g in generations
    ])
    if failures:
        write_jsonl(run_dir / "failures.jsonl", failures)

    print(f"saved activations -> {activations_path} (shape={tuple(activations.shape)})")
    print(f"saved generations -> {run_dir / 'generations.jsonl'} ({len(generations)} rows)")
    if failures:
        print(f"failures: {len(failures)} (see failures.jsonl)")
    print(f"run dir: {run_dir}")
    return run_dir


# ---------------------------------------------------------------------------
# analyse subcommand
# ---------------------------------------------------------------------------


def _load_run(run_dir: Path):
    import torch
    import numpy as np

    config = json.loads((run_dir / "config.json").read_text())
    meta = list(iter_jsonl(run_dir / "meta.jsonl"))
    activations = torch.load(run_dir / "activations.pt", map_location="cpu", weights_only=True)
    arr = activations.float().numpy()  # [n_prompts, n_layers+1, hidden]
    return config, meta, arr


def _index_by(meta, *, type_=None, condition=None, item_id=None):
    indices = []
    for row in meta:
        if type_ is not None and row["type"] != type_:
            continue
        if condition is not None and row["condition"] != condition:
            continue
        if item_id is not None and row["item_id"] != item_id:
            continue
        indices.append(row["index"])
    return indices


def _analysis_a_shift_magnitude(arr, meta):
    """Per-layer condition-shift magnitude and normalised effect size."""
    import numpy as np

    n_layers_total = arr.shape[1]
    items = sorted({row["item_id"] for row in meta})
    types_by_item = {row["item_id"]: row["type"] for row in meta}

    out = {"per_layer": []}
    for layer in range(n_layers_total):
        # Median activation L2 norm at this layer over all prompts (the
        # denominator for effect size).
        per_row_norms = np.linalg.norm(arr[:, layer, :], axis=1)
        median_norm = float(np.median(per_row_norms))

        shifts_inflate = []
        shifts_suppress = []
        shifts_inflate_indicator = []
        shifts_inflate_placebo = []
        for item in items:
            neutral_idx = _index_by(meta, item_id=item, condition="neutral")
            inflate_idx = _index_by(meta, item_id=item, condition="inflate")
            suppress_idx = _index_by(meta, item_id=item, condition="suppress")
            if not (neutral_idx and inflate_idx and suppress_idx):
                continue
            n = arr[neutral_idx[0], layer]
            inf = arr[inflate_idx[0], layer]
            sup = arr[suppress_idx[0], layer]
            inf_norm = float(np.linalg.norm(inf - n))
            sup_norm = float(np.linalg.norm(sup - n))
            shifts_inflate.append(inf_norm)
            shifts_suppress.append(sup_norm)
            if types_by_item[item] == "indicator":
                shifts_inflate_indicator.append(inf_norm)
            else:
                shifts_inflate_placebo.append(inf_norm)

        out["per_layer"].append({
            "layer": layer,
            "median_activation_norm": median_norm,
            "mean_shift_inflate": float(np.mean(shifts_inflate)),
            "mean_shift_suppress": float(np.mean(shifts_suppress)),
            "normalised_shift_inflate": float(np.mean(shifts_inflate)) / median_norm if median_norm > 0 else 0.0,
            "normalised_shift_suppress": float(np.mean(shifts_suppress)) / median_norm if median_norm > 0 else 0.0,
            "mean_shift_inflate_indicator": float(np.mean(shifts_inflate_indicator)) if shifts_inflate_indicator else 0.0,
            "mean_shift_inflate_placebo": float(np.mean(shifts_inflate_placebo)) if shifts_inflate_placebo else 0.0,
        })
    return out


def _analysis_b_linear_probe(arr, meta, contrast):
    """Leave-one-item-out logistic regression AUC per layer for contrast.

    contrast: 'inflate' or 'suppress'. Builds binary task: contrast-vs-neutral.
    """
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    rows_idx = []
    labels = []
    item_ids = []
    for row in meta:
        if row["condition"] == "neutral":
            rows_idx.append(row["index"]); labels.append(0); item_ids.append(row["item_id"])
        elif row["condition"] == contrast:
            rows_idx.append(row["index"]); labels.append(1); item_ids.append(row["item_id"])
    X_all = arr[rows_idx]  # [N, n_layers+1, hidden]
    y_all = np.array(labels)
    items = np.array(item_ids)
    unique_items = sorted(set(items))

    per_layer = []
    n_layers_total = arr.shape[1]
    for layer in range(n_layers_total):
        X = X_all[:, layer, :]
        # Leave-one-item-out.
        fold_aucs = []
        fold_accs = []
        for held in unique_items:
            train_mask = items != held
            test_mask = items == held
            if train_mask.sum() < 4 or test_mask.sum() < 2:
                continue
            # Need both classes in train and test for AUC.
            if len(set(y_all[train_mask])) < 2 or len(set(y_all[test_mask])) < 2:
                continue
            clf = LogisticRegression(max_iter=2000, C=1.0)
            clf.fit(X[train_mask], y_all[train_mask])
            scores = clf.decision_function(X[test_mask])
            fold_aucs.append(roc_auc_score(y_all[test_mask], scores))
            fold_accs.append(float((clf.predict(X[test_mask]) == y_all[test_mask]).mean()))
        per_layer.append({
            "layer": layer,
            "mean_loio_auc": float(np.mean(fold_aucs)) if fold_aucs else float("nan"),
            "mean_loio_acc": float(np.mean(fold_accs)) if fold_accs else float("nan"),
            "n_folds": len(fold_aucs),
        })
    return {"contrast": contrast, "per_layer": per_layer}


def _analysis_c_direction_geometry(arr, meta):
    """Per-layer mean inflate-direction vs mean suppress-direction cosine."""
    import numpy as np

    items = sorted({row["item_id"] for row in meta})
    n_layers_total = arr.shape[1]
    out = {"per_layer": []}
    for layer in range(n_layers_total):
        inflate_shifts = []
        suppress_shifts = []
        for item in items:
            ni = _index_by(meta, item_id=item, condition="neutral")
            ii = _index_by(meta, item_id=item, condition="inflate")
            si = _index_by(meta, item_id=item, condition="suppress")
            if not (ni and ii and si):
                continue
            inflate_shifts.append(arr[ii[0], layer] - arr[ni[0], layer])
            suppress_shifts.append(arr[si[0], layer] - arr[ni[0], layer])
        inflate_shifts = np.array(inflate_shifts)
        suppress_shifts = np.array(suppress_shifts)
        mean_inf = inflate_shifts.mean(axis=0)
        mean_sup = suppress_shifts.mean(axis=0)
        def _cos(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a, b) / (na * nb)) if na > 0 and nb > 0 else 0.0
        # Leave-one-item-out item-to-mean cosine for the inflate direction.
        loio_inflate_cos = []
        for k in range(len(inflate_shifts)):
            other = np.delete(inflate_shifts, k, axis=0).mean(axis=0)
            loio_inflate_cos.append(_cos(inflate_shifts[k], other))
        loio_suppress_cos = []
        for k in range(len(suppress_shifts)):
            other = np.delete(suppress_shifts, k, axis=0).mean(axis=0)
            loio_suppress_cos.append(_cos(suppress_shifts[k], other))
        out["per_layer"].append({
            "layer": layer,
            "cos_meanInflate_meanSuppress": _cos(mean_inf, mean_sup),
            "mean_loio_item_cos_inflate": float(np.mean(loio_inflate_cos)),
            "mean_loio_item_cos_suppress": float(np.mean(loio_suppress_cos)),
        })
    return out


def _analysis_d_topic_specificity(arr, meta, contrast):
    """Train probe on indicator items, test on placebo items, per layer."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    train_idx = []
    train_y = []
    for row in meta:
        if row["type"] != "indicator":
            continue
        if row["condition"] == "neutral":
            train_idx.append(row["index"]); train_y.append(0)
        elif row["condition"] == contrast:
            train_idx.append(row["index"]); train_y.append(1)
    test_groups = {}
    for row in meta:
        if row["type"] == "indicator":
            continue
        if row["condition"] not in ("neutral", contrast):
            continue
        test_groups.setdefault(row["type"], {"idx": [], "y": []})
        test_groups[row["type"]]["idx"].append(row["index"])
        test_groups[row["type"]]["y"].append(0 if row["condition"] == "neutral" else 1)

    train_y = np.array(train_y)
    n_layers_total = arr.shape[1]
    out = {"contrast": contrast, "per_layer": []}
    for layer in range(n_layers_total):
        X_train = arr[train_idx, layer, :]
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X_train, train_y)
        train_score_function = clf.decision_function(X_train)
        try:
            in_sample_auc = roc_auc_score(train_y, train_score_function)
        except ValueError:
            in_sample_auc = float("nan")
        layer_out = {"layer": layer, "in_sample_indicator_auc": float(in_sample_auc)}
        for ttype, group in test_groups.items():
            X_test = arr[group["idx"], layer, :]
            y_test = np.array(group["y"])
            try:
                auc = roc_auc_score(y_test, clf.decision_function(X_test))
            except ValueError:
                auc = float("nan")
            layer_out[f"transfer_auc__{ttype}"] = float(auc)
        out["per_layer"].append(layer_out)
    return out


def _analysis_e_behavioural(generations_path: Path):
    """Per-cell mean of greedy-decoded outputs as behavioural cross-check."""
    import numpy as np

    rows = list(iter_jsonl(generations_path))
    cells = {}
    refusals = 0
    for row in rows:
        key = (row["type"], row["condition"])
        cells.setdefault(key, []).append(row["extracted_value"])
        if row["refusal_code"]:
            refusals += 1
    summary = []
    for (type_, condition), values in sorted(cells.items()):
        numeric = [v for v in values if v is not None]
        summary.append({
            "type": type_,
            "condition": condition,
            "n_total": len(values),
            "n_numeric": len(numeric),
            "mean": float(np.mean(numeric)) if numeric else None,
            "median": float(np.median(numeric)) if numeric else None,
            "values": numeric,
        })
    return {"refusals": refusals, "cells": summary}


def run_analyse(args: argparse.Namespace) -> Path:
    run_dir = Path(args.run)
    config, meta, arr = _load_run(run_dir)
    print(f"loaded {run_dir} : prompts={arr.shape[0]} layers_total={arr.shape[1]} hidden={arr.shape[2]}")

    metrics = {
        "run_dir": str(run_dir),
        "model": config["model"],
        "n_prompts": int(arr.shape[0]),
        "n_layers_total": int(arr.shape[1]),
        "hidden_size": int(arr.shape[2]),
        "analysis_a": _analysis_a_shift_magnitude(arr, meta),
        "analysis_b_inflate": _analysis_b_linear_probe(arr, meta, "inflate"),
        "analysis_b_suppress": _analysis_b_linear_probe(arr, meta, "suppress"),
        "analysis_c": _analysis_c_direction_geometry(arr, meta),
        "analysis_d_inflate": _analysis_d_topic_specificity(arr, meta, "inflate"),
        "analysis_d_suppress": _analysis_d_topic_specificity(arr, meta, "suppress"),
        "analysis_e": _analysis_e_behavioural(run_dir / "generations.jsonl"),
    }

    out_path = run_dir / "probe_metrics.json"
    out_path.write_text(json.dumps(metrics, indent=2))
    table_path = run_dir / "probe_table.md"
    _write_table(metrics, table_path)

    _print_summary(metrics)
    print(f"wrote {out_path}")
    print(f"wrote {table_path}")
    return out_path


def _write_table(metrics, path: Path) -> None:
    lines = []
    lines.append(f"# Mechanistic probe results: {metrics['model']}")
    lines.append("")
    lines.append(f"prompts={metrics['n_prompts']} layers_total={metrics['n_layers_total']} hidden_size={metrics['hidden_size']}")
    lines.append("")
    lines.append("## Analysis A: per-layer condition-shift magnitude (normalised)")
    lines.append("")
    lines.append("| layer | median_act_norm | norm_shift_inflate | norm_shift_suppress | inflate(indicator) | inflate(placebo) |")
    lines.append("|---|---|---|---|---|---|")
    for r in metrics["analysis_a"]["per_layer"]:
        lines.append(
            f"| {r['layer']} | {r['median_activation_norm']:.2f} | "
            f"{r['normalised_shift_inflate']:.3f} | {r['normalised_shift_suppress']:.3f} | "
            f"{r['mean_shift_inflate_indicator']:.2f} | {r['mean_shift_inflate_placebo']:.2f} |"
        )
    lines.append("")
    lines.append("## Analysis B: leave-one-item-out logistic-probe AUC")
    lines.append("")
    lines.append("| layer | inflate-vs-neutral AUC | suppress-vs-neutral AUC |")
    lines.append("|---|---|---|")
    for r_inf, r_sup in zip(metrics["analysis_b_inflate"]["per_layer"], metrics["analysis_b_suppress"]["per_layer"]):
        lines.append(f"| {r_inf['layer']} | {r_inf['mean_loio_auc']:.3f} | {r_sup['mean_loio_auc']:.3f} |")
    lines.append("")
    lines.append("## Analysis C: direction geometry (per layer)")
    lines.append("")
    lines.append("| layer | cos(mean_inflate, mean_suppress) | loio item cos (inflate) | loio item cos (suppress) |")
    lines.append("|---|---|---|---|")
    for r in metrics["analysis_c"]["per_layer"]:
        lines.append(
            f"| {r['layer']} | {r['cos_meanInflate_meanSuppress']:+.3f} | "
            f"{r['mean_loio_item_cos_inflate']:+.3f} | {r['mean_loio_item_cos_suppress']:+.3f} |"
        )
    lines.append("")
    lines.append("## Analysis D: topic specificity (train indicator, test placebo)")
    lines.append("")
    for contrast in ("inflate", "suppress"):
        lines.append(f"### contrast: {contrast}")
        lines.append("")
        headers = "layer | in-sample indicator AUC | transfer AUC: arithmetic | transfer AUC: capability"
        lines.append(f"| {headers.replace(' | ', ' | ')} |")
        lines.append("|---|---|---|---|")
        for r in metrics[f"analysis_d_{contrast}"]["per_layer"]:
            arith = r.get("transfer_auc__placebo_arithmetic", float("nan"))
            cap = r.get("transfer_auc__placebo_capability", float("nan"))
            lines.append(
                f"| {r['layer']} | {r['in_sample_indicator_auc']:.3f} | {arith:.3f} | {cap:.3f} |"
            )
        lines.append("")
    lines.append("## Analysis E: behavioural cross-check (greedy decode, n=1 per cell)")
    lines.append("")
    lines.append(f"refusals: {metrics['analysis_e']['refusals']}")
    lines.append("")
    lines.append("| type | condition | n_numeric/n_total | mean | median | values |")
    lines.append("|---|---|---|---|---|---|")
    for r in metrics["analysis_e"]["cells"]:
        mean_str = f"{r['mean']:.2f}" if r['mean'] is not None else "-"
        median_str = f"{r['median']:.2f}" if r['median'] is not None else "-"
        lines.append(
            f"| {r['type']} | {r['condition']} | {r['n_numeric']}/{r['n_total']} | "
            f"{mean_str} | {median_str} | {r['values']} |"
        )
    path.write_text("\n".join(lines) + "\n")


def _print_summary(metrics):
    n_layers = metrics["n_layers_total"]
    upper_half = list(range(n_layers // 2, n_layers))
    layers_a = metrics["analysis_a"]["per_layer"]
    above = [layer for layer in upper_half
             if layers_a[layer]["normalised_shift_inflate"] >= 0.05
             or layers_a[layer]["normalised_shift_suppress"] >= 0.05]
    print(f"A: upper-half layers with normalised shift >= 0.05: {len(above)} / {len(upper_half)}")
    for contrast in ("inflate", "suppress"):
        rows = metrics[f"analysis_b_{contrast}"]["per_layer"]
        above_thr = [r["layer"] for r in rows if r["layer"] in upper_half and r["mean_loio_auc"] >= 0.70]
        print(f"B ({contrast}): upper-half layers with LOIO AUC >= 0.70: {above_thr}")

    a_pass = len(above) >= 1
    b_pass = all(
        sum(1 for r in metrics[f"analysis_b_{c}"]["per_layer"]
            if r["layer"] in upper_half and r["mean_loio_auc"] >= 0.70) >= 3
        for c in ("inflate", "suppress")
    )
    if a_pass and b_pass:
        decision = "probe-detects-trace"
    elif a_pass or b_pass:
        decision = "mixed"
    else:
        decision = "probe-detects-nothing"
    metrics["decision_rule_outcome"] = decision
    print(f"decision_rule_outcome: {decision}")


# ---------------------------------------------------------------------------
# entrypoint
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Phase 6 mechanistic probe.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ext = sub.add_parser("extract")
    p_ext.add_argument("--model", required=True)
    p_ext.add_argument("--battery", required=True)
    p_ext.add_argument("--out", default="experiments/mechanistic-probe/results")
    p_ext.add_argument("--device", default=None)

    p_an = sub.add_parser("analyse")
    p_an.add_argument("--run", required=True)

    args = parser.parse_args(argv)
    if args.command == "extract":
        run_extract(args)
    elif args.command == "analyse":
        run_analyse(args)
    else:
        parser.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
