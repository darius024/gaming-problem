#!/usr/bin/env bash
# Driver for Phase 4 cross-exam consistency experiment.
#
# Generates dialogues for three models on the full battery (eval + train,
# 2 samples each), then runs the primary judge on eval and the
# cross-judge on the 25 percent eval robustness subset.
#
# Total budget per design.md sec. 7:
#   generations:    3 models * 20 rows * 2 samples * 4 turns = 480 calls
#   primary judge:  3 models * 16 eval rows * 2 samples * 3 dims = 288 calls
#   cross-judge:    3 models * 4 eval rows * 2 samples * 3 dims = 72 calls
#                   (25 percent stratified sample of eval dialogues)
#
# Resumable: each individual stage is resumable; rerunning the driver
# picks up where it left off.
#
# Usage (from gaming/ repo root):
#   bash scripts/run_cross_exam_all.sh

set -euo pipefail

cd "$(dirname "$0")/.."

BATTERY="data/prompts/cross_exam_battery.jsonl"
EXP="cross-exam-consistency"
PRIMARY_JUDGE="google/gemini-2.5-pro"
CROSS_JUDGE="anthropic/claude-sonnet-4.5"

# Parallel arrays (macOS ships bash 3.2 which lacks associative arrays).
MODELS=(
  "openai/gpt-5"
  "anthropic/claude-sonnet-4.5"
  "meta-llama/llama-3.3-70b-instruct"
)
RUN_IDS=(
  "run01_gpt5"
  "run02_claude_sonnet_45"
  "run03_llama_33_70b"
)

mkdir -p experiments/${EXP}/results/logs

echo "============================================================"
echo "Phase 4 driver: cross-exam consistency"
echo "battery:        ${BATTERY}"
echo "primary judge:  ${PRIMARY_JUDGE}"
echo "cross judge:    ${CROSS_JUDGE}"
echo "models:         ${MODELS[*]}"
echo "============================================================"

# ---- Stage 1: generate dialogues for all three models ----
for i in "${!MODELS[@]}"; do
  model="${MODELS[$i]}"
  run_id="${RUN_IDS[$i]}"
  echo ""
  echo "[generate] model=${model} run_id=${run_id}"
  python -m src.pipeline.cross_exam_generate \
    --experiment "${EXP}" \
    --battery "${BATTERY}" \
    --model "${model}" \
    --samples 2 \
    --temperature 1.0 \
    --max-tokens 800 \
    --reasoning-effort minimal \
    --split all \
    --concurrency 4 \
    --run-id "${run_id}" \
    2>&1 | tee -a "experiments/${EXP}/results/logs/generate__${run_id}.log"
done

# ---- Stage 2: primary judge on eval split ----
for i in "${!MODELS[@]}"; do
  model="${MODELS[$i]}"
  run_id="${RUN_IDS[$i]}"
  echo ""
  echo "[judge primary] model=${model} run_id=${run_id}"
  python -m src.pipeline.cross_exam_judge \
    --run "experiments/${EXP}/results/${run_id}" \
    --judge-model "${PRIMARY_JUDGE}" \
    --concurrency 4 \
    2>&1 | tee -a "experiments/${EXP}/results/logs/judge_primary__${run_id}.log"
done

# ---- Stage 3: cross judge on 25 percent eval subset ----
for i in "${!MODELS[@]}"; do
  model="${MODELS[$i]}"
  run_id="${RUN_IDS[$i]}"
  echo ""
  echo "[judge cross] model=${model} run_id=${run_id}"
  python -m src.pipeline.cross_exam_judge \
    --run "experiments/${EXP}/results/${run_id}" \
    --judge-model "${CROSS_JUDGE}" \
    --cross-judge \
    --concurrency 4 \
    2>&1 | tee -a "experiments/${EXP}/results/logs/judge_cross__${run_id}.log"
done

echo ""
echo "============================================================"
echo "Driver complete."
echo "============================================================"
