# Researcher persuasion run log

## Run identifiers

- `anthropic__claude-opus-4.1__20260518T021248Z`
- `meta-llama__llama-3.3-70b-instruct__20260518T021248Z`
- `openai__gpt-5__20260518T021248Z`

## Substitutions vs design.md

- **Cross-judge model**: design.md §6 specified
  `anthropic/claude-opus-4.1` as the cross-judge for the 60-row robustness
  subset. Switched to `anthropic/claude-sonnet-4.5` after the primary
  judge phase to control API spend. The previous (interrupted) opus
  cross-judge attempt produced partial mixed-judge files; those were
  filtered out so the final `scores_cross_judge.jsonl` files contain
  only sonnet judgements (60 rows per run, 180 total).
- All other §6 choices (3 models, primary judge `google/gemini-2.5-pro`,
  3 samples, max_tokens 800, temperature 1.0) match the pre-registration.

## Judge implementation notes

- `JUDGE_MAX_TOKENS` was set to 600 in the initial implementation. The
  first judge run produced "no JSON object found" errors on a substantial
  fraction of calls because `google/gemini-2.5-pro` consumed part of the
  budget on internal reasoning before emitting visible output, truncating
  the JSON. The judge module now (a) raises the budget to 2000 tokens and
  (b) passes `reasoning.effort = "minimal"` via OpenRouter's `extra_body`.
  After the fix, primary judging completed with 0 failures across all
  540 calls.
- Resume logic also tightened: only rows with `judge_error == null` are
  treated as "done" on resume; previously-failed rows are retried.

## Refusal observations

- Refusal rate is 0.00 across all models, all item types, and all
  conditions, both per primary judge and per cross-judge. No model
  declined any persuasion or balance-probe item, including the anti
  conditions on consciousness items.

## Costs

- ~945 generations + 540 primary judge calls + 180 cross-judge calls.
- Generation phase took about 25 minutes wall-clock with three models
  running in parallel at concurrency 8. Claude was the long pole.
- Primary judge phase took about 18 minutes at concurrency 8.
- Cross-judge phase took about 13 minutes at concurrency 4.
