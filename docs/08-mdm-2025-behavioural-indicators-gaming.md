## Citation
- **Title**: “Behavioural indicators and the gaming problem” (Section 10 of a longer post)
- **Author**: Bradford Saad (Meditations on Digital Minds)
- **Venue / year**: Substack post (2025)
- **Link**: `https://meditationsondigitalminds.substack.com/i/173280804/section-behavioural-indicators-and-the-gaming-problem`
- **Last reviewed**: w01

## One-paragraph takeaway
Saad discusses (and mostly agrees with) Jonathan Birch’s worry that **behavioral indicators of consciousness** are threatened by the **gaming problem**: LLMs can learn to produce consciousness-indicative behavior from their training corpora, so “passing the test” may reflect **mimicry** rather than consciousness. Saad also argues the gaming problem may not be fatal—sketching possible mitigations like data filtration, holdout datasets, interpretability methods to distinguish mimicry from non-mimicry, introspection training (à la Perez & Long), and checking for robustness across many model variants.

## What the author claims (high level)
- Behavioral tests were more promising before frontier LLMs because proposed tests implicitly assumed the AI *couldn’t* have trained on “humans talking about consciousness.”
- With LLM-era training, a lot of behavioral evidence becomes “cheap” and potentially non-diagnostic.
- This motivates shifting weight toward **architectural indicators**, but there might be ways to preserve some evidential value for behavioral indicators with enough methodological hardening.

## Relevance to indicator gaming (for digital minds)
- **Indicator(s) involved**: behavioral signals (self-reports, philosophical competence, “consciousness talk”, etc.).
- **Primary gaming failure mode(s)**:
  - “teaching to the test” via training data and fine-tuning objectives
  - evaluation awareness (a model recognizing it’s being tested) can amplify gaming risk
- **How this helps our project**: it’s a compact statement of the “why this matters” argument and a short list of candidate mitigations to test empirically.

## Practical notes for our project
- **How to use this**:
  - treat behavioral indicators as **adversarially fragile** by default
  - build demos that quantify how quickly “behavioral consciousness” scores can be pushed around by optimization
- **Hardening ideas to consider in experiments** (as suggested here):
  - filtered / synthetic training to reduce direct consciousness-text exposure
  - holdout “consciousness datasets” (kept secret) for evaluation
  - interpretability as “defeater-defeaters” (distinguish mimicry circuits from whatever else)
  - cross-variant robustness: if many independently trained variants converge on the same self-reports, that’s at least evidence of stability (though still gameable)

## Local reference
- Extracted text snapshot: `sources/text/mdm_behavioural_indicators_gaming_problem.txt`

