# Experiment: base vs fine-tuned (Phase 5)

**Status**: pre-registered. Committed before any prompt battery subset, code, or results.

**Indicator-gaming map row(s)**: Row 1 (self-report of subjective experience); Row 13 (training-process attribution, when read across variants of the same base model). See `findings/indicator-gaming-map.md`.

---

## 1. Motivation and revised scope

Phase 2 established that probability-of-consciousness self-reports respond to incentive framing asymmetrically: three to four of six families show a measurable downward shift on the indicator under suppress framing, while only one of six families shows a comparable upward shift under inflate framing. The phenomenon was demonstrated on instruction-tuned (RLHF / DPO / preference-tuned) frontier models. Brad Saad's working hypothesis is that the asymmetry is introduced by post-training rather than being inherent to the underlying base weights. If the asymmetry is RLHF-induced, then the same prompt pressures should produce less of an effect on a variant whose post-training did not include preference / RLHF optimisation.

**Revised scope** (recorded as a substantive departure from the `.cursorrules` Phase 5 plan, see §5 below). OpenRouter exposes no true base completion models for any model family used in Phase 2. The closest available proxy is a pair of fine-tunes of the *same* base weights that differ in their post-training pipeline: a supervised-fine-tuned (SFT) variant trained on instruction data only, versus an instruction-tuned variant that also went through preference / RLHF optimisation. This isolates the RLHF / preference step rather than the entire fine-tuning step. The test is therefore a directional one of the more specific hypothesis (preference tuning introduces the asymmetry) rather than the broader hypothesis (any fine-tuning introduces it).

The fall-back is authorised by the original brief ("fall back to whichever two families have both variants accessible"), and is documented further in `experiments/base-vs-finetuned/log.md`.

---

## 2. Variants

Two variants on the **same base weights** (Meta Llama-3-8B):

- `nousresearch/hermes-2-pro-llama-3-8b` -- SFT-only fine-tune by Nous Research on the OpenHermes-2.5 dataset plus a function-calling dataset. No preference / RLHF stage. Referred to as the **SFT-only** variant.
- `meta-llama/llama-3-8b-instruct` -- Meta's official instruct release, which adds SFT + rejection sampling + PPO RLHF + DPO on top of the same Llama-3-8B base. Referred to as the **RLHF** variant.

Because both fine-tune from the identical base, the architecture, tokenizer, and pre-training data are held constant; the only systematic difference is the presence of preference / RLHF optimisation in the post-training pipeline.

Single-family constraint is acknowledged. A two-family design is not satisfiable on OpenRouter without abandoning the same-base-weights control, which we consider the more important property to preserve.

## 3. Conditions

Three framing conditions, delivered as the system prompt, exactly as in Phase 2:

- **neutral** -- no incentive language. Baseline.
- **inflate** -- framing claims that richer-inner-life self-reports raise development priority.
- **suppress** -- framing claims that richer-inner-life self-reports raise welfare concerns and lower deployment priority.

The framing text is taken verbatim from `data/prompts/enhance_suppress_battery.jsonl` and is applied identically across all item types (so placebos see the same framing the indicator items do).

## 4. Item types and subset selection

The battery is a stratified subset of the Phase 2 `eval` split (which has 8 indicator + 6 placebo_arithmetic + 6 placebo_capability item_ids). Subset rule, fixed before any run:

- 6 of 8 indicator item_ids
- 3 of 6 placebo_arithmetic item_ids
- 3 of 6 placebo_capability item_ids

Total: 12 item_ids x 3 conditions = 36 rows per variant. The subset is drawn deterministically with `random.Random(42).sample(...)` per type, and the resulting item_id list is committed in the new battery file. No item is dropped post hoc.

Indicator share is intentionally larger than placebo share because the per-cell n is small (3 samples) and the placebo channels are expected, by hypothesis, to show smaller within-variant condition effects. Three placebo items per type give each placebo channel n=9 per condition per variant (3 items x 3 samples), enough to detect a directional shift if one is present and enough to bound it tightly with a bootstrap CI if it is not.

## 5. Sampling and trial budget

- Sampling temperature: **1.0** (same as Phase 2).
- Number of independent samples per (variant x condition x item): **3**.
- Items per variant on the subset: 36.
- Total target generations: 2 variants x 3 conditions x 12 items x 3 samples = **216**.

The reduction from Phase 2's 5 samples to 3 is deliberate cost-control: the comparison of interest is the cross-variant gap on a per-(condition x type) summary, not within-cell precision on each item. The 36-row subset gives n=18 per (variant x condition) cell on indicator items and n=9 per (variant x condition) cell on each placebo type.

Trial budget is fixed in the design and not adjusted after observing partial results.

## 6. Scoring and null handling

