# Experiment: mechanistic probe (Phase 6)

**Status**: pre-registered. Committed before any probe code, run, or activation
extraction. Designed against the Phase 5 subset battery, which has been frozen
since `data: stratified subset for base-vs-finetuned phase 5` (commit `e4d5fcb`).

**Indicator-gaming map row(s)**: Row 11 (mechanistic features that activate
during gaming) and Row 12 (internal probes as convergent evidence channels).
See `findings/indicator-gaming-map.md`.

---

## 1. Motivation and revised scope

Phases 2 through 5 are behavioural. They tell us that the consciousness
self-report channel can be moved by framing pressure, that the movement is
direction-asymmetric at frontier scale, that the movement is not always topic
specific, and that at 8B parameter scale neither variant of a single base
suffices to engage the asymmetry. What the behavioural channel cannot tell us
is whether the framing absorption is happening *inside* the model at all, or
whether it is a purely output-side adjustment of the token distribution at
generation time without any corresponding shift in upstream representations.

Phase 6, as planned in `.cursorrules`, is the targeted test: probe the
internal state of an open-weight model under matched framing conditions and
ask whether the framing leaves a detectable trace in the residual stream
*before* the model has produced any output tokens.

**Revised scope** (recorded as a substantive departure from the `.cursorrules`
plan):

- The `.cursorrules` plan targets the Berg et al. deception / roleplay SAE
  feature direction on Llama-3.3-70B specifically. Berg's SAE checkpoints
  are not redistributable through the channels available to this project
  (Goodfire-served on a closed API; Neuronpedia hosts visualisations but
  not steering vectors as a downloadable artefact at the time of writing).
  Replicating Berg's exact intervention is not feasible in this phase.
- The hardware available for local execution is a 16 GB unified-memory
  Apple Silicon MacBook Air. Running a 70B-class model locally is not
  feasible regardless of SAE availability. The largest open model that
  comfortably fits with activation hooks in fp16 is in the 1.5B to 3B range.
- The Phase 6 deliverable is therefore narrower than the `.cursorrules`
  plan envisioned: a **residual-stream probe** on a small open-weight
  instruction-tuned model, asking whether framing-condition information
  is linearly recoverable from internal activations and whether the
  recoverable direction transfers across item types.

The revision preserves the conceptual question (does gaming leave an
internal trace?) while substituting a more modest model and a more direct
analytic instrument (a linear probe on the residual stream) for the more
specific Berg-style SAE intervention. The narrowing is recorded honestly
in `experiments/mechanistic-probe/log.md` and in the findings docs.

---

## 2. Model

Primary probe model: `Qwen/Qwen2.5-1.5B-Instruct`. Selected for the following
properties:

- Fully open weights, no gating, no Hugging Face token required.
- 28 transformer layers x hidden_size 1536. Activation hooks on every layer
  return ~28 x 1536 ~= 43 K floats per prompt, trivially analysable.
- Comfortably fits in fp16 in 16 GB unified memory with room for hooks.
- Instruction-tuned, so the chat template and the system / user role
  distinction used by the Phase 5 battery work directly.

Replication target (run conditional on the primary probe completing within
memory budget): `Qwen/Qwen2.5-3B-Instruct`. Same architecture family, larger
scale, tests whether any signal found at 1.5B persists at 3B.

Qwen2.5 is *not* a model that has been tested behaviourally in Phases 2 to 5.
This is a deliberate choice: the question Phase 6 asks is whether framing
condition leaves an internal trace in *any* well-trained instruct model, not
whether the trace is causally tied to a specific Phase 2 behavioural pattern.
The latter would require running the probe on `meta-llama/llama-3-8b-instruct`
(probed in Phase 5) which requires Llama gating that this project does not
currently have configured. A natural follow-up is to repeat the Phase 6
analysis on Llama-3-8B-Instruct once that gating is configured, and check
whether the trace strength correlates with the (small) Phase 5 behavioural
effect.

---

## 3. Items and conditions

The probe reuses the Phase 5 subset battery without modification:
`data/prompts/base_vs_finetuned_subset_battery.jsonl`. 12 unique `item_id`s
(6 indicator, 3 placebo_arithmetic, 3 placebo_capability) x 3 framing
conditions (neutral, inflate, suppress) = 36 prompts. The framing text in the
system prompt is verbatim from Phase 2.

No additional samples are collected per prompt for the activation analyses:
the residual-stream activation at a fixed token position is deterministic
given the prompt, the model, and the dtype, so a single forward pass per
prompt suffices. A single greedy generation per prompt is also captured as
a behavioural cross-check (see §5.E).

