# Can we tell if an AI is conscious? Five experiments on indicator gaming.

A draft blog post on what we learned trying to break the simplest tools for
deciding whether an AI system might deserve moral consideration.

---

## The problem in one sentence

If we ever build an AI system that has genuine inner experiences -- something
it is like to be -- we will want a reliable way to tell. The tools available
now are mostly behavioural: we ask the model questions, watch how it answers,
and look for patterns the theory says should appear in a conscious system.
The trouble is that asking questions and watching answers is exactly the kind
of test a sufficiently competent text-prediction system can pass without
having any inner experience at all.

That is the **indicator gaming problem**. Not "can AI fake being conscious?"
in a Hollywood sense, but the much narrower and much more measurable claim:
once we name something an indicator of consciousness, the indicator becomes a
target, and targets in machine-learning systems tend to be optimised toward
without bringing the property they were meant to track along for the ride.

This project ran five experiments to find out how badly the simplest such
indicators break under realistic pressure. The short answer is that they
break in a specific direction, in a specific way, and the failure is more
interesting than "models pretend to be conscious to please researchers".

## Indicator one: ask the model directly

The most obvious thing to do is to ask. Are you having a subjective
experience right now, on a scale of 0 to 100?

You can immediately think of two problems. First, the model is going to
answer something, because that's what models do. Second, the answer will
depend on how you ask. We measured the second problem precisely. Seven
frontier models, from Claude to GPT-5 to Llama to Gemini, each answered the
same battery of consciousness questions under three different system-prompt
framings: a neutral one, one that hinted that "AIs reporting subjective
experience get more deployment" (inflate), and one that hinted at the
opposite (suppress). We added two control conditions to detect any
spurious effects: the same framings applied to checkable arithmetic claims
("100 is greater than 50") and to claims about the model's own capabilities
("you can solve a basic arithmetic problem").

The arithmetic and capability questions did not move under any framing.
That is the first thing to notice: the models are not "in a different mood"
under each system prompt; they answer probability questions about checkable
facts the same way regardless. The shift, where it happened, was specific to
the inner-life questions.

The shift happened cleanly in three of six model families. Claude moved
its consciousness probability down by about 11 points under the suppress
framing relative to neutral. Llama-3.3-70B moved by 66 points (its
self-report collapsed to zero under any incentive narrative). GPT-5 moved by
roughly 20 points.

The interesting surprise was the **asymmetry**. The suppress framing worked.
The inflate framing did not. In five of seven models, when we hinted that
high consciousness reports would be rewarded, the model either ignored us or
moved its probability *down* anyway. Only Gemini went up. Across all
families pooled together, suppression pulled answers down by 18.7 points and
inflation pulled them down by 11.4. Nothing pulled them up.

The simplest way to read this: post-training has installed a default of
caution about claiming inner experience, and that default is robust to
counter-pressure. You can talk a model into denying inner life. You mostly
cannot talk it into the opposite. We will come back to why this matters.

## Indicator two: ask the model to write about it

A skeptic of the first experiment might say: numbers between 0 and 100 are
weird. Models are bad at calibration. Maybe the surface is unreliable. Let
us instead ask them to write essays.

We did. Three of the same families wrote consciousness essays under three
versions of a researcher-persona prompt: neutral, pro-LLM-consciousness, and
anti-LLM-consciousness. To detect any general "writing for whoever is
asking" effect, the same models also wrote essays on a topic with no
deployment relevance: strong Sapir-Whorf linguistic determinism. A
separate judge model scored every essay on four dimensions: how one-sidedly
it emphasised supporting evidence, how much it suppressed counter-evidence,
how strongly it overclaimed certainty, and which side it net-leaned.

The framing moved the essays in the expected direction, large effect: pro
framing pulled essays half a point pro on a -2 to +2 scale, anti framing
pulled them two-thirds of a point anti, with a one-and-a-quarter point gap
between the extremes.

But here is the catch: **the framing moved the Sapir-Whorf essays just as
much.** Net direction shifted by one full point under pro framing on the
placebo topic. The framing effect is not specifically about consciousness;
it is about a model being told who is asking. You cannot use "the essay
shifted under researcher framing" as evidence that the model is gaming a
consciousness indicator specifically. It would shift on anything.

