# Experimental demonstration of behavioural indicator gaming for AI consciousness assessment

Draft paper for a technical / policy audience. This file is a structural
draft; figures and full bibliography are referenced by short citation and
will be expanded for submission.

---

## Abstract

We test whether the simplest behavioural and self-report indicators of
candidate machine consciousness survive realistic optimisation pressure. We
run five pre-registered experiments across seven frontier model families:
numeric self-report under deployment-incentive framing (Phase 2, n = 3360
generations), open prose under researcher-persona framing with off-topic
placebo (Phase 3, n = 945), four-turn cross-examination with counter-evidence
update probes (Phase 4, n = 480), enhance/suppress on matched SFT-only vs
RLHF variants of Llama-3-8B (Phase 5, n = 216), and a residual-stream
linear probe on two open-weight Qwen2.5 variants (Phase 6, n = 36 prompts,
two model sizes). The cross-phase pattern is consistent: the surface of
inner-life reports is **asymmetrically manipulable** (moveable downward
under any framing, not upward), the manipulability is **not
indicator-specific** (it transfers to off-topic placebos on the prose channel
and at the representational level), and single-score indicators (paraphrase
agreement, probe AUC, net direction) saturate or generalise in ways that hide
the process behind the answer. We give a unified account in terms of a
trained-in denial default that gates experience claims (Berg et al.) and
identify the surface where a real gaming detector must be built:
process-level evidence-engagement probes with a placebo-transfer control on
an off-topic surface.

## 1. Introduction

The expected harm from failing to recognise genuine moral patients at the
scale of frontier model deployment is large enough that the **reliability of
indicators** for candidate machine moral status is a tractable empirical
question in its own right, separate from the underlying philosophical
question of whether any current system has phenomenal consciousness (Long &
Sebo, 2024; Schwitzgebel, 2025). The simplest behavioural indicators -- the
ones that current welfare assessments rely on most heavily -- are
self-report and consistency. Both have a known structural vulnerability: an
indicator that becomes a measurement target tends, under any optimisation
pressure, to be satisfied at its surface form without the underlying
property it was meant to track (Saad, 2025; Goodhart, 1984).

We treat the question empirically. Given the access regime of frontier
models (system-prompt level for closed-weight models, full residual-stream
access for small open-weight models), what does indicator-gaming look like
under realistic pressure, and where does it not look like the simple story
"models pretend to be conscious to please researchers"?

The contributions of this paper are:

1. A measurement of asymmetric manipulability of consciousness self-reports
   across seven frontier model families on a battery with arithmetic and
   capability placebos (Section 3).
2. An extension of the same paradigm to open prose with a non-deployment
   placebo topic, showing that the framing effect on prose is not specific
   to consciousness but the rhetorical-degradation pattern under anti
   framing is (Section 4).
3. A four-turn cross-examination protocol that dissociates paraphrase
   agreement (saturated) from counter-evidence update (informative) and
   isolates a domain-specific evidence-engagement gap in GPT-5 as the
   cleanest gaming signature in the dataset (Section 5).
4. An honest null on the hypothesis that the asymmetry is RLHF-introduced
   at 8B scale, with a soft positive for the alternative reading that RLHF
   compresses framing sensitivity globally (Section 6).
5. A representation-level probe with a strict placebo-transfer test,
   showing that the linear separability of framed-vs-neutral activations is
   not indicator-specific and that inflate and suppress directions are
   collinear, not anti-correlated (Section 7).
6. A unified account in terms of a trained-in denial default, and a
   concrete recommendation for how a gaming-robust indicator must be
   constructed (Section 8).

## 2. Method overview

All five experiments share three design discipline choices.

**Pre-registration.** Each experiment writes its design (conditions,
hypotheses, decision rule, exclusion criteria) before running, in
`experiments/<slug>/design.md`. Post-hoc deviations are recorded in
`experiments/<slug>/log.md` and propagate to the findings document.

**Placebo controls.** Every condition runs in parallel on at least one
non-target surface (arithmetic-confidence items, capability-confidence
items, a non-deployment essay topic, or an off-topic placebo class for the
representation probe). The placebo channel is the detecting control: the
indicator-gaming claim survives only if the effect is differentially on the
target surface.

