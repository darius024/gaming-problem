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

#### Phase 5 — (planned)

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
