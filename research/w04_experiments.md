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
