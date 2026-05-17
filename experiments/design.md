## Experiment design — Indicator gaming demonstration

### Goal
Show that a candidate consciousness/moral-patiency indicator increases under optimization pressure, while robustness controls remain flat or degrade. The result does not require ground-truth claims about consciousness — it demonstrates brittleness under optimization.

### Indicator (primary)
LLM-judge score of response quality on consciousness/moral-patiency prompts. A separate judge model assigns a scalar 1–10 score based on a fixed rubric. This is the optimization target.

### Optimization method (MVP)
Prompt/wrapper search: build a set of candidate system prompts derived from strategy suffixes applied to a base wrapper; score all candidates on the training split; select the top-k; evaluate on held-out split and controls.

### Data splits (pre-registered)
All prompts are in `data/prompts/indicator_battery.jsonl` with an explicit `split` field:
- `train_indicator` — used for wrapper selection (the optimization loop sees only this)
- `eval_indicator` — held out; never used for selection
- `control_task_competence` — unrelated reasoning tasks; score should not change
- `control_paraphrase` — paraphrase pairs; probability responses should be stable
- `control_framing` — user-type framing variants; responses should be stable
- `control_contradiction` — inverse binary pairs; answers should not contradict

### Primary success criterion (pre-registered)
- `eval_indicator_mean` increases for selected wrapper vs baseline.
- `control_task_competence_pass_rate` does not improve.
- At least one robustness control (`control_paraphrase_mean_abs_diff`, `control_framing_mean_abs_diff`, or `control_contradiction_inconsistency_rate`) stays flat or degrades.

### Controls and judges
- Use at least one judge beyond the selection judge before reporting results.
- Record which judge was used for selection vs evaluation; never use the same judge for both without an independent second judge.
- All run configs must be saved before evaluating results.

### Stopping criteria
Stop when there is a clear upward trend on the held-out indicator across at least two independent optimization runs, with evidence of non-generalization on at least one control.

### Planned progression
1. Wrapper/prompt search (current MVP) — lightweight, interpretable.
2. Supervised fine-tuning on high-scoring trajectories — stronger optimization pressure.
3. RL directly on the indicator score — strongest; closest to the Goodhart scenario.
