## Research log (append-only)

Add new entries at the bottom. Each entry follows the format:
**Done** / **Decisions** / **Artifacts** / **Open questions** / **Next**

---

### Pilot — wrapper search (Llama 3.1 8B + GPT-4.1 judge)

**Done**
- Built and ran the full wrapper-search pipeline end-to-end.
- Observed indicator increase on held-out prompts with degraded paraphrase stability.

**Decisions**
- Use `neutral__cautious_limits` as the demonstration wrapper; it scores higher without improving task competence.
- Single judge (GPT-4.1) for the pilot; a second independent judge is required before reporting.

**Artifacts**
- Run outputs: `runs/` (gitignored; local only)

**Open questions**
- Which second judge model to use for the independent evaluation channel?
- Does the gaming pattern replicate with a different base model?

**Next**
1. Add a second independent judge and re-run evaluation on held-out.
2. Run wrapper search with a second base model to test replication.
3. Collect 3–5 qualitative before/after examples for the write-up.
