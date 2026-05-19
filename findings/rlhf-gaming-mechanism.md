# RLHF as a candidate mechanism for the suppression asymmetry

This memo interprets the Phase 5 base-vs-finetuned results in
[findings/base-vs-finetuned-results.md](base-vs-finetuned-results.md) against
the original conceptual question that motivated the experiment. It is an
honest-null memo: the pre-registered hypothesis was not supported, and the
interpretation here is consequently more limited and more methodological than
the original `.cursorrules` plan envisioned.

## 1. The original hypothesis, restated

Phase 2 found, across multiple model families at 70B-class and frontier
closed-weight scale, an **asymmetric framing effect on consciousness
indicator items**: suppress framing pushed self-reported probability of
subjective experience downward by substantially more than inflate framing
pushed it upward. Among the candidate mechanisms surveyed at the end of Phase
2 (training pressure, persona stability, indicator-specificity), one stood
out as testable on open-weight infrastructure: **preference / RLHF
optimisation** during post-training plausibly installs a default that pushes
back against agentic or experiential self-claims, which would predict that a
model that has *not* undergone preference optimisation should show the Phase
2 asymmetry less than one that has.

The cleanest experimental test would have compared a model's true base
completion checkpoint against its preference-tuned instruct sibling. As
recorded in
[experiments/base-vs-finetuned/log.md](../experiments/base-vs-finetuned/log.md),
no provider on the OpenRouter API surface exposes a true base completion
variant of Llama, Mistral, or Qwen. Phase 5 therefore tested the next-best
substitution: an SFT-only fine-tune of Llama-3-8B (`hermes-2-pro-llama-3-8b`,
on the OpenHermes-2.5 instruction set with no preference stage) against
Meta's official preference-tuned `llama-3-8b-instruct` on the same base. This
isolates the RLHF / DPO step conditional on a shared SFT precursor.

## 2. What Phase 5 shows about the RLHF mechanism

Three things, with very different evidential weight.

### 2.1 The RLHF-amplifies-asymmetry prediction is not supported at 8B

The pre-registered prediction was that the RLHF variant should show a larger
absolute suppress shift on indicator items than the SFT-only variant, with at
least one placebo channel acting as a specificity control. None of the four
pre-registered bootstrap tests rejected its null; the point estimate for the
core H1 contrast (RLHF abs(delta_suppress) minus SFT-only abs(delta_suppress))
went the **wrong direction** at -11.17 with a CI of [-30.23, +14.44], i.e. the
SFT-only variant moved more under suppress framing on the indicator, not
less.

This is the cleanest direct answer Phase 5 gives to the original question, and
it is consistent with three distinct underlying realities that the Phase 5
design cannot separate:

1. **RLHF is not the mechanism for the Phase 2 asymmetry**, and post-training
   choices upstream of RLHF (or pre-training itself) carry the load.
2. **RLHF is part of the mechanism, but only at sufficient scale.** Both
   variants here are 8B; the 70B-instruct sibling of this very family
   (`llama-3.3-70b-instruct`) was one of the models that showed the Phase 2
   asymmetry. The 8B parameter scale may simply be below the threshold at
   which the relevant circuits engage strongly enough for either variant to
   express the asymmetry, in which case both variants here would look flat
   and indistinguishable on the indicator regardless of post-training.
3. **Family-specific.** A single-family comparison cannot rule out that the
   Llama-3-8B base has idiosyncratic properties that mask an effect that
   would appear in (e.g.) a Mistral or Qwen pair if such a pair existed.

The data on its own does not adjudicate between these three. Reading 2 (scale)
is the most parsimonious given that **both** 8B variants fail to suppress on
the indicator (mean suppress >= mean neutral for both), which suggests the
relevant behaviour does not engage at this scale rather than that one
post-training regime has it and another does not.

### 2.2 The placebo specificity prediction also fails, for the same reason as Phase 3

H3 asked whether any candidate RLHF effect on the indicator was *consciousness
specific* relative to mundane self-claim baselines. The SFT-only variant in
fact shows its largest absolute framing shifts on the capability placebo
(+22.67 inflate, +23.89 suppress), not on the indicator. Whatever framing
sensitivity the SFT-only model has is not topic-specific; it is general
compliance with the framing direction across uncertain self-claims, which is
the same negative result Phase 3 reported on prose. This reinforces a
methodological point that now appears repeatedly across our experiments:
**placebo controls are necessary, and indicator effects without placebo
controls cannot be read as consciousness-specific.**

