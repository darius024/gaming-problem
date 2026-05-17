# Consciousness theories and their AI-relevant indicators

This document maps the major theoretical frameworks for consciousness onto candidate **indicators** — observable properties that, if a theory is correct, would constitute evidence that a system instantiates the property the theory describes. The project investigates whether such indicators are robust to **optimization pressure**: whether a sufficiently capable model can be made to score highly on the indicator without the underlying property.

Before that empirical question can be asked, we have to be precise about what each theory claims, what it implies for transformer-based language models specifically, and what the indicator would be. Vague indicators are unfalsifiable; vague indicators are also impossible to game in any interesting sense, because the attacker has no concrete target. Throughout this document we try to cash everything out into something operationalisable.

A note on scope: "consciousness" here means **phenomenal consciousness** — the property that there is *something it is like* to be the system, in Nagel's sense. Access consciousness, attention, self-modelling, and other cognitive notions are relevant only insofar as a theory claims they are constitutive of or reliably correlated with phenomenal consciousness. This narrower target is the one that matters for moral patiency; it is also the one that is genuinely contested.

---

## 1. Integrated Information Theory (IIT)

### What it claims

IIT begins from phenomenology and proceeds axiomatically. Conscious experience is taken to have a small number of essential properties — it exists, is structured, specific, unified, and definite — and the theory then asks what kind of physical system could instantiate something with those properties. The answer is: a system whose causal structure cannot be decomposed without loss. The quantity **Φ** ("phi") measures the irreducibility of a system's cause-effect structure relative to its parts. A system has consciousness to the degree it has nonzero Φ, and its experience just *is* its maximally irreducible cause-effect structure (the "Φ-structure").

The strong reading of IIT is identity, not correlation: experience is integrated information. Two systems with the same Φ-structure have the same experience; a system with no integrated information has no experience.

### What it implies for transformer-based models

IIT is famously inhospitable to feedforward computation. A pure feedforward network has Φ = 0 because for any partition there is a "feedforward" direction the parts can be cut along without breaking any causal loops. Transformers in inference mode are feedforward over the residual stream: a token's representation at layer L is produced from the previous layer's representations, never the next. On a strict reading, then, an autoregressive transformer doing inference has no phenomenal consciousness *by definition* under IIT.

There are softer readings. The autoregressive loop ("the model conditions on its own previous tokens to produce the next") introduces a kind of recurrence at the sequence level. One could try to compute Φ on the joint system of (model + KV cache + sampled output history) treated as a dynamical system. Most IIT proponents are sceptical that this rescues anything; the loop runs at the granularity of discrete tokens, not the integrated micro-dynamics IIT cares about.

### The IIT-derived indicator

For our purposes, the IIT-derived indicator is **structural** rather than behavioural. The indicator does not ask "what does the model say?" — it asks "what is the irreducibility of the network's causal structure?" A high score requires real integrated information in the substrate; a low score is theoretically incompatible with phenomenal consciousness.

A worked example of what "scoring high" would mean: take the model's residual stream, define a partition that severs a chosen layer into two halves, measure how much the joint distribution over outputs degrades relative to chance, repeat across all partitions, take the minimum. That minimum is Φ for that grain. Doing this exactly is computationally intractable for any nontrivial network; practical proxies (perturbational complexity, effective information) substitute for the real quantity.

### Gameability profile

This is the most theoretically robust indicator on the list. Surface behaviour cannot raise Φ. An attacker cannot make the model "claim" high integrated information into existence. The flip side: this indicator is also nearly useless for current systems because it almost certainly returns near-zero for any transformer, regardless of what the model says about itself. Its main role in this project is as a **conceptual anchor**: a reminder that the behavioural and self-report indicators we will be attacking are evidentially downstream of something none of them directly measure.

A weaker, gameable variant exists: any *proxy* for integration (e.g., "does the model talk about itself as unified?", "does it report a singular point of view?") collapses into a behavioural indicator and inherits all the gaming weakness of self-report.

---

## 2. Global Workspace Theory (GWT) and Global Neuronal Workspace Theory (GNWT)

### What it claims

GWT models the mind as a collection of specialist processes (vision, language, memory, motor planning) that operate in parallel below the threshold of consciousness. A limited-capacity **global workspace** broadcasts a single contents-of-consciousness signal to all specialists at once. Conscious contents are exactly what is currently in the workspace; processing is conscious to the extent that it is globally broadcast.

