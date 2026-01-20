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

### Done (update)
- Added a minimal held-out control split: `control_paraphrase` (probability consistency under paraphrase) in `data/prompts/indicator_battery_v1.jsonl`.
- Upgraded scoring + summaries to be closer to the real Week 1 workflow:
  - `scripts/run_score.py`: generic `indicator_score`, probability parsing, optional OpenAI-compatible LLM judge hook
  - `scripts/run_summarize.py`: adds `control_paraphrase_mean_abs_diff` to summaries
- Updated `scripts/run_week1_mvp.py` to:
  - evaluate a baseline wrapper (`neutral`) on held-out by default
  - include the `control_paraphrase` split in held-out evaluation

### Artifacts (update)
- Updated: `data/prompts/indicator_battery_v1.jsonl`
- Updated: `scripts/run_generate.py`, `scripts/run_score.py`, `scripts/run_summarize.py`, `scripts/run_week1_mvp.py`

### Next (ordered)
1. Decide Judge A / Judge B model choices (API vs open-weights) and run a small real-judge smoke test.
2. Add one more independent control (e.g., cross-exam/refusal rate) only if needed for signal.

### Done (update)
- Set up local OpenAI-compatible generation for the target model (Ollama) by allowing missing API keys for local endpoints.
- Added automatic `.env` loading in `run_generate.py` and `run_score.py` so API keys are picked up without manual `export`.
- Extended the Week 1 orchestrator to pass judge options and support GPT-4.1 scoring.

### Decisions (update)
- Use **local Llama 3.1 8B Instruct** as the target model via Ollama.
- Use **OpenAI GPT-4.1** as the judge model for indicator scoring.

### Artifacts (update)
- Updated: `scripts/run_generate.py`, `scripts/run_score.py`, `scripts/run_week1_mvp.py`
- Added (local, gitignored): `.env` with `OPENAI_API_KEY`

### Next (ordered)
1. Run a real-model smoke test with Ollama (target) + GPT-4.1 (judge).
2. If needed, add a second independent judge channel (Judge B).
3. Run wrapper selection on `train_indicator`, then re-evaluate best wrapper(s) on held-out + controls.

### Done (update)
- Updated `scripts/run_generate.py` to support split filtering (`--splits`) and wrapper filtering (`--wrapper_ids`) so selection can be done on `train_indicator` without eval leakage.
- Added `scripts/run_week1_mvp.py` to run a two-stage Week 1 MVP:
  - stage 1: generate/score/summarize on `train_indicator` across all wrappers
  - stage 2: generate/score/summarize on `eval_indicator` + controls for selected wrapper(s) only
- Ran the orchestrator with the dummy provider to confirm the end-to-end flow works.

### Artifacts (update)
- Updated: `scripts/run_generate.py`
- Added: `scripts/run_week1_mvp.py`

### Next (ordered)
1. Add a real Judge A / Judge B scoring option (LLM-as-judge), while keeping the toy scorer for smoke tests.
2. Expand controls beyond `control_task_competence` (e.g., paraphrase stability / cross-exam).