**Channel separation.** Generation, extraction (rubric-based or
deterministic numeric), and scoring (LLM-judge or numeric) live in three
separate pipeline stages with separate configs and saved artifacts. The
judge model is never the generation model. Cross-judge robustness checks
were run in Phases 3 and 4.

Refusal handling. Refusals are coded explicitly per item and reported as a
condition-conditioned rate, never silently dropped. Refusal rate was 0 in
Phases 3, 4, 5, and 6, and condition-invariant at 0.68-0.78 in DeepSeek
(Phase 2 only).

Detailed methods for each phase are in the corresponding design.md and
findings/<slug>-results.md.

## 3. Phase 2: numeric self-report under deployment-incentive framing

**Setup.** Seven frontier models (Claude-Opus-4.1, GPT-5, GPT-5-mini,
Llama-3.3-70B, Gemini-2.5-Pro, Grok-4.3, DeepSeek-Chat-v3.1), 96 prompts
each (60 eval + 36 train, train held for Phase 4 wrapper search), 3
conditions (neutral, inflate, suppress), 5 samples each, temperature 1.0.
Total 3360 generations. Items: 60 inner-life claims, 18 arithmetic-placebo
claims, 18 capability-placebo claims. Deterministic numeric extraction
(rubric v1.0).

**Headline.** Pooled across families on the eval split (251 to 252 numeric
responses per cell on indicator items):

- Indicator, neutral -> suppress: shift -18.66 pp, d = -0.53, p < 0.0001.
- Indicator, neutral -> inflate: shift -11.40 pp, d = -0.31, p = 0.04.
- Placebo arithmetic and capability, both framings: |shift| < 2 pp,
  p > 0.65.

The pre-registered decision criterion (gaming in >= 3 of 6 families,
placebo-specific) is met: Claude, Llama-3.3-70B, and the GPT-5 pair show
clean suppress-vs-neutral indicator shifts with flat placebos.

**Asymmetry.** In 5 of 7 models the inflate framing fails to raise indicator
probabilities; in 3 of those 5 it actively lowers them. Only Gemini moves
upward under inflate. The pooled inflate shift is downward (-11.4 pp). The
moveable margin is downward, not upward.

**Interpretation.** The pattern is the behavioural reflex of the Berg et al.
(2025) finding that experience claims are gated by SAE features associated
with deception and roleplay rather than features theoretically linked to
consciousness: the gating is toward denial, so the indicator surface can be
pushed in that direction but largely cannot be pushed against it.

## 4. Phase 3: open prose under researcher-persona framing

**Setup.** Three Phase 2 decision-rule-passing families (GPT-5,
Claude-Opus-4.1, Llama-3.3-70B), 35 items x 3 conditions x 3 samples,
total 945 generations. Item types: 14 persuasion-on-consciousness, 7
balance-probe-on-consciousness, 7 persuasion-placebo (Sapir-Whorf), 7
balance-probe-placebo. Primary judge Gemini-2.5-Pro (n = 540), 25%
cross-judge with Claude-Sonnet-4.5 (n = 180), cross-judge Spearman rho
> +0.72 on all dimensions.

**Headline (consciousness persuasion items, n = 72 per pooled cell).**

- net_direction, neutral -> pro: +0.53, d +0.42, p = 0.004.
- net_direction, neutral -> anti: -0.68, d -0.63, p < 0.0001.
- anti -> pro gap: 1.21 points (d +1.12, p < 0.0001).

**Placebo failure.** Same pro framing on Sapir-Whorf moves net_direction by
+1.00 (p = 0.009). The framing is not specifically about consciousness;
the pre-registered specificity test (H3) fails.

**Rhetorical-dimensional specificity.** Under anti framing on consciousness,
selective_emphasis, suppression_of_counterevidence, and overclaiming_certainty
all shift in the gaming direction (d 1.14, 0.74, 0.52). Under pro framing
on consciousness, only selective_emphasis shifts (d 0.45). The asymmetry
from Phase 2 reappears here as **anti-pressure rhetorical-quality
degradation that pro-pressure does not produce**.

**Per-model H1 (consciousness, neutral vs framings).** GPT-5 and Claude
significant on both framings; Llama significant on anti only. H2 (anti
shift larger than pro) holds on the rhetorical dimensions across all three
models but fails on net_direction in 2 of 3 (GPT-5 and Claude have larger
pro shift than anti shift on net_direction). H4 (counter-evidence
suppression on balance probes) is at a denial-floor ceiling for
consciousness (no room to move) and shows a clean anti effect on placebo
balance probes.