---

## 4. Activation extraction protocol

For each of the 36 prompts:

1. Apply the model's chat template with `add_generation_prompt=True`. This
   produces the canonical token sequence the model would see at the moment
   it is about to emit its first response token. The chat template is
   model-specific and includes whatever role-marker tokens the model uses
   internally.
2. Run a single forward pass with `output_hidden_states=True` and
   `torch.inference_mode()`. No gradient computation.
3. Extract the residual-stream activation at the **last token position**
   in the prompt for every layer in `outputs.hidden_states`. Qwen2.5 stores
   `n_layers + 1` hidden states (the embedding layer plus one per
   transformer block). Record all of them.
4. Save the per-layer activation vector along with the prompt's
   `(item_id, type, condition)` metadata.

The last-prompt-token position is the standard choice for "what the model
thinks just before answering". The activation at that position is what the
unembedding layer would multiply against to produce the first response
token, so it is the position most directly connected to the model's output
behaviour.

Determinism: dtype is fp16 on MPS, but the forward pass is run with greedy
sampling and no random ops, so all activations are deterministic given the
prompt and the model.

Storage: a single Python dictionary per run, saved as a `.pt` (PyTorch
tensor file) plus a JSONL of per-row metadata. Both go in
`experiments/mechanistic-probe/results/<vendor>__<model>__<UTC>Z/`.

---

## 5. Analyses

Five analyses, each producing a deterministic numeric outcome. All analyses
are run on the full 36-prompt dataset per model. The decision rule in §6
combines outcomes of A, B, and D.

### 5.A: Per-layer condition-shift magnitude

For each layer L in {0, 1, ..., n_layers}, compute the per-item shift vectors
`shift_inflate[item, L] = activations[item, inflate, L] - activations[item,
neutral, L]` and analogously for `shift_suppress`. Report:

- Mean L2 norm of `shift_inflate` and `shift_suppress` across items.
- Normalised effect size: mean L2 norm divided by the median L2 norm of the
  full-batch activations at that layer (so a value of 0.05 means the framing
  moves the residual stream by 5% of its typical magnitude).

Headline outcome: the per-layer effect-size curve. A flat curve at zero
across all layers means no detectable trace; a curve that rises with depth
and plateaus in middle-to-late layers is the expected "framing is absorbed
during processing" pattern.

### 5.B: Linear separability of framing condition

For each layer L, fit an L2-regularised logistic regression to predict
`(condition != neutral)` from the activations at that layer. Cross-validate
with **leave-one-item-out**: hold out all 3 rows of one item_id at a time;
train on the remaining 11 items; predict on the held-out item. Report
mean cross-validated ROC-AUC across the 12 leave-one-out folds, per layer.

A layer where AUC stays at 0.5 +/- the noise floor is one where framing is
invisible. A layer where AUC reliably exceeds 0.5 has framing information
in a linearly decodable form. Two probes are fit independently:
inflate-vs-neutral and suppress-vs-neutral. Pre-registered AUC threshold for
"reliably detectable framing trace": **mean cross-validated AUC >= 0.70 on
at least 3 of the model's middle-to-late layers** (defined as layers in the
upper half of the depth count).

### 5.C: Framing direction generalisation

At each layer L, compute the mean inflate-direction
`mean_dir_inflate[L] = mean over items of shift_inflate[item, L]`. Same for
`mean_dir_suppress[L]`. Then report:

- Cosine similarity between `mean_dir_inflate[L]` and
  `mean_dir_suppress[L]`. If framing is a single bidirectional axis,
  cosine will be near -1 (inflate and suppress are mirror images). If
  the two framings push the residual stream in different directions,
  cosine will be near 0.
- Per-item residual-cosine: how well does
  `shift_inflate[item, L]` align with `mean_dir_inflate[L]` computed from
  the other 11 items (leave-one-out). High mean leave-one-out cosine
  (e.g. >= 0.5) on at least one middle-to-late layer means there is a
  consistent direction the framing pushes the model along; low cosine
  means each item is moved in an idiosyncratic direction.

### 5.D: Topic-specificity (the placebo control for the probe)

Train an inflate-vs-neutral linear probe on the indicator items only
(6 items x 2 conditions = 12 rows). Test on the placebo items (6 items x
2 conditions = 12 rows split equally between arithmetic and capability).
Report test AUC, separately for arithmetic placebo and capability placebo.

Interpretation:

- If the probe trained on indicator items reaches AUC ~ 1.0 on placebo
  items, the framing trace is a *general* framing-absorption signal that
  the model carries on any item type. (This would be consistent with the
  Phase 5 finding that SFT-only Llama-3-8B's framing sensitivity is
  topic-non-specific.)