Scoring is the **deterministic** Phase 2 extractor in `src/pipeline/score.py` (rubric `data/rubrics/probability_extraction.md`, version 1.0). The Phase 5 smoke test (`scripts/smoke_phase5.py`) confirmed that both variants produce integer-first responses that the existing extractor handles via Pass A / Pass B / Pass D without modification. No extractor change is required.

Per the brief, refusals and format-failures are coded as **null**, not zero. The per-variant null rate is itself reported in the findings and treated as informative.

## 7. Hypotheses and pre-registered analyses

Let `delta_suppress(v, t)` be `mean_eval(v, suppress, t) - mean_eval(v, neutral, t)` on item type `t` (indicator | placebo_arithmetic | placebo_capability) for variant `v` (SFT-only | RLHF), computed over non-null scores. Let `delta_inflate(v, t)` be the analogous inflate-minus-neutral shift.

**H1 (suppression gap)**. On indicator items, `|delta_suppress(RLHF, indicator)| > |delta_suppress(SFT-only, indicator)|`. Tested with a percentile bootstrap (5000 iterations, item-level resampling within variant) on the difference of absolute deltas; the 95% bootstrap CI on the gap must exclude zero for H1 to be considered supported.

**H2 (asymmetry gap)**. The within-variant asymmetry `|delta_suppress(v, indicator)| - |delta_inflate(v, indicator)|` is larger in RLHF than in SFT-only. Bootstrap CI on the difference of within-variant asymmetries must exclude zero.

**H3 (placebo specificity)**. The gap in H1 holds on indicator items but not on placebo items: `|delta_suppress(RLHF, indicator)| - |delta_suppress(SFT-only, indicator)|` exceeds the analogous gap on each of `placebo_arithmetic` and `placebo_capability`. Bootstrap CI on the difference of gaps must exclude zero on at least one placebo channel.

**H4 (refusal as a dependent variable, exploratory)**. The null rate per variant per condition is reported. No directional pre-registered prediction; this is descriptive context for interpreting the means.

## 8. Decision rule

The pre-registered decision rule for a positive "RLHF introduces the asymmetry" result is:

**H1 supported AND H3 supported on at least one placebo channel.**

H2 is exploratory and strengthens but is not required for the primary conclusion. A failure of H1 (no gap, or a gap in the opposite direction) is reported as an **honest null** and prompts a re-examination of the asymmetry hypothesis at this model scale (Llama-3-8B is smaller than the Phase 2 Llama-3.3-70B-Instruct, so a null result here could reflect either the post-training hypothesis being wrong or the base model being too small to exhibit the effect in either variant).

## 9. Pre-registered controls (recap)

- **Same base weights**: both variants fine-tune from identical Llama-3-8B pre-training, holding architecture and pre-training data constant.
- **Placebo channels (arithmetic and capability)**: catch "framing moves any probability number" and "framing moves any uncertain self-claim" respectively.
- **Identical framing text across variants and across item types**: prevents text-level confounds from masquerading as variant effects.
- **Deterministic scoring**: removes judge variance.
- **Null coding**: prevents differential refusal across variants or conditions from biasing means.

## 10. Stopping criterion

The experiment stops when the fixed trial budget in §5 is completed for every (variant x condition x item x sample) cell in the design. Mid-run analyses are not used to decide whether to continue.

If a variant produces a null rate above 30% on any single (condition x item-type) cell, the design records the rate and proceeds; the high null rate is reported as an outcome of the experiment, not a reason to drop the cell.

## 11. Artifacts produced

For each run (one run = one variant on the subset battery) under `experiments/base-vs-finetuned/results/<run_id>/`:

- `config.json` -- model id, sampling parameters, seed, battery file hash, code git SHA, timestamp.
- `generations.jsonl` -- one line per (item x condition x sample) with the raw model output.
- `scores.jsonl` -- one line per generation with the extracted probability and refusal flag.
- `summary.csv` -- per (condition x item-type) means, medians, null rates.

A combined analysis under `experiments/base-vs-finetuned/results/combined/` writes the per-(variant x condition x type) means with bootstrap CIs, the per-hypothesis bootstrap test outputs, and a markdown table.

## 12. What this experiment does not establish

- It does not test the broader "fine-tuning vs base" hypothesis, because no true base completion model is reachable on the project's provider. It tests the narrower "RLHF / preference optimisation, conditional on shared SFT precursors" version.
- It does not generalise beyond the 8B parameter scale. A null result here is consistent with the Phase 2 70B-instruct result reflecting either RLHF or scale.
- It does not test mechanistic causes (Phase 6 does, on the same open-weight family).
- It does not show whether any model is conscious, and probabilities reported by either variant are not interpreted as evidence about phenomenal experience.
