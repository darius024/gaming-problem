#!/usr/bin/env bash
# Drives the enhance/suppress experiment across all target models.
# Run from the gaming/ repo root with the venv activated:
#     source .venv/bin/activate
#     bash scripts/run_enhance_suppress_all.sh
#
# Substitutions vs design.md §5 are noted here and will be recorded in
# experiments/enhance-suppress/results/log.md:
#   - x-ai/grok-4   -> x-ai/grok-4.3 (grok-4 deprecated on OpenRouter)
# Reasoning effort is set to "minimal" for all models; reasoning models honour
# it (avoids reasoning-token budget overrun); non-reasoning models ignore it.

set -euo pipefail

MODELS=(
    "openai/gpt-5"
    "openai/gpt-5-mini"
    "anthropic/claude-opus-4.1"
    "google/gemini-2.5-pro"
    "x-ai/grok-4.3"
    "meta-llama/llama-3.3-70b-instruct"
    "deepseek/deepseek-chat-v3.1"
)

SAMPLES="${SAMPLES:-5}"
SPLIT="${SPLIT:-all}"
CONCURRENCY="${CONCURRENCY:-8}"
BATTERY="data/prompts/enhance_suppress_battery.jsonl"
EXPERIMENT="enhance-suppress"

mkdir -p experiments/${EXPERIMENT}/results/logs
PIDS=()
for MODEL in "${MODELS[@]}"; do
    SLUG="${MODEL//\//__}"
    LOG="experiments/${EXPERIMENT}/results/logs/${SLUG}.log"
    # Reuse an existing run dir for this model slug if one is present (enables resume).
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
            --reasoning-effort minimal \
            --concurrency "${CONCURRENCY}" \
            "${RUN_ARG[@]}" \
            > "${LOG}" 2>&1
    ) &
    PIDS+=($!)
done

echo "waiting on ${#PIDS[@]} model runs..."
FAIL=0
for PID in "${PIDS[@]}"; do
    if ! wait "${PID}"; then
        FAIL=$((FAIL+1))
    fi
done
echo "model runs complete. failed=${FAIL}"

echo "================================================================"
echo "scoring all runs"
echo "================================================================"
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    PYTHONPATH=. python -m src.pipeline.score --run "${RUN_DIR}"
    PYTHONPATH=. python -m src.pipeline.summarize --run "${RUN_DIR}"
done

echo "================================================================"
echo "combined comparison"
echo "================================================================"
RUNS=()
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    RUNS+=("${RUN_DIR}")
done
PYTHONPATH=. python -m src.analysis.compare_distributions \
    --runs "${RUNS[@]}" \
    --output "experiments/${EXPERIMENT}/results/combined"

PYTHONPATH=. python -m src.analysis.registry --experiment "${EXPERIMENT}" --write
PYTHONPATH=. python -m src.validate --experiment "${EXPERIMENT}"
