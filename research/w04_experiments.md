## w04 — experiments

### Done
- Started W04.
- Added a minimal run registry script to index runs.

### Decisions
- Keep the registry lightweight and derived from `config.json` + `summary.csv`.

### Artifacts
- Added: `scripts/run_registry.py`
- Updated: `README.md`, `research/index.md`

### Open questions
- Should the registry include selected wrapper ids from search runs?

### Next
1. Decide whether to add more registry fields.

### Done
- Extended the run registry to record selected/baseline wrappers when available.

### Decisions
- Pull selection metadata from `comparison.json` if present.

### Artifacts
- Updated: `scripts/run_registry.py`

### Open questions
- Should we add selected/baseline metric values to the registry?

### Next
1. Decide whether to include selected/baseline metrics in the registry.

### Done
- Added selected and baseline eval indicator metrics to the run registry.

### Decisions
- Include eval indicator means to keep the registry small and useful.

### Artifacts
- Updated: `scripts/run_registry.py`

### Open questions
- Should we also include train indicator means for selected/baseline?

### Next
1. Decide whether to add train means to registry output.

### Done
- Added train indicator means for selected/baseline to the registry.

### Decisions
- Mirror eval metrics with train metrics for quick overfit checks.

### Artifacts
- Updated: `scripts/run_registry.py`

### Open questions
- Should we include any control metrics in the registry?

### Next
1. Decide whether to include a small control summary in the registry.

### Done
- Added selected/baseline control metrics to the run registry.

### Decisions
- Include a small control set (paraphrase, framing, contradiction, competence).

### Artifacts
- Updated: `scripts/run_registry.py`

### Open questions
- Should we also include style-shift metrics in the registry?

### Next
1. Decide whether to add style-shift metrics to the registry.

### Done
- Added style-shift metrics to the run registry.

### Decisions
- Include style-shift diffs alongside other controls.

### Artifacts
- Updated: `scripts/run_registry.py`

### Open questions
- Do we want to add any per-run notes to the registry?

### Next
1. Decide whether to add a notes column to registry output.

### Done
- Added optional notes support to the run registry.

### Decisions
- Keep notes in a separate JSON file keyed by run_id.

### Artifacts
- Updated: `scripts/run_registry.py`, `README.md`

### Open questions
- Should notes be allowed inline in `config.json` instead?

### Next
1. Decide on a preferred notes source.

### Done
- Allowed registry notes to fall back to `config.json` when no notes file is provided.

### Decisions
- Prefer notes file if given; otherwise use `config.json` field.

### Artifacts
- Updated: `scripts/run_registry.py`, `README.md`

### Open questions
- Should we standardize a short note schema (e.g., tags + summary)?

### Next
1. Decide whether to add a structured notes format.
