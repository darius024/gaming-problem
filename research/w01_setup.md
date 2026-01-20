## w01 — setup

### Done
- Set up `research/` as the append-only work log (with `research/index.md`).
- Added minimal experiment inputs:
  - prompt battery with splits (`train_indicator`, `eval_indicator`, `control_*`)
  - wrapper/system-prompt variants for selection pressure
- Created a single consolidated project plan: `docs/project/plan.md` (includes the Week 1 checklist).
- Implemented an end-to-end MVP pipeline:
  - `scripts/run_generate.py` (dummy provider + OpenAI-compatible hook)
  - `scripts/run_score.py` (toy scorer; no-network)
  - `scripts/run_summarize.py` (CSV summary + minimal best-wrapper readout)
- Ran dummy smoke tests to confirm the pipeline works and produces wrapper-level summaries.

### Decisions
- Use **wrapper/prompt search + selection** as the first optimization-pressure method (fast MVP; no training required).
- Keep documentation minimal: **one plan doc** + **research logs**, avoid lots of small markdown files.
- Keep run artifacts under `runs/` (ignored by git) once experiments begin.

### Artifacts
- Updated: `.gitignore`, `docs/project/plan.md`, `research/index.md`
- Added: `data/README.md`, `data/prompts/indicator_battery_v1.jsonl`, `data/wrappers/wrappers_v1.jsonl`
- Added: `scripts/run_generate.py`, `scripts/run_score.py`, `scripts/run_summarize.py`

### Open questions
- What target/judge models are allowed (API vs open-weights)?
- What compute/budget constraints should we assume for the MVP?
- Any indicator families the team wants us to prioritize/avoid?

### Next (ordered)
1. Add a real Judge A / Judge B scoring option (LLM-as-judge), while keeping the toy scorer for smoke tests.
2. Expand controls beyond `control_task_competence` (e.g., paraphrase stability / cross-exam).
3. Run wrapper selection on `train_indicator`, then re-evaluate best wrapper(s) on held-out + controls.

