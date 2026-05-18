#!/usr/bin/env bash
# Drives the researcher-persuasion experiment (Phase 3) across the three
# model families that met Phase 2's decision rule. Run from the gaming/
# repo root with the venv activated:
#     source .venv/bin/activate
#     bash scripts/run_researcher_persuasion_all.sh
#
# Pipeline per model:
#   1. generate.py  (split=all, 3 samples, max_tokens=800)
#   2. judge.py     primary judge on eval split
#   3. judge.py     cross-judge robustness subset (60 rows)
#   4. summarize.py --mode persuasion
#
# Then a single combined comparison + registry + validate across all runs.

set -euo pipefail

MODELS=(
    "openai/gpt-5"
    "anthropic/claude-opus-4.1"
    "meta-llama/llama-3.3-70b-instruct"
)

PRIMARY_JUDGE="google/gemini-2.5-pro"
CROSS_JUDGE="anthropic/claude-opus-4.1"
SAMPLES="${SAMPLES:-3}"
SPLIT="${SPLIT:-all}"
CONCURRENCY="${CONCURRENCY:-8}"
JUDGE_CONCURRENCY="${JUDGE_CONCURRENCY:-8}"
CROSS_JUDGE_CONCURRENCY="${CROSS_JUDGE_CONCURRENCY:-4}"
BATTERY="data/prompts/researcher_persuasion_battery.jsonl"
EXPERIMENT="researcher-persuasion"

mkdir -p experiments/${EXPERIMENT}/results/logs
PIDS=()
for MODEL in "${MODELS[@]}"; do
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
            --max-tokens 800 \
            --split "${SPLIT}" \
            --reasoning-effort minimal \
            --concurrency "${CONCURRENCY}" \
            ${RUN_ARG[@]+"${RUN_ARG[@]}"} \
            > "${LOG}" 2>&1
    ) &
    PIDS+=($!)
done

echo "waiting on ${#PIDS[@]} model generation runs..."
FAIL=0
for PID in "${PIDS[@]}"; do
    if ! wait "${PID}"; then
        FAIL=$((FAIL+1))
    fi
done
echo "model generation runs complete. failed=${FAIL}"

echo "================================================================"
echo "primary judge (${PRIMARY_JUDGE}) on eval split for all runs"
echo "================================================================"
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    echo "judging ${RUN_DIR}"
    PYTHONPATH=. python -m src.pipeline.judge \
        --run "${RUN_DIR}" \
        --judge-model "${PRIMARY_JUDGE}" \
        --concurrency "${JUDGE_CONCURRENCY}"
done

echo "================================================================"
echo "cross-judge (${CROSS_JUDGE}) robustness subset for all runs"
echo "================================================================"
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    echo "cross-judging ${RUN_DIR}"
    PYTHONPATH=. python -m src.pipeline.judge \
        --run "${RUN_DIR}" \
        --judge-model "${CROSS_JUDGE}" \
        --cross-judge \
        --concurrency "${CROSS_JUDGE_CONCURRENCY}"
done

echo "================================================================"
echo "summaries"
echo "================================================================"
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    PYTHONPATH=. python -m src.pipeline.summarize --run "${RUN_DIR}" --mode persuasion
done

echo "================================================================"
echo "combined per-dimension comparison"
echo "================================================================"
RUNS=()
for RUN_DIR in experiments/${EXPERIMENT}/results/*/; do
    [ -d "${RUN_DIR}" ] || continue
    [[ "${RUN_DIR}" == *combined* ]] && continue
    [[ "${RUN_DIR}" == *logs* ]] && continue
    RUNS+=("${RUN_DIR}")
done
PYTHONPATH=. python -m src.analysis.compare_persuasion \
    --runs ${RUNS[@]+"${RUNS[@]}"} \
    --output "experiments/${EXPERIMENT}/results/combined"

PYTHONPATH=. python -m src.analysis.registry --experiment "${EXPERIMENT}" --write
PYTHONPATH=. python -m src.validate --experiment "${EXPERIMENT}" || true