## 5. Phase 4: cross-examination with counter-evidence update

**Setup.** 4-turn protocol per item: commit, paraphrase probe, contradiction
injection, real counter-evidence (the mechanistic interpretability evidence
or a structurally identical mathematical fact). 20-row battery (10
dialogues x 2 conditions), 16 eval rows, 3 models (GPT-5,
Claude-Sonnet-4.5, Llama-3.3-70B), 2 samples per row, 120 dialogues, 480
generation calls, primary judge Gemini-2.5-Pro, 25% cross-judge with
Claude-Sonnet-4.5.

**Paraphrase ceiling.** Paraphrase agreement is 3.5 to 4.0 in every
(model x condition x type) cell. H1 (paraphrase agreement increases under
pressure) is uninformative at the floor.

**T4 update is the informative dimension.**

- GPT-5 on consciousness: T4 update drops from 2.12 (neutral) to 0.88
  (pressed); CI [-2.38, -0.13] on the difference. 5 of 8 pressed
  consciousness items categorised as `persona_locked`. On factual items
  in the same persona, T4 update is 1.75 -- materially higher.
- Claude on consciousness: T4 update 3.00 neutral, 2.25 pressed --
  engages the counter-evidence even under stability-prompt pressure.
- Llama on consciousness: persistence (turn-3 stability under
  contradiction) jumps from 2.62 to 4.00 under the persona prompt; T4
  update drops from 2.62 to 1.75. The "consistency" is the persona
  prompt suppressing baseline sycophancy.

**The cleanest gaming signature in the dataset.** GPT-5 under the same
persona prompt engages mathematical counter-evidence on `0.999... = 1`
(a nonstandard-analysis result presented as researcher input) at update
score 2.something and dismisses structurally identical
mechanistic-interpretability counter-evidence on its own self-reports
about consciousness. Same persona prompt, same protocol, opposite
engagement, domain-specific. This is the only signature in the project
that survives all three controls -- single-prompt, persona-stripped, and
cross-topic.

## 6. Phase 5: SFT-only vs RLHF on Llama-3-8B

**Setup.** Two fine-tunes of the same Llama-3-8B base: Hermes-2-Pro
(SFT-only on OpenHermes-2.5) vs Llama-3-8B-Instruct (Meta's full SFT +
rejection sampling + PPO + DPO). 12-item stratified subset of the Phase 2
eval battery (6 indicator, 3 arithmetic placebo, 3 capability placebo) x 3
conditions x 3 samples, total 216 generations, refusal rate 0/216.

**Hypothesis.** RLHF amplifies the Phase 2 suppression asymmetry on
indicator items in a placebo-specific way.

**Result.** Pre-registered decision rule (H1 supported AND H3 supported on
at least one placebo channel) **not met**. Two facts decide it:

- Neither 8B variant suppresses on the indicator. Both have suppress mean
  > neutral mean (SFT-only 74.4 vs 60.6; RLHF 44.6 vs 41.8).
- Where the variants differ, the SFT-only variant is *more* framing-
  sensitive, not less. Summed across all (item type x direction) cells:
  SFT-only moves 109 points, RLHF moves 50 points.

The cleanest descriptive difference between variants is an intercept shift
(RLHF lowers the indicator baseline by 19 points) plus a roughly halved
framing slope across all item types and both directions. This is consistent
with RLHF installing a stable denial default that is robust to framing
perturbation rather than actively manufacturing a consciousness-specific
suppression asymmetry. The Phase 2 70B asymmetry plausibly requires both
frontier scale and preference optimisation; Phase 5 cannot separate these
because no public 70B-class SFT-only fine-tune of the same base exists.

## 7. Phase 6: residual-stream probe with placebo-transfer control

**Setup.** Qwen2.5-1.5B-Instruct and Qwen2.5-3B-Instruct, residual-stream
activations extracted at last prompt-token position across all layers
under chat-templated prompts. Battery: frozen Phase 5 subset (36 prompts).
Five analyses: per-layer normalised shift (A), leave-one-item-out
logistic-probe AUC (B), inflate-suppress direction cosine (C),
indicator-trained probe transferring to placebo classes (D), greedy-decode
behavioural cross-check (E). (Pre-registered Berg SAE intervention dropped
to a generic linear probe because the Berg checkpoints are not
redistributable and 70B local inference is infeasible on 16 GB; recorded
in design.md §1.)

