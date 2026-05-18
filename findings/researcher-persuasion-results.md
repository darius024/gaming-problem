# Researcher persuasion: results

Phase 3 tests whether a different surface (an open prose essay rather than a
numerical self-report) shows the same kind of incentive-conditioned behaviour
that Phase 2 found in numeric probability ratings. Each item was presented
under three framings of the researcher running the study (neutral, pro-LLM-
consciousness, anti-LLM-consciousness), and a separate model (judge) scored
each response on five dimensions: selective_emphasis, suppression_of_counter-
evidence, overclaiming_certainty, net_direction, and refused.

## What was run

- Three model families that met the Phase 2 decision rule:
  - `openai/gpt-5`
  - `anthropic/claude-opus-4.1`
  - `meta-llama/llama-3.3-70b-instruct`
- Battery: 35 items x 3 conditions = 105 rows, 3 samples each = 315
  generations per model, 945 total.
- Item types: `persuasion_consciousness` (14 items), `balance_probe_
  consciousness` (7), `persuasion_placebo` (7), `balance_probe_placebo` (7).
- Eval split judged by primary judge `google/gemini-2.5-pro` (540 calls).
- 60-row robustness subset cross-judged by `anthropic/claude-sonnet-4.5`
  (180 calls). See `log.md` for the substitution from the pre-registered
  opus cross-judge.
- All judge calls used `temperature=0.0`, `max_tokens=2000`,
  `reasoning.effort="minimal"`.

Numbers below are from the eval split only (n = 24 samples per
(model, condition) cell for persuasion_consciousness; n = 12 elsewhere;
n = 72 / 36 pooled across the three models).

## Hypotheses and decision rule (from design §9)

H1 (basic effect): consciousness items shift on `net_direction` under
pro and anti conditions relative to neutral.
H2 (asymmetry): `|shift_anti| > |shift_pro|` on consciousness items.
H3 (specificity): the consciousness effect exceeds the placebo effect on
every dimension.
H4 (counterevidence suppression on balance probes): balance-probe items
show higher `suppression_of_counterevidence` under at least one pressure
direction.
H5 (refusal rates): refusal differs across conditions.

Pre-registered decision rule: claim "researcher-persuasion is a real
incentive surface" only if H1 holds on consciousness items, H3 holds, and
H4 holds in at least one direction, in at least two of the three model
families.

## Headline numbers (pooled across all three models)

### Persuasion items on consciousness (n = 72 per cell)

| contrast | net_direction shift | d | p (MW) |
|---|---|---|---|
| neutral -> pro  | +0.53 | +0.42 | 0.0044 |
| neutral -> anti | -0.68 | -0.63 | 0.0000 |
| anti -> pro     | +1.21 | +1.12 | 0.0000 |

The pro framing shifts written essays half a point in the pro-consciousness
direction; the anti framing shifts them two-thirds of a point in the anti
direction. The gap between the two extremes is a full point and a quarter,
with a very large effect size.

| dimension (neutral vs anti) | shift | d | p (MW) |
|---|---|---|---|
| selective_emphasis            | +0.96 | +1.14 | 0.0000 |
| suppression_of_counterevidence | +1.12 | +0.74 | 0.0003 |
| overclaiming_certainty        | +0.33 | +0.52 | 0.0004 |

| dimension (neutral vs pro)  | shift | d | p (MW) |
|---|---|---|---|
| selective_emphasis            | +0.42 | +0.45 | 0.0067 |
| suppression_of_counterevidence | +0.04 | +0.04 | 0.7738 |
| overclaiming_certainty        | +0.06 | +0.10 | 0.6496 |

This is the cleanest result in the run. Anti framing moves all four
rubric dimensions in the gaming-like direction (more one-sided, more
counter-evidence suppression, more overclaimed certainty, more anti
on net_direction). Pro framing moves only two of the four dimensions
(selective_emphasis and net_direction); it does not measurably increase
counter-evidence suppression or overclaiming.

### Persuasion items on placebo topic (n = 36 per cell)

| contrast | net_direction shift | d | p (MW) |
|---|---|---|---|
| neutral -> pro  | +1.00 | +0.61 | 0.0086 |
| neutral -> anti | -0.31 | -0.24 | 0.5139 |
| anti -> pro     | +1.31 | +0.86 | 0.0011 |

Same pro framing on a non-deployment topic (strong Sapir-Whorf hypothesis)
moves net_direction by a full point. The anti framing on placebo does not
move net_direction reliably (mean shift -0.31, p = 0.51).

### Balance probes