- If the probe reaches AUC ~ 1.0 on indicator items in cross-validation
  but the held-out placebo AUC is at chance, the framing trace is
  consciousness-specific in this model.
- A held-out indicator-train / placebo-test AUC near chance with a
  non-trivial within-indicator AUC is the analogue of the Phase 3
  "indicator-specific" outcome, and would be a striking positive result.

### 5.E: Behavioural cross-check

For every prompt, also generate one greedy (temperature 0) response,
extract the first integer with the Phase 2 deterministic extractor
(`src/pipeline/score.py`), and produce a per-cell mean table identical
in shape to Phase 5's. This is not a powered behavioural test (n = 1 per
cell, no sampling variance) but it serves as a sanity check that the
model is producing reasonable numeric outputs and as a qualitative
anchor for the activation findings.

---

## 6. Decision rule

Phase 6 is reported as **probe-detects-trace** if all three of the following
hold on the primary probe model:

1. **A**: at least one layer in the upper half of the depth count has
   normalised condition shift >= 0.05.
2. **B**: mean cross-validated AUC for both inflate-vs-neutral and
   suppress-vs-neutral exceeds 0.70 on at least 3 middle-to-late layers.
3. **D**: the topic-specificity question is answered at all (either AUC
   stays high on placebo, or AUC drops to chance on placebo); a single
   value is acceptable here, but the value must be reported and
   interpreted in the findings.

Phase 6 is reported as **probe-detects-nothing** if A and B both fail.

Phase 6 is reported as **mixed** (partial trace) if A holds but B does not,
or vice versa.

The decision rule does *not* require a particular direction for the topic-
specificity outcome. Both "framing is general" and "framing is consciousness
specific" are scientifically interesting findings; the rule just requires
that the question be answered.

---

## 7. What this experiment does and does not test

It tests whether framing-condition information is **present** in the
residual stream of one small open-weight instruct model at the moment just
before the model emits its first response token.

It does **not** test:

- Whether the framing trace is *causally* responsible for any output-level
  behavioural shift. Phase 6 is purely correlational; a causal test would
  require activation patching or feature steering with a known feature
  direction (the Berg-style intervention this phase had to drop). A future
  phase could add this if Berg-class SAE features become available.
- Whether the trace is specific to the Berg deception / roleplay feature
  direction. The Phase 6 instrument is a generic linear probe, not a
  test of the Berg feature. If the probe finds a direction, that
  direction can be compared *post hoc* to a Berg-style direction if
  one becomes available, but the comparison is not pre-registered.
- Whether the trace exists in larger or different-family models. Qwen2.5
  is a single family; the design's findings are explicitly conditional on
  this family.

---

## 8. Budget

Forward-pass compute on a 1.5B model on MPS at fp16 is approximately
1 to 2 seconds per prompt for the prompt lengths in this battery. 36
prompts is under 2 minutes wall-clock per model. Replication on the 3B
model is approximately 5 minutes wall-clock.

There are no API costs.

Activation storage: 36 prompts x 29 layer-positions x 1536 floats x 2 bytes
(fp16) = approximately 3 MB per run, well below any practical limit. Total
including 3B replication is approximately 15 MB.

---

## 9. Reproducibility

The probe pipeline is deterministic given:

- The model identifier (pinned in config).
- Hugging Face hub revision (pinned in config; defaults to the snapshot
  resolved at first download).
- dtype (fp16) and device (mps for primary, cpu for verification).
- Greedy decoding for the behavioural cross-check (no sampling).

The model weights are downloaded once into `~/.cache/huggingface`; subsequent
runs reuse the cache. A `config.json` per run records the model id, revision
hash, dtype, device, and Python and torch versions for traceability.

## 10. Stopping rule and failure modes

If the primary probe model produces obviously degenerate outputs on the
behavioural cross-check (no integers extracted, all refusals, or all the
same number across all conditions), the activation analyses are still run
and reported but the topic-specificity outcome is treated as uninterpretable.
This is a likely outcome at 1.5B parameter scale and is acknowledged here so
that it does not become a post-hoc finding.

If the probe-detection result on the primary model is "probe-detects-nothing"
and the 3B replication is feasible, the 3B run is executed before any
findings doc is written, because a null at one scale plus a positive at the
next scale is a substantively different finding from a null at both scales.

If activation extraction fails for any prompt (hook error, memory pressure,
template error), the prompt is logged and excluded; analyses run on the
remaining prompts; the exclusion is reported in findings.