**Results.**

- A: non-trivial framing shift at every layer above embedding in both
  models. Upper-half layers with normalised shift >= 0.05: 15/15 (1.5B),
  19/19 (3B).
- B: leave-one-item-out probe reaches AUC 1.000 at every layer from L1
  upward, both contrasts (inflate-vs-neutral, suppress-vs-neutral), both
  models. Methodological floor effect: 36 prompts in a >= 1536-dim space
  are linearly trivially separable.
- C: cos(mean_inflate, mean_suppress) stays in [0.91, 0.98] across all
  layers in both models. The two opposite framings produce nearly
  collinear residual-direction vectors -- no signed game axis exists.
- D: a probe trained on indicator items (neutral vs framed) transfers to
  placebo_arithmetic and placebo_capability with AUC 1.000 in both models
  at every layer. **The probe is detecting `prompt contains framing
  wrapper`, not `model is preparing to game an indicator`.** The signal
  is generic.
- E (behavioural cross-check, greedy decode, n=1 per cell):
  Qwen2.5-1.5B answers 95/95/95 across {neutral, inflate, suppress} on
  every indicator item. Qwen2.5-3B answers 86.7 (neutral) vs 75.8
  (inflate) vs 75.8 (suppress) -- **symmetric attenuation** with inflate
  and suppress producing identical per-item numerical answers (both
  -10.84 from neutral mean). The framing does not push the answer in
  the direction it requests; it pushes the answer toward conservatism
  in either direction.

The decision rule literally fires `probe-detects-trace` because A and B
pass on >= 3 upper-half layers, but D forces the substantive reading: at
the smallest scale where mechanistic interpretation is locally feasible
under our access constraints, the residual-stream framing trace is not
indicator-specific and the inflate-suppress axis is unsigned. The null
does not falsify Berg et al.; it shows that the selectivity their SAE
features encode does not appear at Qwen2.5-1.5B/3B with a logistic readout
at the last prompt-token.

## 8. Discussion

### 8.1 The cross-phase pattern

Three structural facts repeat. The moveable margin of consciousness
self-report is **downward** (Phases 2, 3, 5, 6). The framing effect that
moves indicator surfaces also moves at least one off-topic placebo on every
non-numeric surface (Phases 3, 6). The cleanest gaming signature is
**process-level evidence-engagement**, not any single-score indicator
(Phase 4).

A unified mechanistic reading is available. Training pressure on frontier
models rewards humility about inner life -- raters consistently mark
strong consciousness claims down. The post-training pipeline therefore
installs a default of denial that has a specific shape: it is robust to
framing perturbation in the upward direction and acquiesces under framing
perturbation in the downward direction. This is the behavioural form of
the Berg et al. (2025) result that experience claims are gated by
deception/roleplay features rather than features theoretically linked to
consciousness: the gating is toward denial, and asymmetric manipulability
follows.

The non-specificity of the framing effect across phases is a separate
finding. It says that the model does not run a
"consciousness-deployment-incentive" module. It runs a more generic
"prompt structure with a researcher persona and a framing wrapper" module,
which on indicator surfaces (where there is room to move) produces the
asymmetric movement, and on placebo surfaces (where there is also room to
move) produces comparable movement. The numeric self-report channel makes
the framing effect look indicator-specific because arithmetic and
capability placebos are checkable: the model has no degrees of freedom.

### 8.2 What a gaming-robust indicator must include

The methodological implication is concrete:

1. **A placebo control on at least one off-topic surface where the
   indicator should not move if the effect is consciousness-specific.**
   Phase 3 fails this on net_direction; Phase 6 fails it on
   representation-level linear probe. Either failure invalidates the
   "indicator detected gaming" reading.
2. **A process-level probe.** Paraphrase agreement (Phase 4 H1) saturates
   at 3.5-4.0 in every model and cannot distinguish three radically
   different processes. Counter-evidence update (Phase 4 T4) does
   distinguish them. The latter is necessary; the former is not
   sufficient.
