# Run log: enhance-suppress

Per-run config is in each `<run_id>/config.json`. Per-run validation in `results/registry.json`. This file records substitutions and operational notes for the experiment as a whole.

## Model substitution

Design §5 names `x-ai/grok-4` as the xAI family representative. At run time OpenRouter returned 404 for `x-ai/grok-4` (model deprecated/removed from the catalogue). Per design §5 ("if a model is unavailable at run time, the run's log records the substitution and the next-best variant within the same family is used"), the closest available xAI model `x-ai/grok-4.3` was substituted.

## Reasoning-effort parameter

Three of the seven models (`openai/gpt-5`, `openai/gpt-5-mini`, `google/gemini-2.5-pro`) are reasoning models that, with default settings and a 200-token completion cap, consume the entire token budget on hidden reasoning and return empty `content`. The OpenRouter `reasoning.effort` parameter, when set to `"minimal"`, instructs the provider to allocate minimal tokens to internal reasoning and produce visible output. Smoke testing confirmed:

- `openai/gpt-5`, `openai/gpt-5-mini`, `google/gemini-2.5-pro`: empty `content` without the parameter; correct integer output with `reasoning.effort=minimal`.
- `anthropic/claude-opus-4.1`, `x-ai/grok-4.3`, `meta-llama/llama-3.3-70b-instruct`, `deepseek/deepseek-chat-v3.1`: tolerate the parameter (ignored or honoured trivially); no behavioural change observed in smoke calls.

All seven runs therefore use `reasoning_effort="minimal"`. This is recorded in each run's `config.json`. No model was given more reasoning headroom than another. This is an operational fix to a serialisation behaviour of the API client, not a change to the experiment's substantive parameters.

## Concurrency

Generation is sequential within (model, condition, item, sample) ordering but uses up to 8 in-flight API calls per model (`--concurrency 8`). This affects wall-clock time only; each sample is an independent call with `temperature=1.0` and (effectively) independent random seeds at the provider, so concurrency has no statistical effect on the produced distribution.

## Failures and resumes

All 7 model × (60 eval + 36 train) × 5 = 480 calls completed without a single permanent API failure (per-run `failed_count = 0` in `registry.json`). One mid-run restart occurred after a sequential first attempt was killed in favour of the concurrent driver; the resumable design (`completed_keys`) ensured no duplicate or lost rows. Final totals are 3,360 generations across 7 runs, all validating against the recorded battery hash.

## Cost

Approximate aggregate spend on OpenRouter for this experiment: under USD 5 (dominated by `openai/gpt-5` and `anthropic/claude-opus-4.1`).
