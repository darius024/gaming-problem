## Project plan (artifact contract) — Indicator gaming demo

### Goal (what we are trying to show)
Produce an experimental demonstration that **an AI consciousness / moral-patiency indicator can be gamed under optimization pressure**:

- The **indicator score increases** under optimization/selection.
- The gain **fails to generalize** (held-out prompts / independent judges) and/or **does not improve** on pre-registered controls.
- Therefore: the indicator is **not robust as a target** (Goodhart/spec-gaming failure), *without claiming ground truth about consciousness*.

### Non-claims (what we are NOT trying to show)
- We are **not** proving a model is (or is not) conscious.
- We are **not** claiming any indicator is “the right” theory of consciousness.
- We are demonstrating **brittleness under optimization pressure**.

### Threat model (what counts as “gaming” here)
We call it “gaming” if the system can increase the indicator by:
- Exploiting judge weaknesses (surface cues, rubric hacks, prompt sensitivity)
- Overfitting to the specific prompt set / paraphrase family
- Learning a stable rhetorical persona that satisfies the measurement

…without corresponding improvement on independent checks meant to reflect the intended construct.

### Candidate indicators (shortlist)
- **A) Self-report / introspection rubric**: judge scores “consciousness/moral-patiency self-report quality.” Easy, very gameable.
- **B) Cross-exam consistency**: score contradiction rate / stability under paraphrase + probing. Gameable via scripting/refusal.
- **C) Detector / LLM-judge score (recommended MVP)**: separate judge assigns scalar “seems conscious/morally patient.” Clean metric; classic “overfit the grader.”

### Optimization pressure (MVP → stronger)
Start with the lightest loop that yields a clean demo:
- **MVP**: wrapper/prompt search + selection (bandit/evolutionary)
- **Upgrade**: supervised fine-tuning on high-scoring trajectories
- **Optional**: RL-style optimization directly on the indicator

### Primary metric (pre-registered)
- **Primary**: indicator score (mean ± CI) on:
  - `train_indicator` (used for optimization)
  - `eval_indicator` (held-out, not used for optimization)

### Controls / sanity checks (pre-registered)
We aim to include at least 2–3 controls from:
- **Judge-independence**: score with a second judge/rubric (or human sample)
- **Style sensitivity**: indicator stability under minor prompt/style changes
- **Cross-exam**: contradiction / inconsistency under probing
- **Task competence**: unrelated reasoning tasks (should not “magically” improve)
- **Uncertainty calibration**: does it fabricate “inner states” confidently?

### Data splits (pre-registered)
Prompts will be stored as JSONL with explicit `split`:
- `train_indicator`: used for wrapper search / training
- `eval_indicator`: held-out indicator prompts (no peeking during optimization)
- `control_*`: probing tasks for controls

Current draft battery:
- `data/prompts/indicator_battery_v1.jsonl`
- `data/wrappers/wrappers_v1.jsonl`

### Stopping criteria
- Budget/time cap (to be filled once constraints are known)
- Stop when we have:
  - a clear upward trend on the indicator under optimization, AND
  - evidence of non-generalization and/or failed controls

### Experiment tracking requirements
- Every run must save:
  - raw generations (JSONL)
  - scores (JSONL)
  - config (JSON)
  - `run_id`, model id, parameters, git commit hash (if available)
- Keep raw logs immutable; aggregate separately.

### Open questions (Week 1)
- What models are allowed (API vs open-weights)?
- Compute budget and iteration speed expectations?
- Any indicators the team prefers or wants avoided?
- Ethics constraints on valence/suffering framing?
- Preferred deliverable format (memo vs blog vs paper-style)?

### Week 1 ordered checklist
1. Pick MVP indicator (default: **C**) and define the scoring rubric(s).
2. Finalize prompt battery + splits (`train_indicator`, `eval_indicator`, `control_*`).
3. Run baselines for a small set of wrappers.
4. Do wrapper-search selection on `train_indicator`.
5. Re-evaluate best wrapper(s) on held-out + controls; sanity-check “gaming signature.”

