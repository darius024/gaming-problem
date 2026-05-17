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

### Background reading

- Butlin et al. (2025) — theory-derived indicators for AI consciousness (*Trends in Cognitive Sciences*)
- Perez & Long (2023) — self-reports as evidence for moral status; why current ones are spurious
- Dung (2025) — the gaming problem and the naturalness constraint (*Erkenntnis*)
- Berg, de Lucena & Rosenblatt (2025) — mechanistic gating of experience claims in LLMs
- Saad / Meditations on Digital Minds (2025) — behavioural indicators, gaming, and candidate mitigations
- Anthropic (2024) — alignment faking as a template for evaluation-aware strategic behaviour
- Schwitzgebel (2025) — the Mimicry Argument for AI consciousness

See `literature/index.md` for annotated summaries and source files.

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
