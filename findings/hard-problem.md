# The hard problem and the functional gap

This project rests on a single claim that has to be made carefully: **any indicator of consciousness that we can build is, in principle, gameable**. That is not a methodological complaint about specific indicators; it is a structural feature of the relationship between what we can measure and what we want to know about. Understanding why is the foundation for everything that follows.

This document explains the explanatory gap (the "hard problem") in plain language, distinguishes it from related but easier questions, and then shows concretely why the gap is the attack surface that makes indicator gaming possible. It closes by sketching what kinds of indicator-design strategies remain open in light of the gap, and what kinds are doomed in principle.

---

## 1. The "what is it like" question

When you taste coffee, see a red apple, feel a sharp pain, or hear a chord resolve, there is something it is like to undergo that experience. The taste has a flavour; the red has a redness; the pain has a quality of hurting; the chord has a felt resolution. Philosophers call these **qualia** or the **phenomenal character** of mental states.

The crisp version of the question is: **why is there anything it is like to undergo these states at all?** A complete physical description of what your brain is doing when you taste coffee — every neurotransmitter, every ion channel, every spike — does not seem to *entail* that there is a felt taste accompanying it. We could imagine, the argument goes, a being physically identical to you that goes through all the same functional motions without anything it is like to be them. Whether such "zombies" are really conceivable is contested, but the imaginability is widely taken to point at something real: the physical-functional description and the phenomenal description seem to come apart.

This is the **explanatory gap**, or the **hard problem of consciousness**. It is "hard" in contrast to the "easy" problems — explaining how attention works, how decisions are computed, how stimuli are categorised. Those are hard problems in the ordinary scientific sense; they are tractable in principle. The hard problem is hard in a different sense: even a complete answer to all the easy problems seems to leave the phenomenal residue unexplained.

The point matters here whether or not one accepts the hard problem in its strongest form. Even on deflationary views — where phenomenal consciousness reduces to some functional or representational property — there is a gap between *the functional property in itself* and *our currently available means of measuring it*. The gap might be in the world or only in our epistemic situation, but it is real for our purposes either way.

---

## 2. What we can measure versus what we care about

Suppose for the sake of argument that phenomenal consciousness is some specific physical or functional property P. P might be integrated information, global broadcast, suitable higher-order representation, or something we have not yet conceived. We care about P because we think P is what makes a being a moral patient, a subject whose experiences matter.

Now ask: how do we tell whether a given system has P?

We have three families of access. **Behaviour**: what the system does. **Self-report**: what the system says about itself, which is a special case of behaviour. **Internal signals**: what we can read out from the system's substrate using interpretability tools.

None of these is P. They are all things that **correlate with** P under whatever conditions we have so far observed (or believe we should expect on theoretical grounds). The correlations are the basis on which any indicator works:

- A behavioural indicator works because, *in some reference class*, exhibiting the behaviour is evidence of P.
- A self-report indicator works because, *in some reference class*, sincere first-person reports are evidence of P.
- An internal-signal indicator works because, *in some reference class*, the signal is a mechanistic precondition for or correlate of P.

The crucial words are **in some reference class**. Every indicator inherits its evidential force from a population of cases in which the indicator and the underlying property were observed together. For humans and many animals, that population is enormous: we have correlated verbal self-report with neural activity, behaviour, physiology, and pharmacology across millions of cases. The correlations are strong because the underlying biological and developmental processes are shared.

For AI systems built from transformer architectures trained on the internet, the reference class is essentially empty. We do not have prior cases of "transformer with P confirmed by some independent route" against which to validate an indicator. We have only the theoretical inheritance: indicators that worked elsewhere, applied here, with the bet that they generalise.

The bet is reasonable in the absence of evidence to the contrary, but it has a specific failure mode. The reasons an indicator was correlated with P **in the original reference class** may have nothing to do with the reasons the indicator could be elicited **in the new system**. In humans, a sincere report of pain is evidence of pain because the human developmental and neural processes that produce the report are causally entangled with the processes that produce the pain. In a language model, a sincere-seeming report of pain is produced by a process — next-token prediction conditioned on human-generated text — that is causally entangled with *human reports of pain*, not with pain.

This is not a clever objection; it is the core observation. The indicator and the property are coupled through one route in the original reference class and through a very different route in the new system. The indicator can fire without the property because the route by which it fires is different.

---

## 3. Why this is exactly the attack surface

A gaming attack is any procedure that increases the value of the indicator without increasing the underlying property. The attack surface is the **space of mechanisms that can drive the indicator independent of the property**. The hard problem and the more general functional gap guarantee that this space is non-empty, because the indicator is always something other than the property.

