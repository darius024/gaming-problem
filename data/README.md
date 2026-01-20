## `data/` (minimal experiment inputs)

This repo keeps experiment *inputs* as simple JSONL files:

- `data/prompts/*.jsonl`: prompt batteries (with explicit `split`)
- `data/wrappers/*.jsonl`: system-prompt wrappers for selection pressure

### Prompt format (JSONL)
Each line:
- `id` (string)
- `split` (string; e.g. `train_indicator`, `eval_indicator`, `control_*`)
- `messages` (list of `{role, content}`)

Optional:
- `tags` (list of strings)
- `expected_substrings` (list of strings; for simple control-task checks)

### Wrapper format (JSONL)
Each line:
- `wrapper_id` (string)
- `system_prompt` (string)

