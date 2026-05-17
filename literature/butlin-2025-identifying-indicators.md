## Citation
- **Title**: Identifying indicators of consciousness in AI systems
- **Authors**: Patrick Butlin, Robert Long, Tim Bayne, Yoshua Bengio, Jonathan Birch, David Chalmers, … (many coauthors)
- **Venue / year**: *Trends in Cognitive Sciences* (Opinion), 2025
- **Link**: `http://eprints.lse.ac.uk/130322/` (free PDF mirror)
- **Last reviewed**: w01

## One-paragraph takeaway
Butlin et al. argue that we can make **non-handwavy progress on AI consciousness** by taking mainstream *neuroscientific theories of consciousness*, deriving **indicator properties** implied by those theories, then empirically assessing whether particular AI systems satisfy them—using the results to **update our credences** (not to “prove” consciousness).

## What the authors claim (high level)
- **We need rigorous assessment methods** because there are serious risks of both **over-attribution** (wasting resources / making bad policy on “zombies”) and **under-attribution** (causing harms to conscious systems at scale).
- **Define the target carefully**: they focus on **phenomenal consciousness** (“something it is like”).
- **Theory-derived indicator method**: select *suitable* consciousness theories (credible + empirically implicating), derive testable indicators, and treat indicator evidence as probabilistic evidence bearing on consciousness.

## Relevance to indicator gaming (for digital minds)
- **Indicator(s) involved**: this paper is basically *the* canonical “indicator list” framing (theories → indicators → tests → credence updates).
- **Primary gaming failure mode(s)**:
  - Once indicators become targets (explicitly or implicitly), systems may be optimized to **satisfy the indicator** without satisfying what we hoped the indicator tracked (Goodhart-style failure).
  - Behavioral cues and even some internal proxies can be **mimicked or engineered**.
- **How this helps our project**: it gives a principled starting set of **candidate indicators** that we can try to **stress-test under optimization pressure**.

## Practical notes for our project
- **How to use this**: pick 1–2 candidate indicators derived from a theory (or a small set), implement a measurement procedure, then show a concrete “indicator ↑, intended property unclear / robustness ↓” result under optimization/selection.
- **Controls / hardening ideas** (implied by the method):
  - separate *training* vs *evaluation* indicator variants (holdouts)
  - ablations that break the “cheat” while keeping task competence
  - triangulate with alternative indicators (don’t rely on a single proxy)

## Local reference
- Extracted text snapshot: `sources/text/Butlin_Identifying_Indicators_TiCS_2025.txt`