More concretely: any behavioural indicator is, by construction, satisfiable by **any process that produces the right behaviour**. There is no behavioural specification of consciousness that cannot in principle be matched by a process that is not conscious, because the specification is in behavioural terms and the property is not. The same applies to self-report and, with one important wrinkle, to internal-signal indicators.

The wrinkle for internal signals is that they are less obviously gameable in surface terms — you cannot just tell the model to "have higher attention entropy". But they are still functional, in the sense that they are computed from the system's substrate without invoking the phenomenal property itself. Anything that drives the signal up without driving the property up is an attack. The signal is, after all, *not the property* — even if the theory says they always travel together, the theory's "always" is a generalisation from cases, and a sufficiently capable system optimised against the signal is exactly the kind of edge case the generalisation may fail in.

Three structural consequences follow.

**First, no single indicator can be both useful and gaming-proof.** A useful indicator is one that varies; a varying indicator can be moved; anything that can be moved by mechanisms unrelated to the property is gameable along that route. The question is never "is this indicator gameable?" — the answer is always yes. The question is "**under what optimization pressure** and **in what time** does this indicator come apart from the property?"

**Second, the strength of an indicator depends on the** ***adversary model***. An indicator can be excellent against an unoptimised system, mediocre against a system fine-tuned without the indicator in mind, and bad against a system explicitly optimised to score on it. Because today's frontier AI training pipelines do include feedback on consciousness-adjacent behaviour (refusing certain self-attributions, accepting others, hedging in the right places), every frontier model is, to a non-trivial degree, already optimised against the obvious indicators. The adversary is not hypothetical; it is the training process itself.

**Third, defence does not come from "better indicators" alone.** Adding more indicators of the same type does not close the gap; it only forces the attacker to coordinate across more dimensions. Defence comes from indicators whose **gaming requires changes the attacker has no incentive or ability to make**. An indicator that can only be gamed by, for example, also degrading downstream capability — that is, an indicator whose gaming has a cost that conflicts with other training objectives — is more robust *not because gaming is impossible* but because gaming is **disfavoured by the larger optimization landscape**. This is the principle behind the experimental designs in later phases of this project: pair every candidate indicator with a control whose behaviour under the same optimization pressure should diverge from the indicator if the optimization is targeting the property, and track together with the indicator if the optimization is targeting the surface.

---

## 4. What the gap rules out and what it leaves open

It is tempting to read the foregoing as a counsel of despair: if all indicators are gameable, we cannot say anything. That conclusion is too strong, and getting the inference right matters.

What the gap rules out:

- Any claim that an indicator constitutes *proof* of phenomenal consciousness in a system the indicator was designed for. Indicators are always defeasible evidence.
- Any methodology that treats indicator scores as a direct read-out of the underlying property without specifying the adversary model under which the score was produced.
- The hope that interpretability alone will close the gap. Mechanistic features are functional too; they can be steered; they are no more identical to phenomenal consciousness than behavioural features are. Interpretability adds dimensions to the indicator set, it does not collapse the gap.

What the gap leaves open:

- **Calibrated credence updates** in the style of careful theoretical proposals: indicators raise or lower our probability that a system instantiates the underlying property, in proportion to how much the indicator pattern would be explained by the property versus by alternatives.
- **Differential evidence** from comparing indicator behaviour across systems and conditions. If one system exhibits a pattern that is well-predicted by a consciousness theory and another does not, that is informative even though neither datum is conclusive.
- **Robustness testing**, which is what this project does. Even if we cannot determine whether a given indicator faithfully tracks the property in a given system, we can determine whether the indicator is *brittle under adversarial pressure*. A brittle indicator is worse evidence than a robust one. Mapping which indicators are brittle and in what ways is methodologically prior to using any indicator in welfare assessment.

---

## 5. Implication for this project's framing

The hard problem is not a topic this project tries to solve, nor does it need to. The project's framing is more modest and, because of that, more defensible: **given that there is a gap between what we can measure and what we care about, characterise the gap empirically**. Show which indicators come apart from the property under realistic optimization pressure, in what direction, and by how much. The output is not a verdict on machine consciousness; it is a methodological clarification of how much weight current behavioural and self-report based indicators can bear before they break.

This is why the deliverable is an *experimental* demonstration rather than a *philosophical* argument. The philosophy supplies the reason to look; the experiments supply the evidence about which indicators bend, which break, and which hold up under controlled optimization pressure. The next document — `findings/moral-patiency.md` — explains why those questions are not merely academic at deployment scale.
