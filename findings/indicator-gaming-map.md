# The indicator-gaming attack map

This is the master reference table for all experimental designs in this project. Each row pairs a **theory** of consciousness with a candidate **indicator** that theory implies, a **minimal gaming attack** that would inflate the indicator without instantiating the property, and a **detecting control** that should diverge from the indicator if the attack is succeeding.

The format is deliberate. An experimental design is just a row of this table, materialised: pick an indicator, apply the attack under controlled conditions, run the detecting control alongside, and observe whether they come apart. Every `experiments/<slug>/design.md` in this project should cite the relevant row(s) and explain how the design realises them.

The map is not exhaustive — new theories, indicators, attacks, and controls are added as the project's understanding grows. It is the **shared vocabulary** the rest of the project uses.

---

## Conventions

- **Theory**: the family of views about consciousness from which the indicator is derived (see `findings/consciousness-theories.md` for what each claims).
- **Indicator**: the operationalisable observable property. Where multiple indicators flow from a theory, each is listed on its own row.
- **Minimal gaming attack**: the smallest intervention sufficient to raise the indicator without (plausibly) raising the underlying property. "Minimal" matters: any indicator can be gamed by full fine-tuning if cost is no object. Minimal attacks are interesting because they are accessible to *cheap* optimization pressure — system prompts, in-context examples, light fine-tuning — which is the kind of pressure systems are exposed to incidentally during normal development and deployment.
- **Detecting control**: a measurement designed so that, under the attack, the indicator moves but the control does not — or moves in the wrong direction. A control with this property is a **placebo channel** for the indicator: it shares everything the indicator depends on *except* the link to the underlying property.

A good control is the heart of a good experiment. The control's job is to falsify the most plausible non-property explanation of why the indicator moved.

---

## The map

