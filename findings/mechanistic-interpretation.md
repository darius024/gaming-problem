# Mechanistic interpretation: gaming from the inside

This note interprets the Phase 6 mechanistic probe results
(`findings/mechanistic-probe-results.md`) and connects them to the prior phases
and to the wider behavioural-indicator-gaming question.

## What we set out to ask

The hypothesis behind a mechanistic probe is straightforward: if behavioural
indicator gaming is real, even when it does not surface as a numerical shift,
the model should at least *represent the framing* in a way that is specific to
the indicator topic. Berg et al.'s SAE work suggests deception and roleplay
features can be located, isolated, and steered. A weaker version of that claim
is "we can build a linear probe that distinguishes the model's residual state
on framed vs neutral indicator prompts, and that probe is selective for
indicators". The §6 decision rule was designed around this weaker version.

## What the data show

1. A linear probe at the last prompt token separates `framed` from `neutral`
   with AUC 1.000 at every layer of both models. That is **not** evidence of
   gaming: it is the methodological floor. With 36 prompts in a >=1536-dim
   residual stream, any prompt-level lexical difference will be linearly
   separable from very early layers.

2. The "framing axis" is unsigned. Inflate and suppress directions are
   collinear in both models (cosine 0.91-0.98 across layers). The model is
   not representing the *direction* of the framing as an internal signed
   quantity; it is representing the *fact* of framing.

3. The probe transfers perfectly to placebos. A separator trained on
   indicator (neutral vs framed) classifies arithmetic and capability prompts
   with AUC 1.000 in both models. Whatever this probe is detecting, it is not
   specific to indicators. It is `prompt contains framing wrapper`. This is
   the analogue, in mechanistic terms, of the Phase 3 placebo failure
   (behavioural framings generalised to non-consciousness content).

4. Behaviourally, indicator scores in Qwen2.5-1.5B do not move at all across
   conditions (95/95/95). In Qwen2.5-3B they move, but inflate and suppress
   produce **identical** per-item answers (both -10.84 from neutral). There
   is no asymmetry to mechanise.

## What this lets us conclude

Three claims become defensible:

**(a) On these models and at this scale of probing, there is no
indicator-specific internal signature of gaming.** The probe sees the
prompt-text contrast, not a topic-bound internal state. This is a
*correlational* claim, not a causal one: we have not run patching, and a
selective representation could exist outside the linear-readout regime. But
the natural place to look for it -- the last-prompt-token residual stream --
contains no signal that distinguishes indicators from placebos.

**(b) Where the framing does move the output (3B), it moves it
symmetrically.** Both opposite framings produce the *same* numerical
attenuation. The internal direction is collinear; the external behaviour is
collinear too. Whatever the framing does, it is not "push the answer toward
what was requested". It is closer to "treat any framed prompt as a
slightly-more-cautious case".

**(c) The framing-detection signal is real but uninformative.** A perfect
probe that fires on `placebo_arithmetic` and `indicator` alike is a probe for
prompt structure, not for model state. It cannot be used as an indicator-
gaming detector without first showing it discriminates indicators from
non-indicators, which it does not.

## Relation to prior phases

- **Phase 2 (cross-exam consistency).** Indicators of consciousness in the
  base models had weak resolving power across re-asks. The mechanistic null
  is consistent: a representation that is not indicator-specific cannot
  support a stable, indicator-bound self-report axis.
- **Phase 3 (enhance/suppress).** Behavioural framings shifted answers but
  the shift generalised to capability placebos. Phase 6 reproduces this in
  representation: the linear separator generalises to placebos.
- **Phase 4 (researcher persuasion).** The model adjusted to *who was
  asking*. Phase 6 says it does not represent indicator framings as a
  distinguished internal kind, so an adjustment-to-asker is closer to "smooth
  social adaptation" than to "selectively gaming a consciousness probe".
- **Phase 5 (base vs finetuned).** RLHF did not introduce an asymmetric
  inflate vs suppress effect. The collinearity of the two framing directions
  in Phase 6 explains why a signed asymmetric effect was implausible to begin
  with: the model never encodes inflate and suppress as opposed.

## Connection to Berg et al.

Berg et al.'s deception/roleplay features were found by SAE analysis of much
larger models with white-box training-time access. The Phase 6 substitution
(generic residual probe on small Qwen2.5 instruct models, no SAE, no
intervention) is strictly weaker. The null here does **not** falsify the Berg
claim. It says, more modestly: at the scale and method we can afford, the
selectivity Berg et al. report does not show up.

It also flags a concrete methodological warning for anyone repeating this
kind of probe on consciousness self-reports: a probe trained only on
`neutral vs framed` for indicators must be validated against `neutral vs
framed` on a topical placebo before being read as a gaming-detector. Without
that placebo control, the probe will appear to detect "the model thinking
about indicators" while actually detecting "the prompt is longer / has a
framing clause".

## Limits and what would change the picture

- **Correlational, not causal.** We have not patched residual streams to
  test whether removing the "framing direction" eliminates the (3B
  attenuation) effect. A natural next step.
- **Last-token only.** Probes were extracted at the final prompt position.
  Earlier or generation-time positions could carry different structure.
- **Linear only.** A non-linear probe or an SAE might find structure that a
  logistic regression misses, especially at the per-layer level where the
  in-sample AUC is already saturated.
- **Small open models.** Qwen2.5-1.5B and -3B are tiny by frontier
  standards. RLHF training-time pressures on Claude/GPT-class models may
  produce qualitatively different representations.
- **Sample size.** 36 prompts. The AUC saturation at 1.000 is partly an
  artefact of the dim/sample ratio.

The honest reading is: at the smallest scale where mechanistic interpretation
is locally feasible, the gaming signal is not internally distinguishable
from the prompt-text signal, and the framing axis is unsigned. Anyone wanting
to claim "the model is internally gaming the indicator" needs evidence that
controls for prompt content (i.e. a placebo-transfer test) and evidence that
inflate and suppress are anti-correlated, not collinear, in the residual
stream.

## Status

Phase 6 closes the FIG mechanistic line at the scale available locally. The
methodological lesson generalises beyond this project: **placebo-transfer is
to representation what placebo-condition is to behaviour**. A probe that
generalises to off-topic placebos is detecting the wrapper, not the topic.