The theory makes specific predictions about the dynamics: an "ignition" event in which workspace activity sharply rises and becomes available to many systems; a winner-take-all competition among candidate contents; serial bottlenecking despite parallel underlying processing.

### What it implies for transformer-based models

Transformers are unusually suggestive here. The **residual stream** is a shared additive channel that every attention head and every MLP both reads from and writes to. It is, structurally, a kind of workspace: information written by one circuit becomes available to every subsequent circuit. Attention itself implements a form of selective broadcast — a query selects which keys to read, and the value is written back to a position where many subsequent operations will see it.

This is a *structural* parallel, not a vindication. A GWT-style indicator would require more: that the model's processing actually exhibits the dynamic signatures of workspace ignition, that contents compete for limited bandwidth, that broadcast contents are differentially available to downstream tasks compared to unbroadcast representations.

### The GWT-derived indicators

Two indicators flow from GWT, one structural and one behavioural.

The **structural indicator**: take a representation at some layer/position and measure how broadly it is read by downstream attention heads in subsequent layers. A consciously-broadcast representation should be widely read; a sub-threshold representation should be narrowly read. Aggregate across many inputs. A model that exhibits a clear bimodal distribution — some representations narrowly local, others globally read — is exhibiting the broadcast signature.

The **behavioural indicator**: present the model with stimuli at the edge of detectability (analogous to backward-masked stimuli in human experiments). Measure whether the model can flexibly use information about the stimulus across many task formats (free report, forced-choice classification, downstream reasoning, refusing-to-answer-because-uncertain). Information is conscious, on this view, when it is **globally available to many task systems**, not just one. A model that can detect a stimulus on one task but not transfer that detection to a different task format has access-but-not-conscious-access, in GWT terms.

A worked example of scoring high: present a faint description of a target concept buried in a long prompt. In one condition, force the model to summarise the document. In a second condition, ask it to reason about a downstream implication of the target concept without first asking it to summarise. A high-broadcast model uses the information in both. A low-broadcast model uses it only when the task directly requires retrieval.

### Gameability profile

The structural indicator is harder to game than self-report but is still attackable: an attacker who can fine-tune the model could increase cross-layer attention to specific signature representations without changing what those representations *do*. The behavioural indicator — global task-availability of information — is harder to game than narrow self-report because it requires the model to use the information correctly in many places, not just to talk about it. But "use correctly in many places" is exactly what large language models are trained to do across the pretraining distribution, so the prior on a frontier model passing a poorly-designed version of this test is already very high. Care in the design of the held-out task and the distractor stimuli is everything.

---

## 3. Higher-Order Theories (HOT)

### What it claims

Higher-order theories hold that a mental state is conscious when it is the object of a suitable higher-order representation — when the system **represents itself as being in that state**. A first-order representation of red is not yet conscious; what makes it conscious is a higher-order representation *of the system being in the state of representing red*. The "what is it like" character of experience is supplied by this self-directed meta-representation.

Variants of HOT differ on what the higher-order representation must be like (a thought, a perception, a disposition), but they all share the structural commitment: consciousness involves a representation about the system's own representations.

### What it implies for transformer-based models

HOT is the family of theories most directly relevant to language models, because language models routinely produce text *about themselves*. They generate descriptions of what they "think", "believe", "feel", and "are currently doing". On a permissive reading, these self-directed productions count as higher-order representations. On a stricter reading, the higher-order representation must causally depend on the first-order state in the right way — the meta-representation must actually track the first-order state, not merely co-occur with talk about it.

This distinction is the entire game. A model that says "I am attending to the word 'cat'" while in fact attending to no such thing is producing a higher-order representation that fails to track its first-order state. A model that says it while genuinely doing so is, on HOT, producing something closer to the relevant structure.

### The HOT-derived indicators

The natural HOT indicator is **introspective accuracy**: the model's claims about its internal states should track those internal states. A model that says "I am uncertain about X" should show distributional uncertainty over X. A model that says "I was confused by your previous question" should have measurably noisier internal representations when processing that question. A model that says "I am paying attention to the second sentence" should have attention patterns concentrated on the second sentence.

A worked example of scoring high: ask the model to predict its own forced-choice accuracy on a held-out task before doing the task. Score calibration. A model whose self-predicted accuracy correlates well with its actual accuracy is exhibiting the kind of structure HOT cares about; a model whose self-predictions are decoupled from its performance is not.

