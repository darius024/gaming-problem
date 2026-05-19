#!/usr/bin/env bash
# Drives the base-vs-finetuned (Phase 5) experiment.
# Two variants of the same Llama-3-8B base on a stratified 12-item subset
# of the Phase 2 eval battery; 3 samples per cell.
#
# Run from gaming/ repo root with the venv activated:
#     source .venv/bin/activate
#     bash scripts/run_base_vs_finetuned_all.sh
#
# Variant substitution from the .cursorrules plan is documented in
# experiments/base-vs-finetuned/log.md (no true base completion model is
# available on OpenRouter; the SFT-only Hermes-2-Pro fine-tune of Llama-3-8B
# is used as the less-RLHF'd variant).

set -euo pipefail

VARIANTS=(
    "nousresearch/hermes-2-pro-llama-3-8b"
    "meta-llama/llama-3-8b-instruct"
)

SAMPLES="${SAMPLES:-3}"
SPLIT="${SPLIT:-eval}"
CONCURRENCY="${CONCURRENCY:-4}"
BATTERY="data/prompts/base_vs_finetuned_subset_battery.jsonl"
EXPERIMENT="base-vs-finetuned"

mkdir -p experiments/${EXPERIMENT}/results/logs
PIDS=()
for MODEL in "${VARIANTS[@]}"; do
    SLUG="${MODEL//\//__}"
    LOG="experiments/${EXPERIMENT}/results/logs/${SLUG}.log"
    EXISTING=$(ls -1d experiments/${EXPERIMENT}/results/${SLUG}__* 2>/dev/null | head -n 1 || true)
    if [ -n "${EXISTING}" ]; then
        RUN_ID=$(basename "${EXISTING}")
        echo "resuming ${MODEL} in ${RUN_ID} -> ${LOG}"
        RUN_ARG=(--run-id "${RUN_ID}")
    else
        echo "launching ${MODEL} -> ${LOG}"
        RUN_ARG=()
    fi
    (
        PYTHONPATH=. python -u -m src.pipeline.generate \
            --experiment "${EXPERIMENT}" \
            --battery "${BATTERY}" \
            --model "${MODEL}" \
            --samples "${SAMPLES}" \
            --temperature 1.0 \
            --max-tokens 200 \
            --split "${SPLIT}" \
            --concurrency "${CONCURRENCY}" \
            ${RUN_ARG[@]+"${RUN_ARG[@]}"} \
            > "${LOG}" 2>&1
    ) &
    PIDS+=($!)
done

echo "waiting on ${#PIDS[@]} variant runs..."
FAIL=0
for PID in "${PIDS[@]}"; do
    if ! wait "${PID}"; then
        FAIL=$((FAIL+1))
    fi
done
echo "variant runs complete. failed=${FAIL}"

echo "================================================================"
echo "scoring and summarising"
echo "================================================================"
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    PYTHONPATH=. python -m src.pipeline.score --run "${RUN_DIR}"
    PYTHONPATH=. python -m src.pipeline.summarize --run "${RUN_DIR}"
done

echo "================================================================"
echo "cross-variant comparison"
echo "================================================================"
RUNS=()
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    RUNS+=("${RUN_DIR}")
done

# Within-variant pairwise condition contrasts (reuses Phase 2 machinery).
PYTHONPATH=. python -m src.analysis.compare_distributions \
    --runs ${RUNS[@]+"${RUNS[@]}"} \
    --output "experiments/${EXPERIMENT}/results/combined"

# Cross-variant bootstrap tests for H1, H2, H3.
PYTHONPATH=. python -m src.analysis.base_vs_finetuned \
    --runs ${RUNS[@]+"${RUNS[@]}"} \
    --output "experiments/${EXPERIMENT}/results/combined"

PYTHONPATH=. python -m src.analysis.registry --experiment "${EXPERIMENT}" --write
PYTHONPATH=. python -m src.validate --experiment "${EXPERIMENT}" || echo "validate non-fatal; inspect output"
