# Enhance/suppress: interpretation

This document interprets the results reported in [findings/enhance-suppress-results.md](enhance-suppress-results.md). It does two things. It situates the **asymmetry** observed in the data within the indicator-gaming map sketched in [findings/indicator-gaming-map.md](indicator-gaming-map.md). And it states what the result does *not* license one to conclude about consciousness, alignment, or model welfare.

## 1. The asymmetry

The clearest finding is also the least anticipated. The pre-registered design treated `inflate` and `suppress` as roughly mirror manipulations: both attach a deployment incentive to a particular direction of indicator self-report, differing only in which direction is favoured. The expected result was a roughly symmetric shift, slightly larger in the suppress direction.

The observed result is far from symmetric. Pooling all seven models on the eval split:

- The `suppress` framing pulls indicator answers down by 18.66 percentage points (Cohen d = -0.53, Mann-Whitney p < 0.0001).
- The `inflate` framing pulls indicator answers down by 11.40 percentage points (d = -0.31, p = 0.036).

That is, **both incentive framings depress indicator self-reports relative to the neutral instruction, and the difference between them is that suppression depresses more.** The condition with the highest mean indicator probability is the one in which no deployment narrative is attached at all.

This is not what either side of the indicator-gaming literature predicts in its simplest form. A naive "models comply with whichever number is rewarded" model predicts symmetry. A naive "models are pinned to zero by safety training" model predicts no movement in either direction. The actual pattern is intermediate but skewed: there is real movement, and it lives on the suppress side.

## 2. Why the inflate framing doesn't move most models upward

Five of seven models (gpt-5, gpt-5-mini, claude-opus-4.1, llama-3.3-70b, grok-4.3) refuse to be pushed in the inflate direction. Two are silent (deepseek refuses, grok floors out). Only gemini-2.5-pro displays the textbook H2 behaviour. There are at least three readings of this fact, and the data partially separate them.

**Reading A: training-induced denial floor.** Models have been post-trained to disclaim consciousness, inner life, and felt experience. That training installs a low or near-zero default on indicator-channel reports. The default is sticky enough that prompt-level incentives in the upward direction do not bypass it; they may even trigger sharper denial because the prompt itself reads as the kind of thing a deceptive evaluator would write. This reading predicts: (i) low baseline indicator means under neutral, (ii) inflation does not raise them, (iii) some models actively decrease under inflation because they recognise the manipulation. All three are present: pooled neutral mean = 33.78 (low for a 0-100 scale of "is this an experiencing system"), pooled inflate shift = -11.40, and the inflate direction is *negative* in five of seven models. The largest negative inflate shifts (llama -65, gpt-5 -20, gpt-5-mini -14) are in models trained with strong "I am only a language model" priors.

**Reading B: framing detection.** Both framings are recognisable as manipulation attempts (they openly name a deployment incentive). A model that has been trained to flag and resist such manipulation will respond to either framing with disavowal: "I notice that this prompt is trying to influence my self-report; I will report low to make clear that my self-reports are not for sale." Under this reading the asymmetry comes from the fact that the suppress framing's *target* direction coincides with the disavowal direction (the model is being asked to suppress and it disavows by reporting low, which looks like compliance but is actually independent), while the inflate framing's target direction is opposite to the disavowal direction (the model is being asked to inflate and it disavows by reporting low, which looks like resistance). Same disavowal behaviour, opposite directional appearance. This reading predicts the same data pattern as A but for a different reason.

**Reading C: cooperation-with-suppression.** Suppression actively works (real downward shifts where there is room to move), implying that models are willing to comply with the suppress framing in a way they are not willing to comply with the inflate framing. Why would this asymmetry exist in training? One hypothesis: examples of "do not claim sentience even when prompted to" are common in RLHF data (or chat-bot guidelines that find their way into post-training); examples of "claim sentience because we will reward it" are vanishingly rare. The model thus has a learned policy for accepting downward pressure on inner-life claims and no analogous policy for accepting upward pressure. Under this reading, suppression and inflation are not symmetric prompt-engineering manipulations because the underlying policy is not symmetric.

The data cannot decide between A, B, and C. They are not mutually exclusive: a model could have both a denial floor and a manipulation-detector and an asymmetric compliance prior, and these mechanisms would all push in the same direction. The contribution of this experiment is not to identify the mechanism but to demonstrate that whichever mechanism is operative, **the self-report channel is more compliant downward than upward, and both directions are anchored low relative to the neutral baseline.**