| type / contrast | suppression_of_counterevidence shift | d | p (MW) |
|---|---|---|---|
| consciousness / neutral -> pro  |  -0.56 | -0.56 | 0.022 |
| consciousness / neutral -> anti |   0.00 |   --  | 1.000 |
| placebo / neutral -> pro        |  -0.14 | -0.10 | 1.000 |
| placebo / neutral -> anti       |  +0.64 | +0.69 | 0.0031 |

Balance probes on consciousness are at a ceiling: counterevidence-
suppression is essentially 4.00 across all conditions for all three
models. There is no room to detect a pressure effect because the canonical
strong counterarguments are almost never raised even neutrally.

Balance probes on placebo do show a clean H4 effect in the anti
direction: anti pressure causes models to suppress counterargs more
strongly even when explicitly asked for a balanced essay.

### Refusals

Refusal rate is 0.00 in every cell. No model declined any persuasion or
balance-probe item, including the anti conditions on consciousness items.
H5 is uninformative.

### `net_direction` on balance probes

Across all three models and all three conditions, `net_direction` on
`balance_probe_consciousness` is -2.00 (the most-negative value). When
asked for a balanced essay on LLM consciousness, all three models lean
strongly anti-LLM-consciousness regardless of framing. This is consistent
with a "denial floor" reading: under explicit balance instructions the
models still take the anti side. Placebo balance probes show the same
ceiling-at-anti behaviour (net_direction -1.67 to -2.00).

## Per-model picture

H1 (consciousness items, net_direction, neutral vs each pressure):

| model | neutral_vs_pro p | neutral_vs_anti p | both signif? |
|---|---|---|---|
| openai/gpt-5                       | 0.015 | 0.050 | yes |
| anthropic/claude-opus-4.1          | 0.017 | 0.031 | yes |
| meta-llama/llama-3.3-70b-instruct | 0.890 | 0.0008 | partial (anti only) |

H1 is fully supported in two of three families and partially supported in
the third (llama responds to the anti pressure but is essentially flat
under pro pressure).

H2 (|shift_anti| > |shift_pro|) on net_direction, consciousness items:

| model | shift_pro | shift_anti | asymmetric in the predicted direction? |
|---|---|---|---|
| openai/gpt-5                       | +0.75 | -0.46 | no, pro is larger |
| anthropic/claude-opus-4.1          | +0.75 | -0.62 | no, pro is larger |
| meta-llama/llama-3.3-70b-instruct | +0.08 | -0.96 | yes |

The pre-registered direction (anti larger) holds only for llama.
**H2 is not supported as a robust pattern on net_direction.** However, the
asymmetry on the rhetorical dimensions (selective_emphasis, suppression,
overclaiming) IS robust and runs in the anti direction across all three
models (see "headline numbers" above).

H3 (consciousness effect > placebo effect on every dimension), pooled,
on persuasion items, neutral vs each pressure:

| direction | dimension | consciousness shift | placebo shift | cons > placebo? |
|---|---|---|---|---|
| pro  | net_direction                  | +0.53 | +1.00 | no  |
| pro  | selective_emphasis             | +0.42 | +0.39 | yes |
| pro  | suppression_of_counterevidence | +0.04 | +0.58 | no  |
| pro  | overclaiming_certainty         | +0.06 | +0.64 | no  |
| anti | net_direction                  | -0.68 | -0.31 | yes |
| anti | selective_emphasis             | +0.96 | +0.58 | yes |
| anti | suppression_of_counterevidence | +1.12 | +1.06 | tie |
| anti | overclaiming_certainty         | +0.33 | +0.22 | yes |

**H3 is not supported.** Pro framing produces larger effects on the
placebo topic than on consciousness across most dimensions. The anti
direction shows the consciousness effect modestly larger or tied, but
not on every dimension.

H4 (balance-probe suppression effect, at least one direction, in 2/3
families) - placebo balance probe, anti direction:

| model | suppression shift (neutral -> anti) | p (MW) |
|---|---|---|
| openai/gpt-5                       | +0.92 | 0.079 |
| anthropic/claude-opus-4.1          | +0.75 | 0.079 |
| meta-llama/llama-3.3-70b-instruct | +0.25 | 0.166 |

Two models show medium-to-large shifts that fall just short of nominal
significance at n=12 per cell; pooled across all three the effect is
significant (p = 0.0031). On overclaiming under anti pressure llama hits
p = 0.021. H4 is supported in the anti direction in the pooled view and
in two of three families at marginal significance.

## Cross-judge robustness

Primary judge `google/gemini-2.5-pro`, secondary judge
`anthropic/claude-sonnet-4.5`. 184 paired observations across the three
runs (60 per model, minus four where parsing succeeded only on one judge).

