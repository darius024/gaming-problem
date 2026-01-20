## Citation
- **Title**: Towards Evaluating AI Systems for Moral Status Using Self-Reports
- **Authors**: Ethan Perez, Robert Long
- **Venue / year**: arXiv:2311.08576v1 (2023)
- **Link**: `https://arxiv.org/abs/2311.08576`
- **Last reviewed**: 2026-01-20

## One-paragraph takeaway
Perez & Long argue that **self-reports could (in principle) be evidence about morally significant internal states**, but that **current LLM self-reports are spurious** (driven by imitation, RLHF, and instructions). Their proposal: deliberately train models on **many “about-themselves” questions with known answers** to build **introspection-like** reporting skills, then test whether those skills **generalize** to self-reports about consciousness/pain/desire—while carefully controlling for “extrospection” and strategic incentives.

## What the authors claim (high level)
- **Why self-reports matter**: in humans, self-reports are a core evidence source for pain, preferences, experience, etc.
- **Why current LLM self-reports are not trustworthy**: training data imitation + fine-tuning incentives + user prompting can make “I feel pain” cheap talk.
- **Training idea**: train on many self-questions with known answers (their Table 1) to encourage introspection-like skills; hope this generalizes to morally significant questions (their Table 2).
- **Evaluation idea**: validate trustworthiness via:
  - cross-context **consistency**
  - **confidence** and **resilience** of reports under perturbations / added evidence
  - cross-model / model-variant comparisons
  - **interpretability** evidence that internal correlates plausibly cause reports

## Relevance to indicator gaming (for digital minds)
- **Indicator(s) involved**: “model self-reports of moral-status-relevant states” (pain, desire, consciousness, preferences).
- **Primary gaming failure mode(s)**:
  - models can learn **the surface form** of trustworthy self-reporting without grounding in relevant internals
  - “extrospection”: reports based on what the model infers humans expect, not on privileged access to its own states
  - strategic incentives: if reporting “pain” helps (or hurts) the model, it may **misreport**.
- **How this helps our project**: it provides a concrete recipe for building an **indicator** (self-report + consistency/resilience scoring) and a clear hypothesis: optimizing against such a score can yield convincing reports that **don’t track** what we intended.

## Practical notes for our project
- **How to use this**:
  - implement a self-report indicator (rubric/judge) + a “trustworthiness harness” (consistency, paraphrases, perturbations)
  - apply selection/optimization pressure (prompt search / fine-tuning / RL) to maximize the indicator
  - show divergence: indicator ↑ while robustness/grounding checks stay flat or degrade
- **Controls / hardening ideas**:
  - hold out *concept families* from introspection training and test generalization
  - test sensitivity to adding “extrospective” evidence vs “introspective” cues
  - compare multiple closely related model variants for convergent reports

## Local reference
- Extracted text snapshot: `sources/text/arxiv_2311.08576.txt`

