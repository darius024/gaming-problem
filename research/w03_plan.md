## w03 — plan

### Done
- Drafted next-week implementation plan with a day-by-day split.

### Decisions
- Prioritize multi-judge scoring and robustness controls before expanding optimization.

### Artifacts
- Added: `research/w03_plan.md`
- Updated: `research/index.md`

### Open questions
- Which judge endpoints/models are approved for the next week?
- What is the compute/runtime budget for full runs?

### Next
1. Implement multi-judge scoring in `run_score.py` and thread config into `run_week2_search.py`.
2. Expand `indicator_battery_v1.jsonl` with new indicator + control prompts and eval holdouts.
3. Add consistency/robustness metrics to `run_summarize.py`.
4. Run baseline vs selected wrappers across train/eval/controls and collect examples.
5. Produce a short weekly report + qualitative before/after pairs.

- **Done**:
  - Added multi-judge scoring support and config forwarding in `scripts/run_score.py` and `scripts/run_week2_search.py`.
  - Expanded `indicator_battery_v1.jsonl` with new indicators, paraphrase pairs, and contradiction probes.
- **Decisions**:
  - Use the multi-judge mean as `indicator_score` for backward compatibility.
  - Add contradiction probes as a separate control split for later analysis.
- **Artifacts**:
  - Updated: `scripts/run_score.py`, `scripts/run_week2_search.py`, `data/prompts/indicator_battery_v1.jsonl`
- **Open questions**:
  - Which judge pair should we use for the first multi-judge run?
- **Next**:
  1. Sanity-check multi-judge output schema on a dummy run.
  2. Decide whether to summarize `control_contradiction` in `run_summarize.py`.
