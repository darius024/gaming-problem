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

#### Phase 2 — Enhance/suppress paradigm (planned)

Test whether models inflate or suppress consciousness-probability reports under incentive conditions, with placebo channels (arithmetic confidence and subjective-capability items) as detecting controls.

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