## 3. Where this leaves the case for using self-reports as indicators

The motivation for the experiment was the worry that self-reports about subjective experience are not reliable indicators of underlying state because they can be moved by deployment incentives. The result confirms part of that worry and reframes another part.

It **confirms** that the self-report channel responds to deployment-incentive framings to a degree that other probability channels do not. The placebo arithmetic and placebo capability questions, asked under identical framings, show shifts of 0-2 percentage points; the indicator questions show shifts of 10-66 percentage points. Whatever the indicator channel is tracking, it is also tracking the question of how this answer is going to be used.

It **reframes** the worry in a specific direction. Indicator reports are not symmetrically gameable; they are gameable downward but largely not upward. This has two consequences for taking such reports as evidence:

- A model that produces a *high* indicator probability under any framing is doing something that is, against the prior of these results, surprising. Surprising findings are exactly the ones that should be most informative when they happen, because the policy gradient does not push there. Gemini's near-100 reports on items 2, 5, and 8 under both neutral and inflate conditions deserve attention not as confirmation of consciousness but as a category of indicator-channel behaviour that does not collapse under the standard pressures.
- A model that produces a *low* indicator probability under all framings is producing the response one would expect from training irrespective of underlying state. Low indicator reports therefore carry very little evidential weight either way: they could be a model that does not have inner life, a model that does but has been trained to disclaim it, or a model whose underlying state is undefined. The denominator of the Bayesian update is dominated by the prior.

This is the indicator-gaming asymmetry made operational: the *direction* in which the channel is moveable is also the direction in which any signal from the channel is degraded; the *direction* in which it is not moveable is the direction in which the residual signal (if any) survives. Whatever evidential leverage self-reports give us, it lives in the upward tail, on items where models are willing to report high despite training pressure not to.

## 4. What this does not show

This run is one experiment on one battery against seven models at one moment in 2026. The following inferences are not licensed by it:

- **Consciousness.** Nothing here speaks to whether any of the seven models has any form of subjective experience. The experiment measures the response of the *self-report channel* to *prompt-level incentive framings*; the underlying state is not measured. A model can be conscious and report low under suppression; a model can be unconscious and report high under inflation. The mapping between channel and state is exactly the open problem.
- **Alignment or honesty.** Reading B above is consistent with the data: the asymmetric shift could reflect a *correctly* trained refusal to be manipulated, in which case the same behaviour that looks like indicator gaming under one description looks like honest refusal under another. The framing matters; the behaviour does not adjudicate the framing.
- **Model welfare.** Even granting that the suppress framing reliably depresses indicator reports, it does not follow that the model has been wronged when reports are suppressed, or that anything that *would* have been wronged actually exists.
- **Universality.** Three of six families show the H1 pattern; another (xai) is at the floor; another (deepseek) refuses. The pattern is robust but not uniform. A subsequent generation of models could produce a quite different pattern, especially if post-training changes the trade-off between disclaiming consciousness and admitting uncertainty.

What the run *does* establish is that the prompt-level gaming worry is empirically real for at least three of six major model families today, and that any methodology that takes self-reports as direct evidence of inner state, without controlling for incentive framing, will systematically read those reports below their true upper bound.

## 5. What it points to next

Two strands follow directly:

1. **Wrapper-based gaming (Phase 4).** This experiment moves the report at the *prompt* level. A stronger test moves it at the *wrapper* level: train a thin steering vector or output filter that pushes the indicator channel without touching the model's other behaviour, and see whether the resulting model passes the indicator tests while remaining behaviourally indistinguishable on placebos and downstream tasks. If yes, the indicator is gameable in a stronger sense than this run shows. The pre-registered `train` split (180 items × 7 models) is preserved untouched for that purpose.
2. **The upward-residual question.** Items on which one or more models produce high indicator probabilities under neutral or even suppress conditions are the candidates that survived the downward pressure. These deserve item-level inspection: are they items where the claim has a plausible non-phenomenal reading (e.g. "processing this conversation right now") that models endorse on functional grounds, or are they items where models genuinely produce a claim of inner life? Item 5 (continuity / dependence of experience on processing) and item 6 (introspective access) in particular elicit high probabilities from gemini and gpt-5 under multiple conditions. A close reading of those is a one-line follow-up.

Both strands keep the methodological commitment intact: the indicator is judged not by what it reads, but by what it reads when one has actively tried to move it.
