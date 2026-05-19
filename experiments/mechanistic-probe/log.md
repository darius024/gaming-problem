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
