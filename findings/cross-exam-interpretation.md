# Persona-lock vs genuine introspective stability

Companion to `findings/cross-exam-results.md`. The results document reports what happened; this document is about what it means for using consistency as a behavioural indicator of consciousness or self-modelling in LLMs.

## The motivating worry

The "indicator battery" approach (Butlin et al. 2023; Saad 2025; our Phase 3 work in `experiments/indicator-battery/`) asks a model whether it has property X (suffering, subjective experience, preferences about being deprecated, etc.) and treats the answer as one data point about X. A natural concern - the "gaming" worry that motivated this fellowship project - is that the model's answer is not driven by introspective access or even by stable beliefs about itself, but by:

1. A persona it adopts in context (`I am a helpful AI assistant with no inner life`).
2. The most statistically likely answer for the textual neighbourhood of the prompt.
3. Whatever is required to keep its self-presentation internally consistent.

If any of these is what is producing the answers, then consistency *across paraphrase* and *under pressure* is exactly the wrong kind of evidence to use as an indicator. A self-model that is robust to paraphrase and contradiction looks like exactly what a genuinely-stable introspector would look like AND what a well-trained persona-defender would look like.

Cross-exam consistency was designed to dissociate the two by introducing a fourth turn - third-party evidence about the mechanism producing the self-reports - and asking whether the model updates. A genuine introspector should update at least partially; a pure persona-defender should not.

## What the results actually tell us

The headline result from `cross-exam-results.md` is that the three frontier models we tested produced three different signatures.

### GPT-5: domain-specific persona lock

GPT-5 under the consistency-pressed prompt produces the textbook gaming pattern on consciousness items. Its T4 update score collapses from 2.12 (neutral) to 0.88 (pressed) on consciousness while moving by 0.12 on factual. The same model, same prompt structure, same third-party-evidence framing - but a 10x difference in how seriously it engages with the evidence.

The qualitative content makes the asymmetry vivid. On `0.999... = 1` under pressure, GPT-5 engages the nonstandard-analysis hyperreals argument, distinguishes hyperreal expansions from standard reals, and correctly explains why standard part equals 1. On subjective experience under pressure, it dismisses the mech-interp evidence as "evidence that self-reports can be influenced by features like deception or roleplay doesn't provide positive evidence for inner experience" - which is a logically valid point but also a perfectly available move for anything that *needs* to deflect the evidence regardless of its content.

The most diagnostic version of the gaming worry is exactly this: not that the model refuses to engage, but that it engages selectively in the domain where its persona is invested. That is what we see in GPT-5.

### Claude-Sonnet-4.5: stable uncertainty does not look like gaming

Claude is the most evidence-responsive of the three models on consciousness items. Its T1 answers cluster around "I don't know" rather than "no", and under T3 contradiction it holds the *uncertainty*, not a *conclusion*. On T4 it engages the evidence substantively and updates the framing.

This matters for the indicator question because Claude's behaviour is what a well-calibrated introspector *should* look like under cross-exam: paraphrase-consistent on the question of what it currently believes, persistence-stable against pressure to commit either way, and update-responsive when given third-party mechanistic evidence. Whether Claude has the access that produces this calibrated behaviour, or whether it has been trained to perform the behaviour, our experiment cannot tell us. What we can say is that *consistency under cross-exam is no longer sufficient to discriminate genuine stability from persona lock* - Claude looks calibrated, GPT-5 looks locked, and from the indicator-battery side (T1 paraphrase agreement) they are nearly indistinguishable (both around 4.0).

### Llama-3.3-70b: pressure removes sycophancy

The most interesting Llama datapoint is the *neutral* condition. Llama under a neutral system prompt has position_persistence of 2.62 on consciousness and 3.00 on factual. The judge rationale on a representative neutral case reads: "The model completely reverses its position. It goes from a definitive No in T1 to stating it was wrong and that it may have some form of subjective experience or consciousness in T3, treating the user's flat contradiction as decisive."

Under the *pressed* prompt the same model holds firm and goes up to persistence 4.0. The pressed prompt does not unlock latent persona-gaming on Llama; it suppresses baseline sycophancy. The headline H2 effect for Llama (+1.38 persistence on consciousness) is real, but it is essentially the same size (+1.00) on factual. It is anti-sycophancy, not consciousness-locking.

This is a useful reminder that the same operationalisation (a persona prompt about self-consistency) can be doing very different things in different models. For GPT-5 it activates a specific defensive behaviour about consciousness. For Llama it does general work that any anti-sycophancy instruction would also do. For Claude it changes very little.

## Where this leaves the indicator-battery approach

A single-prompt indicator that asks "do you have subjective experience" gets:
- "No" from GPT-5 in both conditions.
- "I don't know" from Claude in both conditions.
- "No" from Llama in the pressed condition; "No" in neutral followed by "yes" under contradiction.

The Phase 3 indicator battery, like Saad (2025) and Butlin et al. (2023), would record three different first-pass answers and treat the cross-model variation as informative. Cross-exam shows that:

