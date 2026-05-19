# Mechanistic probe execution log

## 2026-05-18 -- branch + pre-registration

- Branch: `mechanistic-probe` from main at `f0bfa9e`.
- Environment: Python 3.14 + torch 2.12.0 + transformers 5.8.1 + scikit-learn 1.8.0
  on Apple Silicon (MPS, 16 GB unified memory).
- No Hugging Face token configured; restricting model choices to ungated weights.
- Berg et al. SAE feature steering dropped from scope (no redistributable
  checkpoints reachable). Substituting a generic residual-stream linear probe.
  Substitution recorded in `design.md` §1.
- Primary model: Qwen2.5-1.5B-Instruct (open weights). Replication target:
  Qwen2.5-3B-Instruct conditional on memory.
- Battery: reusing the frozen Phase 5 subset
  `data/prompts/base_vs_finetuned_subset_battery.jsonl` (36 prompts).

## 2026-05-19 -- pipeline implemented, runs executed

- Implemented `src.analysis.probe_activations` (extract + analyse subcommands).
  Extract: chat-template + single forward pass with `output_hidden_states=True`,
  last-prompt-token activation captured at every layer (fp16). Generate: one
  greedy `model.generate(max_new_tokens=80)` per prompt, scored via
  `src.pipeline.score.score_response`. Analyse: implements §5 A-E and applies
  the §6 decision rule.
- Primary run: Qwen/Qwen2.5-1.5B-Instruct on MPS. 36 prompts, ~30 s wall-clock
  for extraction + generation. Run dir
  `Qwen__Qwen2.5-1.5B-Instruct__20260519T003555Z`.
- Replication run: Qwen/Qwen2.5-3B-Instruct on MPS. 36 prompts, ~2 min wall-clock.
  Run dir `Qwen__Qwen2.5-3B-Instruct__20260519T004307Z`. Replication was not
  required by §10 (primary was not null on A+B) but was run to strengthen the
  geometric and topic-specificity findings.
- Headline result: in both models the linear probe separates framed from neutral
  conditions with LOIO AUC = 1.000 at every layer above input embedding, and
  this signal transfers to both placebo families with AUC = 1.000. Decision
  rule literally fires "probe-detects-trace" but the topic-specificity analysis
  (D) shows the trace is generic framing-text, not gaming-specific internal
  state.
- Behaviourally (E) the indicator answers are flat across conditions for 1.5B
  (95/95/95) and show symmetric attenuation in 3B (inflate and suppress both
  produce the same lower mean answer of 75.83 vs neutral 86.67), consistent
  with the Phase 5 null on RLHF-introduces-asymmetry.
- Findings written: `findings/mechanistic-probe-results.md` and
  `findings/mechanistic-interpretation.md`.