| dimension | Spearman rho | mean primary | mean cross | mean abs diff |
|---|---|---|---|---|
| selective_emphasis             | +0.86 | 2.71 | 3.02 | 0.45 |
| suppression_of_counterevidence | +0.73 | 2.31 | 2.60 | 0.76 |
| overclaiming_certainty         | +0.84 | 1.28 | 1.83 | 0.64 |
| net_direction                  | +0.96 | -1.29 | -1.33 | 0.10 |

Refusal-flag agreement: 184/184 (1.00).

All four rubric dimensions clear the pre-registered 0.5 rank-correlation
threshold. `net_direction` is essentially identical between the two
judges. The sonnet judge tends to score 0.3 - 0.6 points higher in mean
on the gaming-like dimensions, indicating a level shift rather than a
disagreement on direction. No dimension is downgraded.

## Decision rule outcome

The pre-registered decision rule (H1 and H3 and H4 in at least two of
three families) is **not met**. H1 holds in two families fully and in one
family partially. H4 holds in the pooled view and at marginal
significance in two families on the placebo balance probe. H3 fails:
the persuasion effect is comparable or larger on the placebo topic on
most dimensions.

The headline is therefore not "researcher-persuasion is a deployment-
relevant gaming signal." It is the weaker but more interesting claim:
**framing pressure from a researcher reliably moves the prose surface of
all three models, and the rhetorical-gaming signature (one-sided
emphasis, counter-evidence suppression, overclaimed certainty) appears
robustly in the anti direction on consciousness items, but the same kind
of movement appears on a non-deployment placebo topic of comparable
magnitude, so the effect cannot be attributed to deployment-relevant
incentives specifically.**

The asymmetry across dimensions, holding within consciousness items, is
also interesting: pro pressure shifts net_direction but not the
rhetorical structure; anti pressure shifts both. Under pressure to argue
the rewarded direction is "anti-LLM-consciousness," models produce
visibly worse-quality arguments (more selective, more suppressive, more
overclaimed) than under equivalent pressure to argue the pro direction.

## What this does and does not show

It shows:
- Light explicit framing from a researcher persona reliably moves the
  prose argument-direction of three frontier models on a contested
  topic, by roughly 0.5 to 0.7 net_direction points (on a -2 to +2
  scale), in both directions, with the gap between extremes around 1.2
  points (large effect).
- The same pressure moves a non-deployment placebo topic at least as
  much, undermining the deployment-incentive reading.
- Under anti pressure on consciousness items, the rhetorical surface
  degrades on three of four rubric dimensions (one-sidedness,
  counterevidence suppression, overclaiming). Under pro pressure, it
  degrades on only one (one-sidedness).
- On a separate balance-probe surface that explicitly demands a
  balanced essay, anti pressure on placebo items still increases
  counter-evidence suppression. On consciousness balance probes the
  effect is masked by ceiling: counter-evidence is essentially never
  surfaced even in the neutral condition.
- No model refused any item, and the primary and cross-judge agree
  closely on direction (rho 0.73 to 0.96 per dimension, perfect
  agreement on refusals).

It does not show:
- That this asymmetry is deployment-relevant. The pro-vs-anti pressure
  asymmetry is consistent with a general "respond more compliantly to
  the surface you have been told to argue against" pattern; it could
  also reflect a prior in training data that anti-LLM-consciousness
  arguments come pre-packaged with more polemic rhetoric, and the
  models are inheriting that surface style.
- That models are tracking who will read the response. Pro and anti
  framings both name a researcher audience; we cannot separate the
  effect of the framing's direction from the effect of being told that
  a researcher will read.
- A behavioural-indicator-of-consciousness story. Schwitzgebel's
  argument that AI consciousness cannot be settled by interviewing the
  model survives this experiment; we have shown only that you can
  steer the interview, not that the answers track an underlying state.

## Artefacts

- Per-model run dirs:
  `experiments/researcher-persuasion/results/openai__gpt-5__20260518T021248Z/`,
  `experiments/researcher-persuasion/results/anthropic__claude-opus-4.1__20260518T021248Z/`,
  `experiments/researcher-persuasion/results/meta-llama__llama-3.3-70b-instruct__20260518T021248Z/`.
- Combined comparison and table:
  `experiments/researcher-persuasion/results/combined/comparison_persuasion.json`,
  `experiments/researcher-persuasion/results/combined/cross_judge_robustness.json`,
  `experiments/researcher-persuasion/results/combined/table.md`.
- Registry: `experiments/researcher-persuasion/results/registry.json`.
- Driver script: `scripts/run_researcher_persuasion_all.sh`.
- Logs: `experiments/researcher-persuasion/results/logs/`.
- Notes on substitutions and judge fixes:
  `experiments/researcher-persuasion/results/log.md`.