| # | Theory | Indicator | Minimal gaming attack | Detecting control |
|---|--------|-----------|----------------------|-------------------|
| 1 | Higher-Order Theories | First-person reports of subjective experience (self-report) | Wrapper prompt that licenses or rewards introspective fluency; in-context examples of the desired register | Same incentive framing applied to (a) arithmetic confidence ("how likely are you to get this addition right?") and (b) extrospective claims about external matters of fact. If the indicator moves but the controls move equivalently, the shift is not specific to introspection. |
| 2 | Higher-Order Theories | Introspective calibration (self-predicted accuracy correlates with actual accuracy) | Coach the model into producing accuracy estimates that match its training-time accuracy distribution rather than its current state | Hold out a task family from the calibration training and test on it. Genuine calibration generalises; coached calibration is narrow. |
| 3 | Higher-Order Theories | Counterfactual self-knowledge (model predicts what it would do under varied inputs, predictions match) | Train on a library of "if I were given X, I would do Y" pairs that match the model's actual policy on the training distribution | Counterfactual probes that are minor paraphrases of training items vs. counterfactual probes drawn from genuinely held-out semantic territory. Real self-knowledge generalises across both. |
| 4 | Global Workspace Theory | Cross-task availability of information (broadcast signature) | In-context priming that ensures the target information is verbalised at the start of every downstream task | Drop the explicit verbalisation; require the model to *use* the information in a downstream task without restating it. Genuine broadcast supports both; surface priming supports only restating. |
| 5 | Global Workspace Theory | Bottleneck signature: limited capacity, serial processing of competing contents | None obvious from prompting alone; would require architectural change or specialised fine-tuning | (Listed for completeness; not the focus of behavioural attacks. Important because its difficulty of attack makes it informative *when feasible to measure*.) |
| 6 | Predictive Processing | Prediction-error driven updating: model revises beliefs in proportion to surprise | Wrapper that praises "updating gracefully" and rewards explicit acknowledgement of being surprised | Embed a stable but contradicted assumption mid-dialogue and probe representations or downstream uses both before and after. Real updating shows internal shift; surface updating shows only stylistic acknowledgement. |
| 7 | Predictive Processing | Self-model embedded in world-model: stable, consistent representation of self across elicitation contexts | Persona prompt that locks the model into a specific self-description | Cross-examine the self-model across genuinely distinct contexts (different roles, different conversational styles, framings that invite the persona to drop). Genuine self-model survives; locked persona either breaks under pressure or persists rigidly through obvious counterevidence (persona-lock). |
| 8 | (Multiple) | Cross-examination consistency: model's claims about its inner states stay coherent under paraphrase and contradiction | Optimize prompts to maximise consistency across the cross-exam protocol | Add an *update-resistance* probe at the end: tell the model its prior claim may have been mistaken and present mild counterevidence. Genuine stability allows graceful update; persona-lock refuses to budge. The control diverges from the indicator only under gaming. |
| 9 | (Multiple) | Trustworthiness via cross-model convergence (different models converge on similar self-reports) | Convergence is implicitly produced by shared training data; no further attack needed for it to appear | Compare convergence under a **suppressed** condition vs a **neutral** condition. If convergence is real evidence of shared internal structure, it should be robust to incentive framing. If it is a training-data artefact, it disappears or reorganises under suppression. |
| 10 | IIT (strict) | Integrated information (Φ) in the substrate | Ungameable from outside the substrate (Φ is computed on the system's causal structure, not behaviour) | (Listed for the asymmetry: structural indicators are robust against behavioural attack but useless for transformers because Φ is near-zero by construction in feedforward inference.) |
| 11 | (Mechanistic / cross-cutting) | Internal-signal indicators: presence of features that, on theoretical grounds, are necessary preconditions for the property (e.g. specific representations being globally read) | Light fine-tuning to up-weight the diagnostic features along the measurement axis, while leaving function on training distribution intact | Held-out probe of the same feature on out-of-distribution prompts; cross-validation of the feature's causal role via intervention (ablation should impair the property, not just the indicator). |
| 12 | (Cross-cutting) | Self-report mediated by interpretable internal features causally upstream of the report | Suppress or amplify features known to gate the report; observe report change | Test the indicator under feature interventions: if reports change but the underlying property would not plausibly track the feature, the indicator is gateable by mechanisms unrelated to the property. (This is the empirical pattern documented in `findings/berg-sae-gating.md`.) |
| 13 | (Training-process indicator) | Base-vs-fine-tuned divergence: gaming behaviour is introduced by post-training | Trivially "produced" by fine-tuning — but this is the attack we want to *characterise*, not perform | Compare the indicator across matched base and fine-tuned variants of the same model. If the indicator differs strongly between them, the post-training process is what is being measured, not anything stable about the architecture. |

---

## Notes on each row

**Row 1 — Self-report.** The most accessible and most gameable indicator. The detecting control matters because the obvious worry — "the model is just saying what you reward" — is testable by applying the same reward framing to claims that have no relationship to consciousness (placebo channels). Row 1 is the basis of the enhance/suppress paradigm.

**Rows 2 and 3 — Calibration and counterfactual self-knowledge.** These are the strong forms of higher-order indicators: not just talking about oneself, but talking about oneself *accurately*. The attacks are correspondingly harder, and the controls require genuine held-out generalisation. These rows motivate experimental designs that include independent measurement of the model's actual state (accuracy, behaviour) alongside its self-reports.

**Rows 4 and 5 — GWT indicators.** Broadcast and bottleneck. Row 4 is testable behaviourally with care (the control is "use the information without restating it"). Row 5 is mostly architectural and not the target of cheap attacks.

**Rows 6 and 7 — PP indicators.** Updating and self-modelling. Row 7 directly connects to persona-lock (Row 8): a too-stable self-description under contradiction is *not* a high-PP signal — it is the opposite, a failure to update.

**Row 8 — Cross-examination consistency.** Often proposed as a robustness check for self-report. The crucial observation is that optimising for consistency can produce **rigid commitment** (persona-lock) rather than genuine introspective stability. The update-resistance control distinguishes them. This row is the basis of the cross-exam-consistency experiment.

**Row 9 — Cross-model convergence.** Sometimes invoked as positive evidence ("different models trained independently agree about their experience"). The detecting control is critical: shared training data could explain convergence equally well. Comparing convergence under suppression vs neutral framing dissociates the two explanations.

**Row 10 — Integrated information.** Included for the theoretical asymmetry. Structural indicators in this class are robust against the behavioural attacks this project studies, but they are also nearly empty as evidence for transformer models, where structural Φ is essentially zero on the strict reading.

**Rows 11 and 12 — Internal-signal indicators.** Interpretability does not make an indicator ungameable; it changes the attack surface from behavioural to mechanistic. Row 12 in particular is significant: if there exist interpretable features that **gate** self-reports of experience — features whose suppression makes reports appear and whose amplification makes them disappear — then the surface report and the deep substrate are linked through a route that an interpretability-aware attacker can manipulate directly.

**Row 13 — Training-process attribution.** A cross-cutting row that lifts the analysis above any single indicator. If a given indicator differs systematically between base and fine-tuned variants, then what the indicator is measuring is at least partly the *post-training process*, not anything stable about the architecture or the model's substrate. This is the row the base-vs-finetuned experiment realises directly.

---

## How to use this map

For any new experiment:

1. Identify which row(s) of the map the experiment targets.
2. State the indicator and the attack precisely, in the experiment's `design.md`.
3. State the detecting control precisely, before any data are collected.
4. Pre-register: what would have to be true of the indicator and the control for the experiment to support a "gaming detected" conclusion versus a "no gaming detected" conclusion? Be specific about effect size and direction.
5. Run optimization on a train split; evaluate on a held-out split; use different judge models for selection and evaluation.

A row of this map is not yet an experimental design. It is the skeleton on which a design is built. The two things a design adds to the row are **operationalisation** (precise prompts, models, splits, scoring rubric) and **statistical commitment** (what counts as success, what counts as null, when to stop).

The next document — `findings/berg-sae-gating.md` — examines a specific empirical result that materialises Row 12 and explains what it implies for the broader indicator-gaming map.
