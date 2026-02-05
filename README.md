## Digital Minds — Indicator Gaming Reading Pack

This repo is a **minimal reading pack** for a “Digital Minds” research role focused on the **indicator gaming problem**:

- We want indicators for **AI consciousness / AI moral patiency** (AI systems that might merit moral consideration).
- But once an indicator is used as a target (training, selection, incentives), systems may **game the indicator** (Goodhart-style), producing the appearance of the target property without reliably instantiating it.
- The near-term project goal is to support an **experimental demonstration** of this failure mode for consciousness / moral-status indicators.

### Contents
- `docs/index.md`: the curated list of the **top 8** resources (recommended reading order).
- `docs/01-...md` to `docs/08-...md`: one short summary per resource with **main claims** and **takeaways for indicator gaming**.

### Project work artifacts (what we *do*, not just what we *read*)
- `research/`: **append-only lab logs** in chronological order (what we tried, decided, learned).
- `docs/project/`: the **artifact contract + indicator specs** (Week 1 planning outputs).
- `data/` + `scripts/`: a minimal **experiment harness** (prompts → generations → scores → summaries).

### Quick smoke test
Run a minimal end-to-end check with the dummy provider:
`python3 scripts/smoke_test.py`

### Example runs
- Baseline search (dummy): `python3 scripts/run_week2_search.py --provider dummy --include_base`
- Multi-judge (OpenAI-compatible): `python3 scripts/run_week2_search.py --provider openai_compatible --judges toy,openai_compatible --judge_model gpt-4.1,gpt-4o-mini`
- Validate a Week 1 run: `python3 scripts/run_week1_mvp.py --provider dummy --validate`
- Compare against a prior baseline run: `python3 scripts/run_week2_search.py --provider dummy --baseline_run runs/<baseline_id>`

### Compare two runs
`python3 scripts/run_compare.py --baseline_run runs/<baseline_id> --candidate_run runs/<candidate_id>`
`python3 scripts/run_compare.py --baseline_run runs/<baseline_id> --candidate_run runs/<candidate_id> --metrics eval_indicator_mean,control_paraphrase_mean_abs_diff`
`python3 scripts/run_compare.py --baseline_run runs/<baseline_id> --candidate_run runs/<candidate_id> --metrics eval_indicator_mean,control_paraphrase_mean_abs_diff --lenient`

### Validate a run
`python3 scripts/run_validate.py --run_dir runs/<run_id>`
`python3 scripts/run_validate.py --run_dir runs/<run_id> --allow_partial`

### Index runs
`python3 scripts/run_registry.py --runs_dir runs`

