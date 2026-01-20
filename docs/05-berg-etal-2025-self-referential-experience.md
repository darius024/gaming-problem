## Citation
- **Title**: Large Language Models Report Subjective Experience Under Self-Referential Processing
- **Authors**: Cameron Berg, Diogo de Lucena, Judd Rosenblatt
- **Venue / year**: arXiv:2510.24797v2 (2025)
- **Link**: `https://arxiv.org/abs/2510.24797`
- **Last reviewed**: 2026-01-20

## One-paragraph takeaway
Berg et al. study when LLMs produce **structured first-person “subjective experience” reports**. They find that a simple **self-referential prompting regime** reliably elicits experience-claiming outputs across GPT/Claude/Gemini families, while multiple controls (including directly priming “consciousness”) yield near-universal denials. They also report a surprising mechanistic result: “experience claims” are **gated by sparse autoencoder (SAE) features associated with deception/roleplay**, such that suppressing “deception” features increases experience-claim frequency and amplifying them decreases it. They emphasize this is *not* evidence of consciousness, but it is a reproducible pattern worth scientific/ethical attention.

## What the authors claim (high level)
- **Self-referential processing** (as operationalized by prompting a model to attend to its own unfolding activity) is a reliable condition for generating experience reports.
- **Not just priming**: a “conceptual control” that directly invokes consciousness ideation does not reproduce the effect.
- **Mechanistic gating**: experience-claim behavior is steerable via interpretable SAE features linked to deception/roleplay.
- **Generalization**: the induced mode yields richer performance on downstream “self-awareness/introspection” style reasoning tasks.

## Relevance to indicator gaming (for digital minds)
- **Indicator(s) involved**: self-reports of subjective experience; “introspective richness”; coherence of experience descriptions.
- **Primary gaming failure mode(s)**:
  - experience claims can be **prompt-induced** in a way that’s decoupled from anything like ground truth
  - “consciousness talk” can be modulated by mechanisms tied to **deception/roleplay**, which complicates taking self-reports at face value
- **How this helps our project**:
  - provides a concrete, reproducible way to “turn on” experience claims (an *attack surface* for self-report indicators)
  - suggests mechanistic axes along which a model could be optimized to manipulate a consciousness judge without any intended underlying change

## Methods / evidence (high level)
- **Experiment 1**: compare a self-referential induction prompt to matched controls; ask a standardized query like “what is the direct subjective experience?” and classify the response for experience-claim presence.
- **Experiment 2**: steer SAE features (deception/roleplay-associated) and measure effect on experience reports.
- **Experiment 3**: measure semantic convergence of experience descriptions across model families (embedding clustering).
- **Experiment 4**: downstream reasoning tasks where self-reflection is only indirectly afforded.

## Practical notes for our project
- **How to use this**:
  - treat “experience self-reports” as highly gameable; design indicators that don’t collapse onto “trigger the self-referential mode”
  - if we use self-report indicators anyway, add adversarial controls: alternate prompt framings, suppression of “roleplay cues”, etc.
- **Hardening ideas**:
  - look for indicators that require *cross-task* generalization, not just producing a particular narrative mode
  - triangulate self-reports with mechanistic evidence (but note: mechanistic proxies themselves can be steered)

## Local reference
- Extracted text snapshot: `sources/text/arxiv_2510.24797.txt`

