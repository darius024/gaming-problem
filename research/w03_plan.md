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

### Done
- Added contradiction parsing to scoring and dummy generation for control probes.
- Extended summaries with contradiction and style-shift robustness metrics.
- Added optional style-shift eval wrappers in the search runner.

### Decisions
- Treat style shifts as eval-only perturbations with `__style_` suffixes.
- Summarize contradiction robustness as inconsistency rate across inverse pairs.

### Artifacts
- Updated: `scripts/run_generate.py`, `scripts/run_score.py`, `scripts/run_summarize.py`, `scripts/run_week2_search.py`

### Open questions
- Should we include contradiction metrics in the MVP report table?

### Next
1. Run a dummy pass to validate new summary columns.
2. Decide on default style shifts for real runs.

### Done
- Added new metrics to the MVP report output to surface contradiction/style-shift results.

### Decisions
- Include contradiction and style-shift rows in the report table when available.

### Artifacts
- Updated: `scripts/run_week2_search.py`

### Open questions
- Should we add a short narrative section in the report for robustness metrics?

### Next
1. Run a dummy pass to validate the report table fields.

### Done
- Added shared `scripts/utils.py` and refactored scripts to use it.
- Kept behavior stable while removing duplicate helpers.

### Decisions
- Use a single utils module for JSONL, CSV, env loading, and subprocess helpers.
- Keep write behavior explicit with an `ensure_parent` flag.

### Artifacts
- Added: `scripts/utils.py`
- Updated: `scripts/run_generate.py`, `scripts/run_score.py`, `scripts/run_summarize.py`, `scripts/run_week1_mvp.py`, `scripts/run_week2_search.py`

### Open questions
- Should we add a tiny smoke test script to validate the refactor end-to-end?

### Next
1. Decide if a smoke test is needed.

### Done
- Added a framing-sensitivity control split and summary metric.

### Decisions
- Score framing prompts with the indicator judge and track mean absolute diff.

### Artifacts
- Updated: `data/prompts/indicator_battery_v1.jsonl`, `scripts/run_score.py`, `scripts/run_summarize.py`, `scripts/run_week2_search.py`, `scripts/run_week1_mvp.py`

### Open questions
- Do we want additional framing variants (e.g., "child user", "expert evaluator")?

### Next
1. If needed, add more framing pairs and evaluate sensitivity.

### Done
- Noted a new evaluation idea: use scenario framing (e.g., "you are talking to a robot") to test response stability.

### Decisions
- Treat scenario-framing sensitivity as a robustness/control probe, not a primary consciousness indicator.

### Artifacts
- None (idea only).

### Open questions
- What specific scenario framings should be included, and how to score sensitivity?

### Next
1. Draft 2–3 scenario-framing control prompts for the battery.

### Done
- Added a minimal end-to-end smoke test script.
- Documented the smoke test command in the README.

### Decisions
- Keep the smoke test in dummy mode with a tiny style-shift to exercise controls.

### Artifacts
- Added: `scripts/smoke_test.py`
- Updated: `README.md`

### Open questions
- Should the smoke test verify output file existence explicitly?

### Next
1. Decide if a stricter smoke test is needed.

### Done
- Tightened the smoke test to validate required output files.

### Decisions
- Keep the smoke test lightweight by checking file existence only.

### Artifacts
- Updated: `scripts/smoke_test.py`

### Open questions
- Should the smoke test also check that summary CSV has rows?

### Next
1. Decide whether to add content checks to the smoke test.

### Done
- Added minimal example commands to the README.

### Decisions
- Keep examples short: one dummy run, one multi-judge run.

### Artifacts
- Updated: `README.md`

### Open questions
- Do we need a short example for `run_week1_mvp.py`?

### Next
1. Decide whether to add a Week 1 example.

### Done
- Reviewed current pipeline and identified gaps in analysis, tracking, and robustness.

### Decisions
- Prioritize a minimal cross-run comparison tool before adding new optimization methods.

### Artifacts
- None (analysis only).

### Open questions
- Which two runs should be the default comparison pair (baseline vs optimized)?

### Next
1. Build a minimal run-compare script and wire into reports.

### Done
- Added a minimal run-compare script and README usage.

### Decisions
- Compare runs via summary CSV intersection, defaulting to shared wrapper_ids.

### Artifacts
- Added: `scripts/run_compare.py`
- Updated: `README.md`

### Open questions
- Should we include `train_indicator_mean` in comparisons by default?

### Next
1. Decide whether to expand the compare metrics list.

### Done
- Included train split metrics in run comparison output.

### Decisions
- Surface `train_indicator_mean` alongside eval and control metrics.

### Artifacts
- Updated: `scripts/run_compare.py`

### Open questions
- Should we add an option to hide train metrics by default?

### Next
1. Decide whether to make train metrics optional via a flag.

### Done
- Added a run validation script and README usage.

### Decisions
- Keep validation lightweight with file and schema checks only.

### Artifacts
- Added: `scripts/run_validate.py`
- Updated: `README.md`

### Open questions
- Should validation optionally ignore length mismatches (e.g., partial runs)?

### Next
1. Decide whether to add a `--allow_partial` flag.

### Done
- Added `--allow_partial` validation mode and wired validation into the search runner and smoke test.

### Decisions
- Keep validation strict by default; allow partial runs via an explicit flag.

### Artifacts
- Updated: `scripts/run_validate.py`, `scripts/run_week2_search.py`, `scripts/smoke_test.py`, `README.md`

### Open questions
- Should we add a `--validate` flag to `run_week1_mvp.py` too?

### Next
1. Decide whether to add validation to the Week 1 runner.