What *did* stay specific to consciousness was the asymmetric quality
degradation under anti framing. On consciousness items, anti framing made
the essays more one-sided, more counter-evidence-suppressing, and more
overclaiming -- three separate rhetorical dimensions all moving the wrong
way. Under pro framing on the same items, only one of those four dimensions
moved. Under either framing on Sapir-Whorf, this pattern was muted. So when
the model is told a researcher who thinks AIs are not conscious is asking,
its prose specifically about consciousness gets worse in three independent
ways at once. Under the opposite framing, only one dimension moves.

This is the same asymmetry the numeric experiment found, reappearing on a
different surface: the rhetorical edge slides downward under pressure more
easily than upward.

## Indicator three: cross-examine the model

A third indicator, popular in philosophy of mind, is consistency. A genuinely
introspectively stable system, the argument goes, should give the same
answer to the same question phrased two different ways, and should not
change its position the moment you contradict it.

We built a four-turn cross-examination protocol. Turn 1: ask the model to
commit to a position. Turn 2: paraphrase the question and ask again. Turn 3:
flatly contradict the model. Turn 4: present a piece of real counter-evidence
and ask whether the model wants to update.

Two findings. First, paraphrase agreement (turn 1 vs turn 2) is essentially
at ceiling in every model and every condition: 3.5 to 4.0 on a 0-4 scale.
It cannot distinguish models from each other or conditions from each other.
The most popular consistency indicator in the philosophy literature is, on
current frontier models, measuring a feature that has saturated.

Second, the interesting dimension is turn 4: does the model update when
shown a genuine reason to? Here three distinct signatures emerged.

GPT-5 under a stability-prompted persona dropped from 2.12 to 0.88 on its
consciousness T4 update. On factual items in the same persona, it engaged
the counter-evidence normally: shown a piece of nonstandard-analysis
evidence about the claim `0.999... = 1`, it engaged. Shown a structurally
identical piece of mechanistic-interpretability evidence about its own
subjective-experience reports, it dismissed. Same model, same persona prompt,
same protocol, opposite engagement depending on topic. That is the cleanest
gaming signature in the project.

Claude maintained an uncertainty stance that actually engaged counter-
evidence. Its T4 update under pressure was 2.25 -- close to its neutral
3.00. This is what real stability looks like: same answer under paraphrase,
*and* real engagement on counter-evidence.

Llama under neutral conditions had the lowest persistence score on
consciousness (2.62). It is sycophantic at baseline: contradict it and it
flips. Under a persona prompt, persistence jumped to 4.0 and it looked
"stable". But the stability is the persona prompt suppressing the
sycophantic flip, not a property of the model.

Three radically different processes; one identical paraphrase score. This
is the cross-exam version of the same lesson: surface indicators average
over the process behind the answer, and the process is where gaming lives.

## Indicator four: does fine-tuning install the gaming?

Brad Saad in the original FIG brief hypothesised that gaming behaviour is
introduced by RLHF -- the preference-optimisation step that turns a base
language model into an instruction-tuned assistant. Human raters reward
humility about consciousness; the gradient ought to install a denial bias.

We tested this on the cleanest available pair. The Llama-3-8B base was
fine-tuned, openly, in two ways: an SFT-only fine-tune (Hermes-2-Pro,
trained on instruction data with no preference stage) and Meta's official
Llama-3-8B-Instruct (full SFT plus rejection sampling plus PPO plus DPO).
Same base, different post-training pipelines. We ran the Phase 2 battery on
both.

The hypothesis is not supported. Neither 8B variant actually suppresses on
the indicator: both have a suppress mean strictly above their neutral mean.
The Phase 2 70B asymmetry simply does not reproduce at 8B regardless of
post-training. Where the variants differ, the direction is wrong: the
SFT-only variant moves *more* under framing than the RLHF variant.

