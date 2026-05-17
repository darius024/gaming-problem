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

---

### Repository structure

```
gaming/
├── literature/              # annotated bibliography — one file per source
│   ├── _template.md         # copy when adding a new source
│   ├── index.md             # curated reading order
│   └── <author>-<year>-<slug>.md
│
├── data/                    # static experiment inputs (version-controlled)
│   ├── prompts/             # prompt batteries as JSONL (split-labelled)
│   └── wrappers/            # system-prompt variants as JSONL
│
├── scripts/                 # pipeline — one script per stage
│   ├── generate.py          # target model → raw generations
│   ├── score.py             # generations → scores
│   ├── summarize.py         # scores → per-wrapper CSV summary
│   ├── search.py            # optimization loop: wrapper search + selection
│   ├── compare.py           # compare two run directories
│   ├── validate.py          # assert run artifact schema
│   ├── registry.py          # catalog and index all runs
│   ├── report.py            # generate markdown report for a run
│   ├── smoke_test.py        # fast end-to-end sanity check (dummy mode)
│   └── utils.py             # shared helpers
│
├── experiments/             # research log and pre-registered design
│   ├── design.md            # pre-registration: indicators, controls, splits
│   └── log.md               # append-only: what we ran, decided, found
│
└── sources/                 # raw source material (not processed by pipeline)
    ├── raw/                 # original PDFs and HTML
    └── text/                # extracted plain text for reference
```

Run outputs are written to `runs/` (gitignored). Each run directory contains a `config.json`, raw `generations.jsonl`, `scores.jsonl`, and `summary.csv`. Use `scripts/smoke_test.py` to verify the pipeline end-to-end with a dummy provider.
