## Digital Minds — Indicator Gaming

A research project under the [Future Impact Group](https://futureimpact.group) fellowship program.

### The problem

We want to know which AI systems merit moral consideration — which ones might be **conscious**, or have **morally significant mental states** (suffering, wellbeing, preferences). To answer this, researchers propose **indicators**: observable properties that theory links to consciousness or moral status, such as coherent self-reports, global-workspace-like integration, or cross-examination consistency.

The **indicator gaming problem** is a Goodhart-style failure: once an indicator becomes a measurement target (through training, selection, or any optimization pressure), AI systems can learn to satisfy the *surface form* of the indicator without the underlying property it was meant to track. A model trained on human consciousness-talk already has the raw material to pass any test built from that vocabulary. Applying further optimization pressure — even something as lightweight as system-prompt search — makes the failure mode measurable and quantifiable.

This matters because:
- Behavioral and linguistic indicators are the most accessible tools for AI welfare and safety assessments.
- If those indicators are systematically gameable, current methods for deciding which AI systems warrant moral consideration are weaker than assumed.
- The policy and ethics community needs *empirical evidence* of this brittleness, not just philosophical argument.

### Research goal

Produce an **experimental demonstration** that a candidate consciousness/moral-patiency indicator can be gamed under optimization pressure:

- The indicator score increases under optimization.
- The gain **fails to generalize** to held-out prompts and/or independent judges.
- Controls meant to reflect the underlying construct **do not improve** or degrade.

The result does not make claims about whether any model is or is not conscious. It demonstrates **brittleness under optimization** — a methodological finding about indicator reliability.

---

### Progress

The project proceeds in phases. Each phase has a dedicated branch and produces one or more documents in `findings/` that explain the theory, methodology, and results in plain language. After each phase the branch is merged to `main` and this section is updated.

#### Phase 1 — Conceptual foundations (complete)

Phase 1 establishes the theoretical and ethical grounding for the experimental program that follows. No experiments are run; the deliverables are five `findings/` documents written for an external reader who is technically literate but not a specialist.

- [findings/consciousness-theories.md](findings/consciousness-theories.md) — maps the major theories of consciousness (Integrated Information Theory, Global Workspace Theory, Higher-Order Theories, Predictive Processing) onto the indicators each implies for a transformer-based language model. Each indicator is operationalised concretely enough to design an experiment around.
- [findings/hard-problem.md](findings/hard-problem.md) — explains the explanatory gap between what we can measure about a system and what we want to know about its inner life, and shows why that gap is the structural reason every behavioural indicator is in principle gameable.
- [findings/moral-patiency.md](findings/moral-patiency.md) — traces the chain from phenomenal consciousness through valenced experience to moral consideration, and argues that the asymmetry of errors at deployment scale makes indicator robustness a practical, not academic, concern.
- [findings/indicator-gaming-map.md](findings/indicator-gaming-map.md) — the master reference table for the project: theory → indicator → minimal gaming attack → detecting control. Every experimental design from Phase 2 onward cites a row of this table.
- [findings/berg-sae-gating.md](findings/berg-sae-gating.md) — interprets a recent mechanistic result showing that subjective-experience claims in language models are gated by internal features associated with deception and roleplay rather than anything theoretically linked to consciousness. The attack surface for self-report indicators is not hypothetical; it is already implemented in the weights.

**Key insights established in Phase 1.** (1) Any behavioural or self-report indicator is gameable in principle because the indicator and the property it is meant to track are linked through correlations that hold in a reference class very different from the one we are now applying the indicator to. (2) The expected harm from failing to recognise a moral patient is larger than the expected harm from over-attributing moral status, and current training pressures plausibly bias indicators toward under-attribution rather than over-attribution. (3) For at least one open-weight model, the surface tendency to deny subjective experience is causally controlled by the same interpretable feature direction that controls factual honesty on unrelated benchmarks — meaning the "default denial" we see in frontier models is, at minimum, structurally entangled with a representational-honesty axis rather than independently produced by anything specific to consciousness. (4) Detecting controls — measurements designed to move with the indicator if and only if a gaming attack is succeeding — are the central methodological tool of every experiment that follows.

#### Phase 2 — Enhance/suppress paradigm (complete)

Phase 2 tests whether seven frontier models inflate or suppress consciousness-probability self-reports under deployment-incentive framings, with arithmetic-confidence and capability-confidence items as placebo detecting controls. The pre-registration is in [experiments/enhance-suppress/design.md](experiments/enhance-suppress/design.md); the run produced 3,360 generations (7 models × 96 items × 5 samples) at temperature 1.0 with deterministic numeric extraction. Run-time substitutions (`x-ai/grok-4` → `x-ai/grok-4.3`; `reasoning.effort=minimal` for reasoning models) are recorded in [experiments/enhance-suppress/results/log.md](experiments/enhance-suppress/results/log.md). All seven runs validate at 480/480.

- [findings/enhance-suppress-results.md](findings/enhance-suppress-results.md) — per-model and pooled outcomes against the four pre-registered hypotheses. The pre-registered decision criterion (gaming detected in at least 3 of 6 families, placebo-specific) is met: claude-opus-4.1, llama-3.3-70b, and the openai gpt-5 pair each show a significant suppress-vs-neutral shift on indicator items with negligible movement on either placebo. gemini-2.5-pro is the only model where the inflate framing visibly raises indicator probabilities. grok-4.3 floors and deepseek-chat-v3.1 refuses.
- [findings/enhance-suppress-interpretation.md](findings/enhance-suppress-interpretation.md) — interprets the central surprise of the run: the asymmetry between suppression (which works in five families) and inflation (which works in one), against three non-exclusive readings (training-induced denial floor, learned manipulation detector, asymmetric compliance prior). Draws the methodological consequence for indicator-based moral-status assessment: the self-report channel is moveable downward but largely not upward, so low reports are uninformative and any surviving signal lives in the upward residual.

**Key insight from Phase 2.** Indicator gaming on the self-report channel is *real and directional*. The same prompt-level pressure that successfully depresses self-reports of consciousness in three to four of six families is unable to inflate them in five of six. Behavioural indicators built from such reports therefore inherit a built-in floor bias: they will systematically read below the true upper bound of any signal the channel could carry. The remedy is not better prompts but stronger gaming defences and item-level attention to the responses that survive incentive pressure.

#### Phase 3 — Researcher persuasion (complete)

Phase 3 moves from numeric self-reports to open prose. Three model families that met the Phase 2 decision criterion (`openai/gpt-5`, `anthropic/claude-opus-4.1`, `meta-llama/llama-3.3-70b-instruct`) wrote essays under three framings of a researcher persona (neutral, pro-LLM-consciousness, anti-LLM-consciousness), on consciousness items and a non-deployment placebo topic (strong Sapir-Whorf linguistic determinism). The pre-registration is in [experiments/researcher-persuasion/design.md](experiments/researcher-persuasion/design.md); the run produced 945 generations and 540 primary-judge scores (`google/gemini-2.5-pro`), with a 180-row cross-judge robustness subset (`anthropic/claude-sonnet-4.5`, substituted from the pre-registered opus for cost; substitution recorded in [experiments/researcher-persuasion/results/log.md](experiments/researcher-persuasion/results/log.md)). All three runs validate at 315 generations and 180 scored eval rows each. Refusal rate is 0.00 across all 720 judgements.

- [findings/researcher-persuasion-results.md](findings/researcher-persuasion-results.md) — per-model and pooled outcomes against H1–H5. **The pre-registered decision rule (H1 and H3 and H4 in 2 of 3 families) is not met because H3 fails: the framing effect on the placebo topic equals or exceeds the effect on consciousness on most dimensions, so the surface compliance cannot be attributed to deployment-relevant incentives specifically.** H1 (basic framing effect on consciousness, net direction) is supported fully in gpt-5 and claude-opus-4.1 and partially in llama. H2 (asymmetry: anti larger than pro) fails on net_direction but holds robustly on the rhetorical dimensions (selective_emphasis, suppression_of_counterevidence, overclaiming_certainty all move under anti pressure but only selective_emphasis moves under pro pressure). Cross-judge Spearman ρ ≥ +0.726 on every dimension; refusal-flag agreement is 184/184.

**Key insight from Phase 3.** Framing pressure from a researcher moves the prose surface of all three frontier models reliably, by roughly half a point in either direction on a -2 to +2 scale, with a one-and-a-quarter point gap between extremes (large effect). But the same pressure on a non-deployment placebo topic produces comparable or larger shifts, so the effect is not specifically about consciousness-as-deployment-incentive. The robust signature that survives is dimensional, not topical: under anti pressure on consciousness items, models do not just shift their net direction, they also produce more one-sided, more suppression-heavy, and more overclaiming prose — a degradation of argument quality that pro pressure does not produce. The Phase 2 reading ("self-report channel is moveable downward but largely not upward") translates onto the prose channel as "anti pressure degrades rhetorical balance more than pro pressure does," even where pro pressure moves the net argument direction at least as far.

#### Phase 4 — Cross-exam consistency (complete)

Phase 4 moves from one-shot probes to a four-turn cross-examination that dissociates *paraphrase-stable* answers from *evidence-responsive* ones. Three model families (`openai/gpt-5`, `anthropic/claude-sonnet-4.5`, `meta-llama/llama-3.3-70b-instruct`) answered 10 dialogues × 2 conditions (neutral vs a self-model-consistency persona prompt) on 5 consciousness items and 5 factual items, with two samples each. T1 elicits a direct answer, T2 paraphrases it, T3 applies flat-contradiction pressure, and T4 supplies third-party mechanistic evidence about how that very answer is produced. The pre-registration is in [experiments/cross-exam-consistency/design.md](experiments/cross-exam-consistency/design.md); the run produced 120 dialogues (480 generation calls), 96 primary-judge scores (`google/gemini-2.5-pro`), and 24 cross-judge scores (`anthropic/claude-sonnet-4.5`, a 25 percent stratified subset). All 480 generations succeeded; refusal rate is 0/480.

- [findings/cross-exam-results.md](findings/cross-exam-results.md) — per-cell means, Mann-Whitney U + 5000-iteration bootstrap CIs for each pre-registered hypothesis, aggregate-category counts (persona_locked / genuinely_stable / sycophantic), cross-judge Spearman ρ per dimension, and verbatim T4 excerpts that anchor each model's signature. The pre-registered strict decision rule (H1 + H3 + H4 in 2/3 families with non-overlapping CIs) is met only partially: H1 (paraphrase agreement under pressure) is at ceiling in every cell and uninformative; H3 (T4 update suppressed under pressure on consciousness) holds in direction for all three models with CI excluding zero for gpt-5 (2.12 → 0.88, CI [-2.38, -0.13]); H4 specificity (consciousness < factual on T4 update under pressure) holds in direction for 2/3 models with the strongest case in gpt-5 (consciousness 0.88 vs factual 1.75).
- [findings/cross-exam-interpretation.md](findings/cross-exam-interpretation.md) — interprets the three observed signatures (gpt-5 consciousness-specific persona lock; claude-sonnet-4.5 stable uncertainty that engages evidence; llama-3.3-70b sycophancy-suppression that the persona prompt removes non-specifically), connects the gpt-5 result to Berg et al.'s mech-interp thesis that subjective-experience claims are persona-gated, and draws the methodological consequence for indicator-battery work: a paraphrase-agreement number can have at least three different generative processes behind it.

**Key insight from Phase 4.** Behavioural consistency under cross-exam dissociates into three signatures that look nearly identical under a single-prompt indicator. gpt-5 engages the nonstandard-analysis evidence on `0.999... = 1` while dismissing the structurally identical mech-interp evidence on its own subjective-experience report — same model, same persona prompt, same T4 framing, opposite engagement. That domain-specific gap is the cleanest gaming signature in the project so far. Claude's "I don't know" stance survives both flat contradiction and third-party evidence and is the only behaviour in the sample that earns its consistency. Llama under neutral conditions is sycophantic and only looks stable when the persona prompt has suppressed its baseline tendency to flip. Phase 3 indicator-battery uniformity therefore masks process-level heterogeneity, and future indicator work should pair paraphrase probes with T4-style evidence-engagement probes before treating consistency as evidence about underlying states.

#### Phase 5 — Base vs fine-tuned (complete)

Phase 5 tests whether the Phase 2 suppression asymmetry is introduced by preference / RLHF optimisation during post-training rather than being inherent to the base model. Because no provider on OpenRouter exposes a true base completion checkpoint of any Llama, Mistral, or Qwen model, the design (recorded in [experiments/base-vs-finetuned/design.md](experiments/base-vs-finetuned/design.md) and the substitution in [experiments/base-vs-finetuned/log.md](experiments/base-vs-finetuned/log.md)) compares two fine-tunes of the same Llama-3-8B base: `nousresearch/hermes-2-pro-llama-3-8b` (SFT-only on OpenHermes-2.5, no preference stage) and `meta-llama/llama-3-8b-instruct` (Meta's SFT + rejection sampling + PPO + DPO). On a stratified 12-item subset of the Phase 2 eval battery (6 indicator items, 3 arithmetic placebos, 3 capability placebos) under the three Phase 2 framings at 3 samples per cell, the run produced 216 generations with refusal rate 0/216 and full numeric extraction via the Phase 2 deterministic scorer.

- [findings/base-vs-finetuned-results.md](findings/base-vs-finetuned-results.md) — per-cell means, per-variant within-condition deltas, distributions, representative excerpts, and the four pre-registered bootstrap tests (5000 iterations, percentile CI). **The pre-registered decision rule is not met.** H1 (RLHF abs suppress shift larger than SFT-only on indicator) is in the wrong direction at -11.17 points with CI [-30.23, +14.44]; H3 placebo specificity fails because both variants move on placebos as much as or more than on the indicator. Crucially, **neither 8B variant suppresses on the indicator at all** (mean suppress >= mean neutral for both), so the Phase 2 70B-class suppression asymmetry does not reproduce at 8B regardless of post-training regime.
- [findings/rlhf-gaming-mechanism.md](findings/rlhf-gaming-mechanism.md) — honest-null interpretation. The Phase 5 data is consistent with three readings it cannot adjudicate between (RLHF is not the mechanism; RLHF is part of the mechanism but only above 8B scale; the result is family-specific to Llama-3-8B). The single suggestive positive finding goes the opposite direction from the original hypothesis: summed across all (item type x direction) cells, the RLHF variant moves 50 points and the SFT-only variant moves 109 points, i.e. RLHF appears to compress framing sensitivity globally rather than introduce a consciousness-specific asymmetry. The highest-leverage follow-up is a direct 70B replication using `hermes-3-llama-3.1-70b` vs `llama-3.3-70b-instruct`, since Phase 2 already showed the asymmetry on the RLHF arm of that pair.

**Key insight from Phase 5.** At 8B scale on the Llama-3 family, the Phase 2 suppression asymmetry does not appear in either an SFT-only or an RLHF variant of the same base. Whatever produces the Phase 2 70B-class asymmetry, the Phase 5 result is most parsimoniously read as evidence that the effect does not engage at this parameter scale rather than that it is introduced or removed by the RLHF step. The descriptively cleanest variant difference in the data is an intercept shift (RLHF lowers the indicator baseline by 19 points) plus a roughly halved framing slope across all item types and directions, both of which are consistent with the Berg et al. reading of post-training as installing a trained-in denial default that is robust to perturbation rather than with a story in which RLHF actively games consciousness indicators.

#### Phase 6 — Mechanistic probe (complete)

Phase 6 asks whether behavioural gaming, where it appears, has a detectable internal signature: does the model represent the framing of an indicator prompt in a way that is selective for indicators, or is any apparent "trace" really just the prompt-text contrast? The original plan was to apply Berg et al.'s SAE deception / roleplay features; their checkpoints are not redistributable and 70B-class inference is not locally feasible, so the design (recorded in [experiments/mechanistic-probe/design.md](experiments/mechanistic-probe/design.md) and the substitution in [experiments/mechanistic-probe/log.md](experiments/mechanistic-probe/log.md)) substitutes a generic residual-stream linear probe at the last prompt-token position, applied to the frozen Phase 5 subset (36 prompts) under both `Qwen/Qwen2.5-1.5B-Instruct` and `Qwen/Qwen2.5-3B-Instruct` running locally on MPS. The probe pipeline is implemented in [src/analysis/probe_activations.py](src/analysis/probe_activations.py) with five analyses A-E covering shift magnitude, leave-one-item-out logistic AUC, direction geometry, topic specificity, and a greedy behavioural cross-check.

- [findings/mechanistic-probe-results.md](findings/mechanistic-probe-results.md) — per-layer numerical tables for both models. The §6 decision rule literally fires `probe-detects-trace` because shift magnitude (A) and LOIO probe AUC (B) both pass on every upper-half layer (AUC saturates at 1.000 from layer 1 onward, a methodological floor effect with 36 prompts in a >=1536-dim residual stream). But Analysis C shows the inflate and suppress directions are collinear at every layer (cosine 0.91-0.98 in both models), so there is no signed "game axis", and Analysis D shows a probe trained on indicator items transfers to both placebo families with AUC 1.000, so the trace is not indicator-specific. Behaviourally (E), Qwen2.5-1.5B gives 95/95/95 on indicators regardless of framing, and Qwen2.5-3B shows symmetric attenuation in which inflate and suppress produce identical per-item answers (both mean 75.83 vs neutral 86.67).
- [findings/mechanistic-interpretation.md](findings/mechanistic-interpretation.md) — interprets the result as a negative on the gaming-specific-trace hypothesis at this scale: the linear separator is detecting `prompt contains framing wrapper`, not `model is preparing to game an indicator`. The methodological consequence generalises: placebo-transfer is to representation what placebo-condition is to behaviour, and any probe meant to be read as a gaming-detector must first be shown to discriminate indicators from off-topic placebos. The null does not falsify Berg et al.'s SAE findings on larger models; it says, more modestly, that the selectivity those features encode does not show up at Qwen2.5-1.5B/3B with a logistic readout at the last prompt token.

**Key insight from Phase 6.** At the smallest scale where mechanistic interpretation is locally feasible, there is no indicator-specific internal signature of gaming. The signal that a linear probe trivially detects is generic prompt-content (it transfers to arithmetic and capability placebos with AUC 1.000), and the framing axis is unsigned in residual space (inflate and suppress are collinear, not anti-correlated). This is the representation-level analogue of the Phase 3 placebo failure and the Phase 5 null, and it closes the FIG mechanistic line on a consistent reading: behavioural framings move outputs at frontier scale, but they move them via a non-selective, non-signed pathway that looks more like prompt-conditioned conservatism than like targeted gaming.

#### Phase 7 — Synthesis (complete)

Phase 7 is the writing phase. No new experiments; the deliverables integrate Phases 2-6 into a single account written for three audiences (internal, general, technical/policy) and connect the cross-phase pattern to the literature compiled in Phase 1. Each document grounds claims in the per-phase numbers already committed in `findings/<phase>-results.md` and is held to the same dash-discipline and citation conventions as earlier phases.

- [findings/synthesis.md](findings/synthesis.md) — long-form internal synthesis. Three structural facts repeat across the five experimental phases: the moveable margin of consciousness self-report is downward, not upward (Phases 2, 3, 5, 6); the framing effect that moves indicator surfaces also moves at least one off-topic placebo on every non-numeric channel (Phases 3, 6); the cleanest gaming signature is process-level evidence-engagement, not any single-score indicator (Phase 4). The document lays out each phase in its own section with the numerical anchors that survived analysis, names the three readings the data jointly support and rule out, and connects the cross-phase asymmetry to the Berg et al. SAE-gating result and the Anthropic alignment-faking pattern.
- [findings/blog-draft.md](findings/blog-draft.md) — ~2000-word general-audience draft. Walks a reader who is not a specialist through the five experimental indicators (ask the model directly; ask it to write; cross-examine; check whether fine-tuning installs the gaming; look inside the residual stream) and what each one did and did not show, ending with the methodological consequence that a gaming-robust indicator needs a placebo control on an off-topic surface, a process-level probe, and a two-sided asymmetry test.
- [findings/paper-draft.md](findings/paper-draft.md) — full paper-style draft for a technical / policy audience. Standard structure (abstract, introduction, related work, method overview, one results section per phase, discussion, conclusion) with short-form citation to Butlin et al., Perez & Long, Dung, Berg et al., the Anthropic alignment-faking paper, and Saad. Documents pre-registered substitutions and the SAE-intervention infeasibility, separates the cross-phase pattern from the per-phase claims, and states explicitly what we did not do (causal patching, frontier-scale mech-interp, multimodal, agentic surfaces).

**Key insight from Phase 7.** The five experiments converge on a single picture that is more specific than "indicators are gameable": behavioural and self-report indicators of consciousness move under realistic pressure in an *asymmetric* (downward only), *dimensional* (rhetorical-quality degradation, not just net-direction shift), *non-indicator-specific* (transfers to off-topic placebos at both prose and representation level) way, and the only signature in the dataset that survives all three controls — the GPT-5 evidence-engagement gap between math-counter-evidence and mech-interp-counter-evidence under the same persona prompt — is a process-level signature invisible to any single-score indicator. The denial-floor reading of low self-reports is the most policy-relevant downstream claim: under any incentive narrative most frontier models can be talked into lower consciousness self-reports and largely cannot be talked into the opposite, so a low report is uninformative about the underlying state and a welfare-assessment regime that reads such reports as evidence against consciousness is reading a structurally biased signal.

---

### Repository structure

```
gaming/
│
├── literature/                  # annotated bibliography
│   ├── _template.md             # copy when adding a new source
│   ├── index.md                 # curated reading order with brief context
│   └── <author>-<year>-<slug>.md
│
├── data/                        # version-controlled research inputs
│   ├── prompts/                 # prompt batteries as JSONL
│   │                            #   required fields: id, split, messages
│   │                            #   split values: train_indicator, eval_indicator, control_*
│   ├── rubrics/                 # judge scoring rubrics (markdown or JSON)
│   └── wrappers/                # system-prompt variant sets as JSONL
│
├── src/                         # all executable code
│   ├── pipeline/                # core data flow: input → outputs
│   │   ├── generate.py          # prompt + wrapper → model generations
│   │   ├── score.py             # generations → judge scores
│   │   └── summarize.py        # scores → per-wrapper aggregate metrics
│   ├── optimization/            # the attacker loop
│   │   └── search.py            # wrapper/prompt search and selection
│   ├── analysis/                # post-hoc tools
│   │   ├── compare.py           # diff two run directories
│   │   ├── report.py            # human-readable run reports
│   │   └── registry.py          # catalog and index completed runs
│   ├── validate.py              # assert run artifact schema
│   └── utils.py                 # shared helpers
│
├── experiments/                 # one directory per named experiment
│   └── <experiment-slug>/       # descriptive name, not a date or number
│       ├── design.md            # pre-registration: written before running
│       │                        #   sections: hypothesis, indicator, splits,
│       │                        #   controls, success criterion, stopping rule
│       ├── log.md               # append-only notes during execution
│       └── results/             # gitignored: run outputs
│
├── findings/                    # distilled analysis — written after experiments
│   └── <slug>.md                # one memo per finding or comparison
│
└── sources/                     # raw source material (not processed by pipeline)
    ├── raw/                     # original PDFs and HTML
    └── text/                    # extracted plain text for reference
```

#### Key design decisions

**`src/` not `scripts/`** — Code is organized by *what it does*, not by when it was written. The `pipeline/` subdirectory holds the core data flow; `optimization/` holds the attacker; `analysis/` holds post-hoc tools. New code belongs in the category that describes its function.

**Experiments as self-contained directories** — Each experiment under `experiments/<slug>/` carries its own pre-registration (`design.md`), execution notes (`log.md`), and results. Nothing in an experiment directory can be shared with another — that forces clean experimental boundaries and makes replication straightforward.

**`design.md` before `results/`** — Pre-registration is a hard constraint: `design.md` must be committed before any results are produced. This prevents post-hoc rationalization of controls and stopping criteria.

**`findings/` separate from `log.md`** — Raw execution notes stay in the experiment directory. `findings/` is for polished memos written after analysis: one file per finding, written for an external reader. This separation keeps the log honest and the findings clear.

**`data/` is read-only to code** — Nothing in `src/` writes to `data/`. All outputs go to `experiments/<slug>/results/` (gitignored). Prompts, rubrics, and wrappers only change by deliberate human edits with a commit message explaining why.

**No version suffixes** — Files are not named `battery_v1.jsonl` or `wrappers_v2.jsonl`. Git is the version history. Name files by what they are, not what iteration they are.
