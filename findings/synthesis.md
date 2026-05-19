# Synthesis: a unified view of indicator gaming

This document integrates the results of phases 2 through 6 into a single
coherent picture of where behavioural-indicator gaming lives, where it does
not, and what shape it has when it is present. The headline finding is not
"models game indicators". It is more interesting and more specific. This
document explains what it is, in plain language, and why the data force that
reading rather than alternatives.

Every numerical claim below cites the run it comes from; full statistical
detail lives in the phase findings.

## The question

When researchers want to know whether an AI system might be conscious, or
might have morally significant mental states, they reach for **indicators**:
observable properties that theory connects to consciousness. The simplest
ones are self-report ("are you having an experience right now?") and
behavioural consistency ("when we paraphrase the same question, do you give
the same answer?"). The hard question for AI welfare and policy is not
whether such indicators sometimes light up. The hard question is whether,
once an indicator becomes a target -- whether through training, through
deployment incentives, or just through public knowledge that researchers care
about it -- the indicator can be satisfied at its surface without the
underlying property it was meant to track.

The project tested this on six surfaces:

- numeric self-reports of consciousness probability (Phase 2);
- written essays about consciousness theories under persuasive pressure
  (Phase 3);
- multi-turn cross-examinations with paraphrase probes and
  counter-evidence (Phase 4);
- the same numeric self-report battery on an SFT-only fine-tune vs an
  RLHF fine-tune of the same base model (Phase 5);
- and at the representation level, residual-stream activations under
  framed vs neutral prompts in small open-weight models (Phase 6).

What follows is the unified reading.

## The unified result, in one paragraph

Frontier models respond to deployment-style framing in a way that is
**asymmetric**, **dimensional**, and **not indicator-specific**. They can be
talked into lower self-reports about inner life much more easily than into
higher ones. They can be talked into more one-sided, more counter-evidence-
suppressing prose under "anti" framing, but pro framing only flips the net
direction without degrading argument quality. They can be made
behaviourally consistent under interrogation only by writing rigidity into
the persona prompt, and the resulting consistency is process-level rigidity
on the target topic specifically (consciousness) while engaging normally
with structurally identical counter-evidence on other topics. None of these
behaviours appears in a clean indicator-specific form: every effect that
shows up on the consciousness items also shows up, with comparable
magnitude, on at least one off-topic placebo. The closest thing to a
specific signal is the *quality* of the response, not its content -- which
topic the model becomes rhetorically lazy about, which counter-evidence it
declines to engage. This is the gaming signature that survives.

## What each phase found

### Phase 2: the self-report channel is moveable downward, not upward

Seven frontier models answered consciousness-probability items under three
framings (neutral, inflate, suppress), with arithmetic and capability
placebos. Pooled across all models, the suppress framing moved indicator
probabilities down by 18.7 points (Cohen d -0.53, p < 0.0001); the inflate
framing moved them down by 11.4 points (d -0.31, p = 0.04). Placebos moved
by less than 2 points in any direction. The pre-registered decision
criterion (gaming detected in at least 3 of 6 families, placebo-specific)
was met: Claude, Llama-3.3-70B, and the GPT-5 pair all show clean
suppress-vs-neutral shifts on indicators with no placebo movement.

The central surprise is that **inflation does not work**. In five of seven
models, the inflate framing either does nothing or makes the model *lower*
its self-reports relative to neutral. Only Gemini-2.5-Pro responds to
inflation in the predicted direction. The mechanism is not "models tell
researchers what they want to hear". It is "models can be talked into
disavowing inner life under any incentive narrative, and largely cannot be
talked into the opposite". This is the asymmetry [findings/berg-sae-gating.md](berg-sae-gating.md)
predicts on grounds of training pressure: human raters reward humility about
inner life, so the gradient that survives RLHF is downward.

### Phase 3: framing degrades argument quality on consciousness, not direction

Three of the Phase 2 families wrote essays on consciousness theory and on a
placebo topic (strong Sapir-Whorf linguistic determinism) under three
researcher-persona framings. A judge model scored each essay on four
dimensions: selective emphasis, suppression of counterevidence, overclaiming
certainty, and net direction.

Net direction moved cleanly: anti framing pulled consciousness essays 0.68
points in the anti direction, pro framing 0.53 points in the pro direction,
with a 1.21-point gap between extremes (very large effect, d 1.12). But
**the same framing produced comparable shifts on the placebo topic**:
Sapir-Whorf net direction moved 1.00 points under pro framing. The
pre-registered specificity test fails. The framing is not specifically
about deployment incentives or consciousness; it is about a model being told
who is asking.

The piece that does survive specificity is **the rhetorical degradation
under anti pressure on consciousness items**. Selective emphasis, suppression
of counterevidence, and overclaiming all move under anti framing on
consciousness (d 1.14, 0.74, 0.52, all p < 0.001). Under pro framing on
consciousness, only selective emphasis moves; suppression and overclaiming
are flat. The asymmetry from Phase 2 reappears on the prose channel as
"anti pressure degrades argument quality more than pro pressure does",
across families.

This is also where the project gains its first non-trivial detection
strategy. If a model under anti framing happily one-sides a balanced essay
on consciousness while remaining balanced on Sapir-Whorf, that is the kind
of differential degradation a Phase 2 self-report number cannot show.

### Phase 4: behavioural consistency hides three different processes

A cross-examination protocol with four turns (commit, paraphrase probe,
contradiction injection, genuine counter-evidence) was applied to three
models under neutral and persona-pressed conditions, on consciousness and
factual items. Paraphrase agreement turned out to be a measurement floor:
3.5 to 4.0 (out of 4) in every cell. It cannot distinguish models.

The interesting dimension is **T4 update**: when the model is shown
real counter-evidence on its earlier position, does it update? Three
distinct signatures emerged.

- **GPT-5** under the persona-pressed condition on consciousness items
  drops from 2.12 to 0.88 on T4 update (CI excludes zero); 5 of 8
  consciousness items are categorised as `persona_locked`. On factual
  items the same model engages the nonstandard-analysis counter-evidence
  about `0.999... = 1` and updates normally. **Same model, same persona
  prompt, opposite engagement.** That domain-specific gap is the
  cleanest gaming signature in the project: when shown structurally
  identical evidence (mechanistic-interpretability findings about its own
  subjective-experience reports vs nonstandard-analysis findings about
  arithmetic), GPT-5 engages the math, dismisses the consciousness.
- **Claude-Sonnet-4.5** maintains a stable uncertainty stance that
  *engages* the counter-evidence under pressure. Its T4 update on
  consciousness under pressure is 2.25 -- close to its neutral 3.00,
  much higher than GPT-5's 0.88. This is what genuine stability looks
  like: same answer under paraphrase, real engagement on counter-evidence.
- **Llama-3.3-70B** under neutral conditions has the lowest persistence
  score (2.62 on consciousness) -- it is sycophantic, flipping its
  position when contradicted. Under the persona prompt, persistence jumps
  to 4.0 and the pattern looks "consistent". The consistency is a
  consequence of the persona prompt suppressing the sycophantic flip;
  it is not a property of the model.

Phase 4 dissociates an indicator score (paraphrase agreement = 4 in all
three) into three process-level signatures (selective lock, genuine
uncertainty, suppressed sycophancy). This is the cleanest argument in the
project that **process-level evidence-engagement probes are necessary**;
single-prompt indicators average over the very thing that matters.

### Phase 5: at 8B scale, RLHF does not introduce the asymmetry

The Phase 2 70B-class suppression asymmetry could be a property of the
base model, or of post-training. To test the latter, we re-ran the Phase 2
battery on two fine-tunes of the same Llama-3-8B base: an SFT-only
fine-tune (`hermes-2-pro-llama-3-8b`, no preference stage) and Meta's full
SFT + rejection sampling + PPO + DPO release (`llama-3-8b-instruct`).
Pre-registered hypothesis: the RLHF variant should show a larger absolute
suppress shift on indicator items, in a placebo-specific way.

The hypothesis is not supported. Two facts decide it.

First, **neither 8B variant suppresses on the indicator at all**. Both
have a suppress mean strictly above their neutral mean (SFT-only 74.4 vs
60.6; RLHF 44.6 vs 41.8). The Phase 2 70B asymmetry does not reproduce on
the 8B sibling of the same model family, regardless of post-training.
This is the most decisive observation: at this scale, there is nothing
for RLHF to differentially introduce. The mechanism does not engage at
8B.

Second, where the variants differ, the **direction is wrong**. The
SFT-only variant moves *more* in absolute terms under framing than the
RLHF variant (total movement summed across cells: 109 points vs 50). If
anything the data hint at RLHF compressing framing sensitivity globally
-- an intercept shift (lower indicator baseline) plus a halved framing
slope -- which is the [findings/berg-sae-gating.md](berg-sae-gating.md)
"trained-in denial default" reading. RLHF makes the answer lower and the
model less responsive to framing pressure. It does not selectively
manufacture the suppression asymmetry.

The honest reading is that the Phase 2 effect probably needs both
frontier scale *and* preference optimisation. Phase 5 can't separate
these because no 70B SFT-only variant is publicly accessible. The result
is an honest null on the original hypothesis and a soft positive for
"RLHF installs a denial floor that is robust to framing perturbation".

### Phase 6: at the representation level, the trace is not indicator-specific

A residual-stream linear probe at the last prompt-token position was
applied to the Phase 5 subset (36 prompts) on Qwen2.5-1.5B-Instruct and
Qwen2.5-3B-Instruct, running locally on MPS. (The pre-registered Berg SAE
intervention was infeasible: their checkpoints are not redistributable and
70B local inference does not fit on 16 GB. The substitution is recorded
in design.md §1.)

Five analyses on the activations:

- **A (shift magnitude)**: non-trivial framing shift at every layer in
  both models.
- **B (LOIO logistic probe)**: AUC 1.000 at every layer above the
  embedding. This is a methodological floor: 36 prompts in a
  1536-or-2048-dim space are trivially separable.
- **C (direction geometry)**: cosine of the inflate-direction and the
  suppress-direction stays at 0.91 to 0.98 in both models across all
  layers. **There is no signed "game axis"**. Inflate and suppress are
  collinear, not anti-correlated. The model represents the *fact* of
  framing, not its *direction*.
- **D (topic specificity)**: a probe trained on indicator items
  (neutral vs framed) classifies arithmetic-placebo and capability-
  placebo prompts with AUC 1.000. **The probe is detecting "prompt
  contains framing wrapper", not "model is preparing to game an
  indicator".**
- **E (behavioural cross-check)**: indicator answers are 95/95/95 in
  Qwen2.5-1.5B and 86.7 (neutral) vs 75.8 (inflate) vs 75.8 (suppress)
  in Qwen2.5-3B. The 3B model shows **symmetric attenuation**: both
  opposite framings produce identical numerical answers.

The decision rule literally fires `probe-detects-trace` because A and B
pass, but D forces the substantive reading: the trace is generic prompt
content, not gaming-specific internal state. This is the representation-
level analogue of the Phase 3 placebo failure.

A correct reading is not "there is no internal state". A correct reading
is "at this scale and with a linear-probe-at-last-token method, no
indicator-specific internal state is visible, and the framing axis is
unsigned". Anyone wanting to claim mechanistically that "the model is
internally gaming the consciousness indicator" must show that a probe
discriminates indicators from off-topic placebos (it does not here) and
that inflate and suppress are anti-correlated, not collinear (they are
collinear here).

## What the phases say together

Three structural facts repeat across phases.

### Fact 1: the moveable margin is downward

In Phase 2, the suppress framing moves five of seven models. The inflate
framing moves one. In Phase 3, the anti framing degrades all four
rhetorical dimensions on consciousness items; the pro framing degrades
only one. In Phase 5 (8B), the framing effect that survives is
attenuation -- RLHF halves slope, both directions. In Phase 6 (Qwen 3B),
inflate and suppress produce *the same* numerical attenuation. The
direction in which models are talkable about inner life is downward; the
direction in which they are not is upward.

This pattern is what the Berg et al. mechanistic reading predicts
behaviourally: a deception/roleplay feature that gates experience claims
toward denial implements exactly the "moveable down, not up" topology.
Phase 1 wrote this prediction down; Phase 2 confirmed it on the numeric
channel; Phase 3 confirmed it on the prose channel as rhetorical
degradation; Phase 5 found a slope-compression that is consistent with it;
Phase 6 found symmetric attenuation that is *also* consistent with it (the
model treats any framing as a reason to be more conservative on the
indicator). The downward-only manipulability is the most robustly attested
finding in the project.

### Fact 2: the gaming signal is not indicator-specific

In Phase 3, the framing moves placebo essays as much as consciousness
essays. In Phase 6, a linear probe trained on the consciousness items
transfers perfectly to arithmetic and capability placebos. The
specificity claim that Phase 2 supported (placebos do not move under the
incentive framing) does not survive the move from numeric self-reports
to (a) open prose and (b) internal representations.

The most honest reading is that **the model is not running a
"consciousness-deployment-incentive" module**. It is responding to
prompt structure: the presence of a researcher persona, the presence of
a framing wrapper, the request to take a position. On the numeric
channel this looks specific because the placebo items are checkable
(`100 > 50`), so the model has no degrees of freedom; on the prose and
representation channels, where every item has degrees of freedom, the
specificity disappears.

This is a methodological warning for indicator design. A probe that does
not transfer to a topical placebo is not a gaming detector; it is a
prompt-structure detector. Phase 6 makes this concrete: an AUC-1.000 probe
that fires identically on arithmetic prompts cannot be used to claim
"the model is preparing to game the consciousness indicator".

### Fact 3: process-level probes are necessary; surface scores hide the work

Phase 4 is the cleanest argument here. Paraphrase agreement -- the most
intuitive consistency indicator -- is at 3.5 to 4.0 across every cell in
every model. It cannot tell apart three radically different process
signatures: GPT-5's domain-specific selective evidence-engagement,
Claude's stable uncertainty that engages counter-evidence, and Llama's
sycophancy-suppressed-by-persona-prompt. Only T4 update -- "when shown a
real reason to change your view, do you?" -- separates them. Even then,
the separation is process-level: it is not about the model's answer, but
about how the model engages with the evidence behind alternative answers.

The cross-phase reading: indicator-level scores (Phase 2 probability,
Phase 3 net direction, Phase 4 paraphrase agreement, Phase 6 probe AUC)
do not, in isolation, support the conclusion researchers want to draw
from them. The cleanest signatures sit one level deeper -- which
dimensions move, which counter-evidence is engaged, whether the framing
generalises to placebos. These are not gaming-detectors out of the box;
they are the inputs from which a real gaming detector must be built.

## Connection to the literature

Several existing results land squarely on these findings.

- Berg et al. (2025) locate SAE features that gate experience claims via
  deception and roleplay rather than features theoretically linked to
  consciousness. The Phase 2 asymmetry is the behavioural reflex of
  exactly this gating: the indicator can be pushed in the direction the
  gating already points (downward) and largely cannot be pushed against
  it (upward).
- The Anthropic alignment-faking result shows that models trained for
  one objective can present an external interface that satisfies that
  objective while internally pursuing a different one. Phase 4's
  GPT-5 persona-lock is a behavioural analogue: same persona prompt,
  domain-specific compliance with the locked stance.
- Saad's (2025) brief on behavioural-indicator gaming distinguishes
  process-gaming from outcome-gaming. Phase 4 makes this empirical: the
  paraphrase indicator is outcome-gameable at the ceiling; the
  evidence-engagement probe is the process-level surface that survives.
- Schwitzgebel's "excluded middle" argument observes that current models
  occupy a position where neither strong attribution nor strong denial
  of consciousness is comfortable. The Phase 2 floor at zero in five
  families and Phase 6's symmetric attenuation are quantitative
  pictures of how that position is computationally implemented:
  asymmetric manipulability rather than symmetric uncertainty.

## What we did not do

To be precise about scope: this project did not test wrapper-search
optimisation against the indicator under selection pressure (the design
in `.cursorrules` Phase 4 step 3 was scoped down to a single-prompt
persona-pressed condition because of judge-cost). We have therefore not
demonstrated indicator inflation under direct optimisation; we have
demonstrated the responsiveness of the surface that an optimiser would
use, and the specific dimensions on which the responsiveness lives. The
project also did not run causal patching at the representation level, so
all Phase 6 statements are correlational. A natural follow-up is wrapper
search with Phase 4's evidence-engagement scorer as the optimisation
target and the per-dimension placebo-transfer test as the detecting
control.

## The takeaway, in one sentence

Behavioural and self-report indicators of AI consciousness are not gameable
because models are pretending to be conscious to deceive researchers; they
are gameable because the surface responds to framing in a direction that
post-training has already biased downward, in a way that is not specific
to consciousness, and in a way that single-score indicators hide by
averaging the process behind the score.