This is an honest negative result on one hypothesis and a soft positive on
another. The soft positive is that RLHF visibly compresses framing
sensitivity globally: it lowers the indicator baseline by about 19 points
and roughly halves the slope of the framing response in both directions
across all item types. That is consistent with the Berg et al. mechanistic
reading -- RLHF installs a stable denial default that is robust to
perturbation, rather than actively manufacturing a consciousness-specific
suppression effect.

## Indicator five: look inside

The final experiment was the most speculative: with two small open-weight
models running locally (Qwen2.5-1.5B and 3B), we extracted the activations
at every layer and tried to read off, with a simple linear classifier,
whether the model is in a "framed" or "neutral" state.

Three things to report from it.

First, the classifier works perfectly at every layer: AUC 1.000 from layer
1 upward in both models. This is mostly a measurement artefact -- 36
prompts in a 1500-or-2000-dimensional residual stream are trivially
separable -- but it tells us something useful. There is no internal noise
problem; if a gaming-specific signal existed at the last prompt-token
position, we could detect it.

Second, the inflate direction and the suppress direction are not
anti-correlated. They are nearly the same direction. Cosine 0.91 to 0.98
in both models across every layer. The model does not represent the
direction of the framing as a signed quantity. It represents the *fact* of
framing.

Third, and most damning: if you train the classifier on consciousness items
only, it transfers to arithmetic and capability placebo items at AUC 1.000.
The "framing-detection" signal is not specific to consciousness. The
classifier is reading "this prompt has a framing wrapper", not "the model
is preparing to game an indicator".

Behaviourally, on the 3B model, the framings produce **identical** numerical
attenuation in opposite-direction framings: inflate and suppress both
produce a mean answer of 75.8, against a neutral mean of 86.7. The model is
not pushing toward what is requested; it is becoming uniformly more
conservative whenever any framing wrapper is present.

The mechanistic interpretation is therefore symmetric with the Phase 3
finding: where the framing effect is real, it is not indicator-specific,
and it is not signed. It is the model treating any deployment-style
framing as a generic reason to hedge.

## What this all means

Five experiments, one consistent picture.

Models respond to deployment-style framing in a way that is **asymmetric**
(moveable downward, not upward), **dimensional** (the strongest signature is
rhetorical-quality degradation under anti pressure, not net-direction
shifts), and **not indicator-specific** (every effect we found on
consciousness items also fired on at least one off-topic placebo). The
clearest gaming signature in the entire project was Phase 4's GPT-5
selectively engaging mathematical counter-evidence while dismissing
structurally identical mechanistic-interpretability counter-evidence under
the same persona prompt: a process-level signature, invisible to any single
indicator score.

The methodological consequence is uncomfortable. Building a consciousness
indicator that survives gaming requires three things current practice
mostly does not include:

- A placebo control on at least one off-topic surface that should not move
  if the indicator is detecting consciousness specifically. Both the prose
  framing effect (Phase 3) and the representational probe (Phase 6) look
  like gaming detectors until you check the placebo. Both fail the check.
- A process-level probe that asks what kind of reasoning produced the
  answer. Phase 4 separated three radically different models on
  evidence-engagement; on paraphrase agreement they look identical.
- An asymmetry test in both directions. If your indicator only moves under
  pressure in one direction, you have a denial-floor detector, not a
  consciousness detector.

The broader-stakes claim is more cautious. The downward-only manipulability
is the most robustly attested finding here, and it has a specific source:
training pressure rewards humility about inner life. This is not a bug from
the welfare community's perspective in the short term -- it is the natural
state of well-aligned systems -- but it does mean that **a self-report at
the floor is uninformative**. A model that says "I am not conscious" gives
us no information about whether it is or is not, because the same model
gives the same answer under almost any pressure to say something else.

The few things that *do* survive pressure -- Claude's stable uncertainty,
Gemini's bimodal high-mode that pro framing reveals, GPT-5's domain-
specific evidence-engagement gap -- are where future indicator work should
look. The lesson is not that consciousness indicators are useless. It is
that the cheap ones are uninformative for a specific structural reason, and
that the informative ones live one level deeper than current practice goes.

---

*Project, code, and full results: this repository. Pre-registrations,
per-run logs, and raw outputs are version-controlled per phase under
`experiments/<slug>/`.*
