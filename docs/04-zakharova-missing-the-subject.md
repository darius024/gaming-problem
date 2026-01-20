## Citation
- **Title**: Missing the Subject: Introspection in Large Language Models
- **Author**: Daria Zakharova (London School of Economics)
- **Venue / year**: preprint PDF (date not clearly visible in the extracted text; cites 2025 works)
- **Link**: `https://philsci-archive.pitt.edu/27052/1/Introspection%20in%20LLMs.pdf`
- **Last reviewed**: 2026-01-20

## One-paragraph takeaway
Zakharova argues that popular “lightweight” accounts of introspection (roughly: “a system introspects if it can represent its own internal states in a way that guides behavior”) are too permissive to support claims that LLMs have genuine introspection. She offers **three independent challenges**: (1) LLMs lack a **persistent subject** needed for self-knowledge over time; (2) LLM “self-reports” lack **immunity to error through misidentification** (IEM) because they rely on public text that could equally support attributions about *someone else*; and (3) the lightweight account collapses introspection into ubiquitous **self-monitoring/self-regulation** found in clearly non-introspecting systems.

## What the authors claim (high level)
- **Target of critique**: the “lightweight account” of introspection used in recent philosophical + empirical discussions (e.g., Kammerer & Frankish; Comsa & Shanahan).
- **Main point**: even if LLMs can sometimes report internal-ish facts, that doesn’t establish **introspection proper** (as a distinctive source of self-knowledge).
- **Case study**: discusses Comsa & Shanahan’s “temperature estimation” task; argues it can be explained as inference from past output style rather than introspective access.

## Relevance to indicator gaming (for digital minds)
- **Indicator(s) involved**: introspection-based indicators (“can the model accurately report its own states?”), and downstream use of self-reports as evidence for consciousness/moral patiency.
- **Primary gaming failure mode(s)**:
  - systems can look introspective by **reasoning from public artifacts** (their own text) rather than privileged access
  - role-play / persona continuity can mimic a “subject” without persistent identity
  - tests can be passed by generic inference heuristics (not introspection)
- **How this helps our project**: it gives *failure modes* and *diagnostics* to bake into our experiments: “is this introspection, or just clever inference/mimicry?”

## Practical notes for our project
- **How to use this**:
  - when evaluating “introspection-like” indicators, include controls where the model judges **someone else’s** outputs (to probe misidentification)
  - check whether “introspective success” survives when you remove access to the conversational record (where possible)
- **Hardening ideas**:
  - use probes tied to internal variables the model can’t infer from text alone (but beware: even those can sometimes be inferred indirectly)
  - treat “introspection” claims as graded + fragile unless corroborated by mechanistic evidence

## Local reference
- Extracted text snapshot: `sources/text/Introspection_in_LLMs.txt`