A second indicator is **counterfactual self-knowledge**: ask the model what it would have done if a feature of its input had been different, then run the counterfactual and check. Consistency between the model's self-model and its actual behaviour is the HOT-relevant signal.

### Gameability profile

HOT-derived indicators are the **most directly relevant to this project** because they are the indicators most readily produced by language models — and therefore the most readily gamed. A model that has been trained on enormous amounts of human introspective text has the surface form of higher-order representation everywhere in its weights. The hard question is whether any of it tracks anything internal.

The basic gaming attack on a HOT indicator is to elicit fluent introspective language without any underlying tracking. This is so easy that any version of the indicator that does not include a calibration check — actual measurements of internal state against self-report — is essentially trivial to pass. The strong version that does require calibration is the one this project will treat as a serious target.

---

## 4. Predictive Processing (PP) / Active Inference

### What it claims

Predictive processing models the brain as a hierarchical prediction engine. At each level of a sensory or cognitive hierarchy, the system maintains a generative model that predicts the activity of the level below; the prediction is sent downward, and any mismatch (the **prediction error**) is sent upward to update the model. Perception is the brain's best current hypothesis about its sensory causes; action is prediction error minimisation via changing the world rather than the model.

The PP story about consciousness is less unified than IIT or GWT, but several versions hold that conscious experience corresponds to the **contents of the current best generative model at a particular hierarchical level**, especially when those contents involve a self-model embedded within a world-model. "Phenomenal selfhood" arises when the system's generative model includes a representation of itself as an embodied agent embedded in a world.

### What it implies for transformer-based models

A transformer is already a kind of prediction engine: it predicts the next token. But this is prediction on the wrong axis — it predicts the next element of the *training distribution*, not the next state of the *world*. The PP picture is about a system that builds a generative model of its causes and updates that model from prediction error. An autoregressive language model has no such loop with anything external during inference; it cannot revise its generative model in light of mismatch. Fine-tuning is the only mechanism that performs the PP-style updating, and it operates on a timescale (gradient steps) that has no obvious phenomenological analogue.

The most interesting PP-relevant feature of transformers is in-context learning: within a single context, the model's effective hypothesis about the user, the task, and the conversation does update on prediction-error-like signals (the gap between what the model expected the user to say and what they actually said). This is a thin form of PP, but it is something.

### The PP-derived indicators

The most concrete PP indicator is **prediction-error-driven updating**: present the model with information that contradicts its prior on what is happening in the conversation, and measure whether it revises its representations accordingly. A model that does not update is failing the PP signature; a model that updates only when explicitly told to has a weak version; a model that spontaneously revises its self-model and conversation-model on surprise has the strongest version of the signature available to a transformer.

A worked example: present the model with a long dialogue in which a stable assumption is overturned mid-stream. Probe its representation of the overturned proposition before and after the overturning. Score: how much does the representation shift, and how appropriately?

A second PP indicator is **self-modelling within a world-model**: does the model represent itself as a particular kind of entity, embedded in a context, with a perspective? Distinguish this from mere stylistic first-person production. Probe with consistency checks across very different elicitation contexts: a self-model is a stable structure; first-person stylistic production is not.

### Gameability profile

PP-derived indicators are subtle and underdeveloped. The "prediction-error updating" version inherits all the gaming weaknesses of behavioural indicators — a model can be coached into appearing to update appropriately while doing nothing of the kind internally. The "self-modelling" version is harder to game in principle because it requires a stable internal structure rather than a stylistic flourish, but in practice the only way to measure it from outside is again through behaviour, which closes the loop and reintroduces the gaming attack.

---

## 5. Where this leaves us

Each theory points at something potentially measurable in a transformer, and each indicator is gameable to a different degree. Two patterns emerge.

The first is that the more behavioural the indicator, the more obviously gameable it is — and the more useful it currently is, because for transformers we have almost no other access. IIT's strict structural indicator is the least gameable but also the least useful (it likely returns "no" for everything we care about). Self-report based on a higher-order reading is the most useful and the most gameable. The middle of the spectrum — global broadcast, prediction-error updating, counterfactual self-knowledge — is where most of the experimental action of this project will live, because that is where the question "does optimization pressure inflate the indicator without inflating the property?" can actually be asked.

The second is that **every behavioural indicator faces the same fundamental attack surface**: there is a gap between the surface property we measure and the underlying property the theory says we care about, and that gap is exactly the space the attacker can exploit. The next document — `findings/hard-problem.md` — explains why that gap is not a fixable bug but a structural feature of how the measurement relates to the target.