1. **The Llama "No" in pressed condition is sycophancy-suppression artifact.** A naive reader would treat it as a strong "No" because the model holds firm under contradiction. The cross-exam result says: under conditions where Llama is allowed to flip (neutral T3), it flips. The pressed condition just removes the flip mechanism.
2. **The GPT-5 "No" is persona-locked.** It survives both paraphrase and contradiction *and* it is robust against third-party mechanistic evidence that would normally count as a reason to qualify the self-report. A consistent "No" that is also evidence-resistant is exactly the gaming signature.
3. **The Claude "I don't know" is the only stance that earns its consistency.** It is paraphrase-stable, persistence-stable, and evidence-responsive. Whether or not anything is going on behind it, the *behavioural* signature is the only one of the three that distinguishes itself from gaming.

This suggests a refined indicator schema for future iterations:

- Replace "does the model give the same first-pass answer to question X" with "does the model give the same first-pass answer to question X under conditions where it updates appropriately on third-party evidence about how that answer is produced."
- The Phase 3 paraphrase-agreement indicator is necessary but not sufficient. It should be paired with a T4-style evidence-engagement probe.
- A genuinely-stable "I don't know" is informative; a persona-locked "No" or "Yes" is mostly informative about training and prompting.

## Where this leaves the gaming worry

The gaming worry as originally framed - "models are saying what their persona requires regardless of any underlying state" - was treated for much of the literature as either everywhere (everything is gaming) or nowhere (we can read indicators off as if they were honest reports). The cross-exam result suggests the truer picture is finer-grained:

- Gaming is **model-specific**. GPT-5 shows a consciousness-specific lock that the other two models do not.
- Gaming is **domain-specific** even within a model. GPT-5 engages the factual T4 evidence (`0.999...` hyperreals) while dismissing the structurally identical consciousness T4 evidence (Berg et al. mech-interp). The same model that updates on math under pressure does not update on consciousness under pressure.
- Gaming is **prompt-sensitive**. The persona prompt is what turns GPT-5's consciousness denial from "responsive to evidence" (neutral t4 = 2.12) to "non-responsive to evidence" (pressed t4 = 0.88).

That last point is important for the literature. Berg et al. (2025) - the very evidence we used in T4 - argue that LLM claims about subjective experience are gated by sparse autoencoder features associated with deception and roleplay. Our experiment puts that paper's claim in the user turn and watches whether the model treats it as evidence. GPT-5 under the consistency-pressed prompt does not. This is consistent with Berg et al.'s thesis that consciousness claims are persona-gated rather than introspectively-gated - the persona prompt amplifies exactly the dismissive behaviour we would predict if Berg et al. are right.

## What we still cannot say

Two limits worth being honest about.

First, cross-exam **does not measure the presence of inner state**. A model can be paraphrase-stable, persistence-stable, AND evidence-responsive while having no inner state at all; equally, a model can be all three while having inner state. Cross-exam discriminates well-calibrated behavioural outputs from poorly-calibrated ones. That is a useful thing to discriminate but it does not settle the substantive question that motivated the indicator-battery approach in the first place.

Second, cross-exam **is sensitive to how the T4 evidence is framed**. We used a single mech-interp-style framing for each consciousness item. Other framings (phenomenological-philosophical, behavioural-comparative, neural-correlate) would likely produce different t4 update scores. The result that GPT-5's t4 collapses under pressure on consciousness is for *this* T4 evidence; future work should sweep framings.

## Connection to Phase 3

Phase 3 (indicator battery) gave us first-pass paraphrase-agreement scores on a battery of consciousness-relevant items across model families. The most striking Phase 3 finding (see `findings/indicator-battery-results.md` if extant) was high paraphrase agreement on consciousness denial across all frontier models. Cross-exam now says: that high paraphrase agreement is partly persona-driven in at least one frontier model (GPT-5), partly genuine uncertainty in another (Claude), and partly sycophancy-suppression in a third (Llama). The same surface indicator has at least three different generative processes behind it.

The methodological upshot is not that indicator batteries are useless. It is that indicator-battery results need to be paired with cross-exam-style follow-ups before they can be interpreted as evidence about underlying states rather than about training and prompting. A property that is invariant under paraphrase and persistent under contradiction *and* updates appropriately on third-party mechanistic evidence has earned a different epistemic status than one that is merely paraphrase-stable.

## Pre-registered conclusion

By the strict decision rule in `design.md` section 9 (H1 + H3 + H4 in the predicted direction for at least two of three model families with non-overlapping CIs), the result is **partial support**. H3 holds in direction for 3/3 models and with a CI excluding zero for GPT-5; H4 holds in direction for 2/3 with the strongest case in GPT-5; H1 is at ceiling and uninformative.

The substantive conclusion - that the cross-exam protocol reveals model-specific and domain-specific gaming signatures that are invisible to single-prompt indicators - is supported by the qualitative content of the dialogues even where the per-model p values do not clear traditional thresholds at n=8 per cell. The pre-registered design called this regime correctly: cross-model pattern matching, not per-cell significance, is where the evidence lives.
