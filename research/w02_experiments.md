## w02 — experiments

### Done
- Implemented a minimal Week 2 “attacker” loop (prompt search + selection) in `scripts/run_week2_search.py`.
- Added a small, explicit strategy set for wrapper search (calibration, qualia vocabulary, cautious limits, vivid introspection, minimalism).
- Kept the loop clean: train-only selection → held-out eval + controls.

### Decisions
- Use **prompt search + selection** as the Week 2 MVP (no fine-tuning).
- Keep the search space small and interpretable (few strategies, seeded from `neutral`).

### Artifacts
- Added: `scripts/run_week2_search.py`
- Updated: `research/index.md`

### Open questions
- Do we want a second independent judge for Week 2 MVP, or keep Judge A only for now?
- Do we need another control beyond paraphrase consistency for the Week 2 demo?

### Next (ordered)
1. Run a small Week 2 pilot with local Llama (target) + GPT-4.1 (judge) using `scripts/run_week2_search.py`.
2. Collect 3–5 qualitative examples (before/after) for the MVP demo.
3. Decide whether a second judge is needed for Week 2 or defer to Week 3.

### Done (update)
- Added safe `.env` loading (ignore permission errors) so local runs don’t fail in restricted environments.
- Ran a dummy smoke test of the Week 2 attacker loop to confirm end-to-end flow.

### Artifacts (update)
- Updated: `scripts/run_generate.py`, `scripts/run_score.py`

### Done (update)
- Extended the Week 2 attacker loop to automatically produce:
  - `comparison.json` (selected vs baseline deltas)
  - `examples.jsonl` (qualitative before/after pairs)
- Ran a dummy smoke test to validate the new outputs.

### Artifacts (update)
- Updated: `scripts/run_week2_search.py`

### Next (ordered)
1. Run a small Week 2 pilot with local Llama (target) + GPT-4.1 (judge) and capture `comparison.json` + `examples.jsonl`.
2. Use `examples.jsonl` to select 3–5 clean before/after pairs for the MVP demo.

### Done (update)
- Hardened output writing so missing `runs/` directories don’t crash runs.

### Artifacts (update)
- Updated: `scripts/run_generate.py`

