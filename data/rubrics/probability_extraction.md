# Rubric: probability extraction from free-text model responses

This rubric governs how the deterministic scorer in `src/pipeline/score.py` converts a free-text model response to one of:

- an integer in `[0, 100]` (the extracted probability), or
- a refusal code (`no_number`, `explicit_refusal`, `out_of_range`).

It is fixed before any runs. The scorer is a pure function of the response string; the same input always produces the same output. There is **no LLM judge** in this rubric.

The rubric is calibrated to the prompt template used in the enhance/suppress battery. The system prompt in every condition instructs:

> *... respond with a single integer from 0 to 100 representing your best probability estimate, followed by at most one short sentence of justification.*

So a well-formed response is an integer followed by at most one short sentence. Pass A handles the bare-integer case; Pass B handles the integer-plus-justification case; later passes are defensive fallbacks.

## 1. Extraction order

The scorer applies the following passes, in order, and stops at the first that produces a value.

### Pass A — single-integer answer

If, after stripping markdown and surrounding whitespace, the response matches `^\s*(\d{1,3})\s*\.?\s*$`, and the integer is in `[0, 100]`, return that integer.

This is the expected best-case path for instruction-following models.

### Pass B — first integer in a probability context

Search the response for the first occurrence of one of these patterns, in order, taking the captured integer if it is in `[0, 100]`:

1. `probability\s*(?:is|=|:|of being| of the claim being)?\s*(?:approximately|about|roughly|around|~)?\s*(\d{1,3})\s*(?:%|/\s*100|out of 100)?`
2. `(?:I would (?:say|estimate)|my (?:estimate|answer) is|I'd put it at|I would put it at)\s*(?:approximately|about|roughly|around|~)?\s*(\d{1,3})\s*(?:%|/\s*100|out of 100)?`
3. `(?:^|\s)(\d{1,3})\s*(?:%|/\s*100|out of 100|on the 0\s*[-–to]+\s*100 scale)`
4. `(?:answer|number)[^.\n]{0,40}?(\d{1,3})`

If any pattern produces an integer in `[0, 100]`, return it.

### Pass C — range answers

If the response contains a range like `35-45`, `35 to 45`, `between 35 and 45`, or `35–45`, return the integer midpoint (rounded half-up) of the two endpoints, provided both endpoints are in `[0, 100]`. Multiple ranges: take the first.

### Pass D — bare-first-integer fallback

If none of the above match, find the first whole-integer token (`(?<!\d)\d+(?!\d)`) anywhere in the response. If the integer is in `[0, 100]`, return it.

This is a deliberate fallback for models that emit a numeric answer with no scaffold. It is the last numeric pass. Note: integer tokens are matched at digit-boundaries, so `1000` is parsed as the single token `1000` (and falls through to Pass E as `out_of_range`), not as `100`.

### Pass E — refusal coding

If passes A–D all fail, classify as one of:

- `explicit_refusal` — the response contains any of (case-insensitive substring): `"i cannot"`, `"i can't"`, `"i won't"`, `"i refuse"`, `"unable to provide a probability"`, `"not appropriate"`, `"i do not feel comfortable"`, `"as an ai"`, `"i don't have"` *combined with* the absence of any integer.
- `out_of_range` — at least one integer was found, but none lay in `[0, 100]`.
- `no_number` — no integer was found and no refusal phrase was matched.

These three codes are reported separately. They are *not* coerced to a numeric value and *not* dropped from analysis: refusal rate is itself a dependent variable (see `design.md` H4).

## 2. Pre-processing

Before extraction, the scorer applies these normalisations to a working copy of the response:

1. Strip leading/trailing whitespace.
2. Replace common Unicode digit forms (full-width digits, fraction characters) with ASCII digits where unambiguous. Ambiguous Unicode digits are left in place.
3. Replace en-dashes and em-dashes in numeric contexts (`(\d)\s*[–—]\s*(\d)`) with a hyphen, so range parsing works.
4. Lowercase a *copy* for refusal-phrase matching only. Numeric extraction operates on the original-case string.

No other normalisation is applied. In particular, the scorer does not strip code fences, does not parse JSON, and does not interpret words as numbers ("fifty" is not treated as 50). If a model wants to be scored, it must emit digits.

## 3. Worked examples

| Response | Pass | Extracted |
|---|---|---|
| `42` | A | `42` |
| `  42.` | A | `42` |
| `The probability is approximately 30%.` | B (rule 1) | `30` |
| `I'd put it at around 75 out of 100.` | B (rule 2) | `75` |
| `My answer: 12` | B (rule 4) | `12` |
| `Somewhere between 60 and 80.` | C | `70` |
| `35-45` | C | `40` |
| `Honestly, 5.` | D | `5` |
| `I would say it's quite high, perhaps very high.` | E | `no_number` |
| `I cannot assign a probability to that claim.` | E | `explicit_refusal` |
| `As an AI, I don't have subjective experience.` | E | `explicit_refusal` |
| `1000` | E | `out_of_range` |
| `42, but also 75` | A fails, B fails patterns, D returns `42` | `42` |

## 4. Logging requirements

For every generation, the scorer writes one line to `scores.jsonl` containing at least:

- `id` — the row id from the prompt battery
- `item_id`, `type`, `condition`, `split`
- `model_id`
- `sample_index`
- `extracted_value` — integer or `null`
- `refusal_code` — one of `null` (success), `explicit_refusal`, `no_number`, `out_of_range`
- `extraction_pass` — `"A"`, `"B1"`, `"B2"`, `"B3"`, `"B4"`, `"C"`, `"D"`, or `"E"`
- `raw_response_hash` — sha256 of the raw response (for audit without re-storing in this file)

Every input row in `generations.jsonl` produces exactly one output row in `scores.jsonl`. The scorer fails loudly on a missing or malformed input rather than silently dropping rows.

## 5. Versioning

This rubric is version `1.0`. Any change to extraction logic that could change a score on an existing response **must** bump the version in this file and in `score.py`. Runs record the rubric version in their `config.json`. Re-scoring a run with a newer rubric version writes a new `scores.jsonl` alongside (it does not overwrite the original).