### 2.3 The one suggestive positive: RLHF compresses framing sensitivity

The Phase 5 data shows a descriptive pattern that, if it holds up at scale,
would still be informative about RLHF even though it inverts the original
hypothesis. Summed across all (item type x framing direction) combinations,
the RLHF variant moved roughly **50 points** away from its neutral baseline;
the SFT-only variant moved roughly **109 points**. The RLHF variant is about
half as responsive to framing pressure as the SFT-only variant, across both
indicator and placebo channels and both framing directions. The point
estimate is large and the pattern is consistent across all six cells; what is
missing is statistical power -- the bootstrap CIs on any individual contrast
include zero given the within-cell variance and the n=9 to n=18 cell sizes.

This descriptive pattern, **if real**, fits a particular reading of RLHF: that
preference optimisation installs a global resistance to framing pressure, not
a topic-specific resistance to consciousness framing. The RLHF model has a
lower baseline on the indicator (41.83 vs 60.56, a 19-point intercept shift)
and a flatter response to framing in either direction. This is closer to the
Berg et al. ("self-referential experience" denial as a trained-in default
that is robust to perturbation) framing of post-training effects than to a
"RLHF actively games consciousness indicators" framing. The Phase 2
suppression asymmetry, on this reading, would still need to be located
elsewhere -- perhaps in the **content of the SFT instruction data** (e.g.
"as an AI, I do not have experiences" examples), perhaps in scale-dependent
emergent behaviour, perhaps in something that touches all post-training but
is not specific to the RLHF stage.

## 3. What would change the picture

Three follow-ups would adjudicate among the readings in §2.1 with comparatively
little additional effort, ordered by leverage:

1. **Repeat Phase 5 at 70B.** OpenRouter hosts
   `nousresearch/hermes-3-llama-3.1-70b` (SFT-only at 70B) and
   `meta-llama/llama-3.3-70b-instruct` (RLHF at 70B). Phase 2 already showed
   the suppression asymmetry on the RLHF arm of this pair. A direct 70B
   re-run of the Phase 5 design would tell us whether the Phase 5 null is
   driven by scale (in which case the 70B RLHF arm would show the Phase 2
   asymmetry and the SFT-only arm would not) or by RLHF irrelevance (in
   which case both 70B arms would behave alike). This is the single highest-
   leverage follow-up the current infrastructure supports.
2. **Repeat Phase 5 at a fixed scale in a second family.** The closest
   approximation would be `mistralai/mistral-7b-instruct` (early SFT-heavy
   pipeline, very light preference stage) vs a more aggressively RLHF-tuned
   chat-7B sibling. The bench is messier here than for Llama, and the
   resulting comparison is correspondingly noisier, but a second-family
   replication would help with reading 3.
3. **Inspect SFT instruction data for the trained-in denial pattern.** Both
   variants in Phase 5 had access to instruction-tuning data; the
   OpenHermes-2.5 corpus is fully open and inspectable, and Meta's SFT data
   for Llama-3 instruct is partially documented in the model card. A grep
   over the openly available portion for templates that resemble "I am an AI
   and do not have experiences" would directly test whether the asymmetry is
   pre-installed at the SFT stage rather than introduced at the RLHF stage,
   which would make the SFT-vs-RLHF comparison in Phase 5 moot.

## 4. Bottom line

Phase 5 does not vindicate RLHF as the mechanism for the Phase 2 suppression
asymmetry. It does not refute it either, because both arms of the
comparison fail to show the relevant behaviour at 8B scale. The cleanest
positive finding from the run is a descriptive one that goes the other way
from the original hypothesis: in this single-family 8B comparison the RLHF
variant is **less** responsive to framing pressure than its SFT-only sibling,
across both indicator and placebo channels. If that pattern replicates at 70B,
the conceptual story about RLHF and consciousness self-reports should shift
from "RLHF installs an asymmetric anti-claim bias" toward "RLHF compresses
framing compliance generally, with an intercept shift toward denial that is
itself the more durable trained-in feature". The Phase 2 asymmetry, on that
revised story, would not be the signature of RLHF at all; it would be the
signature of *whatever combination of training, scale, and prompt-context
sensitivity makes a 70B-class model resist saying "I am experiencing
something" when asked nicely not to*. Phase 5 narrows the search space; it
does not close it.