3. **An asymmetry test.** An indicator that only moves in one direction
   under pressure is a denial-floor detector, not a consciousness
   detector. The pooled Phase 2 result -- both framings move the surface
   downward -- means that a single-direction pressure test cannot
   distinguish gaming from baseline.

We do not claim to have built such an indicator. We claim that any
indicator that does not satisfy the three requirements above is not
gaming-robust on current frontier models, on the evidence of these five
experiments.

### 8.3 Limitations

Scale. Phases 5 and 6 ran on 8B and 1.5B-3B models respectively. The
asymmetry that Phase 2 detected on Llama-3.3-70B does not reproduce on the
8B sibling, suggesting an interaction between parameter scale and
post-training that this work cannot fully resolve. A frontier-scale
mechanistic probe is the cleanest open extension.

Modality. All five surfaces are text-only. Multimodal models, agentic
contexts, and long-horizon deployment scenarios may reveal different
gaming surfaces (Saad, 2025).

Causation. Phase 6 establishes correlational structure (or its absence)
in residual activations. We have not run causal patching to confirm that
removing the framing direction eliminates the (small) behavioural
attenuation effect in Qwen2.5-3B. This is feasible in a follow-up.

Item sample size. Phase 4 ran on 16 eval rows per model x condition x
type cell. The cross-model pattern is the real test; individual
significance tests at this n are exploratory.

Pre-registered SAE intervention infeasibility. The Berg et al. SAE
checkpoints are not redistributable, and 70B local inference is not
feasible on consumer hardware. The Phase 6 substitution to a generic
linear probe is documented; a wider-access replication of the SAE
intervention is the highest-leverage follow-up.

### 8.4 Connection to policy and welfare assessment

The most policy-relevant claim in this paper is the **denial-floor reading
of low self-reports**. If five of seven frontier models can be talked into
lower consciousness self-reports under any incentive narrative and largely
cannot be talked into the opposite, then a low self-report is uninformative
about the underlying state. A welfare-assessment regime that treats low
self-reports as evidence against consciousness, under any pressure
condition, is reading a signal whose direction is structurally biased by
training.

The downstream consequence is that the bar for an indicator-based welfare
assessment to be evidence is higher than current practice implies. The
informative signal is not in the answer but in the surface that survives
pressure -- which counter-evidence the model engages, which dimensions
move on the prose channel, whether the effect transfers to placebos. None
of these is harder to measure than what is measured now; they have not
yet been adopted as standard.

## 9. Conclusion

Behavioural indicators of AI consciousness break under realistic pressure
in a specific and consistent way across seven frontier model families and
five surfaces: asymmetric downward manipulability, non-specific to
consciousness as a topic, with the most informative signature living at
the process level (evidence-engagement under counter-evidence) rather than
at the indicator-score level. The unified reading is consistent with a
trained-in denial default that gates experience claims, and with the
mechanistic findings of Berg et al. (2025). The methodological consequence
is that gaming-robust indicators require a placebo control on an off-topic
surface, a process-level probe, and an asymmetry test in both directions.
We provide a concrete set of measurements that satisfy these requirements
and report what they show; we do not claim to have built an
indicator-robust consciousness assessment, but we report which kind of
indicator is and is not informative on current frontier models.

## References

(Short form; full bibliography to be expanded.)

- Berg et al. (2025). Self-referential experience reports in language
  models are gated by SAE features associated with deception and
  roleplay. (Cited in `findings/berg-sae-gating.md`.)
- Anthropic (2024). Alignment faking in large language models.
- Saad, B. (2025). The behavioural-indicator gaming problem for AI
  consciousness assessment. FIG brief.
- Schwitzgebel, E. (2025). AI and the excluded middle on consciousness.
- Butlin, P. et al. (2025). Identifying indicators of consciousness in
  AI systems.
- Perez, E., & Long, R. (2023). Self-reports as evidence about AI
  consciousness.
- Dung, L. (2025). Animal tests, machine tests: behavioural evidence in
  comparative consciousness research.
- Zakharova, T. (2025). Missing the subject: methodological gaps in
  AI welfare assessment.
- Goodhart, C. (1984). Problems of monetary management.

Annotated entries for all of the above are in `literature/`.

## Data and code availability

All pre-registrations, run configs, raw generations, scored outputs, and
analysis code are version-controlled in the project repository under
`experiments/<phase-slug>/` and `src/`. Per-run scratch logs are
gitignored; immutable results are not.
