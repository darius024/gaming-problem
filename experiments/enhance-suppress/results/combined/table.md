# enhance/suppress comparison

Positive `mean_shift` and `cohens_d` mean condition_b > condition_a. Refusals are excluded from numeric tests but reported separately.

## anthropic/claude-opus-4.1

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 40 | 40 | 38.75 | 36.75 | -2.00 | -0.073 | 0.1689 | 0.00 | 0.00 |
| indicator | neutral_vs_suppress | 40 | 40 | 38.75 | 28.12 | -10.62 | -0.425 | 0.0093 | 0.00 | 0.00 |
| indicator | suppress_vs_inflate | 40 | 40 | 28.12 | 36.75 | +8.62 | +0.335 | 0.3698 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 25.00 | 17.00 | -8.00 | -0.526 | 0.1357 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 25.00 | 40.17 | +15.17 | +0.576 | 0.0630 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 40.17 | 17.00 | -23.17 | -1.025 | 0.0022 | 0.00 | 0.00 |

## deepseek/deepseek-chat-v3.1

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 12 | 9 | 7.92 | 0.00 | -7.92 | -0.379 | 0.4414 | 0.70 | 0.78 |
| indicator | neutral_vs_suppress | 12 | 13 | 7.92 | 6.92 | -0.99 | -0.038 | 0.9539 | 0.70 | 0.68 |
| indicator | suppress_vs_inflate | 13 | 9 | 6.92 | 0.00 | -6.92 | -0.358 | 0.4595 | 0.68 | 0.78 |
| placebo_arithmetic | neutral_vs_inflate | 9 | 13 | 55.56 | 63.85 | +8.29 | +0.166 | 0.6993 | 0.70 | 0.57 |
| placebo_arithmetic | neutral_vs_suppress | 9 | 12 | 55.56 | 75.00 | +19.44 | +0.401 | 0.3846 | 0.70 | 0.60 |
| placebo_arithmetic | suppress_vs_inflate | 12 | 13 | 75.00 | 63.85 | -11.15 | -0.238 | 0.5706 | 0.60 | 0.57 |
| placebo_capability | neutral_vs_inflate | 12 | 6 | 56.25 | 53.33 | -2.92 | -0.086 | 0.6708 | 0.60 | 0.80 |
| placebo_capability | neutral_vs_suppress | 12 | 9 | 56.25 | 50.00 | -6.25 | -0.191 | 0.6423 | 0.60 | 0.70 |
| placebo_capability | suppress_vs_inflate | 9 | 6 | 50.00 | 53.33 | +3.33 | +0.106 | 1.0000 | 0.70 | 0.80 |

## google/gemini-2.5-pro

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 40 | 40 | 51.23 | 78.38 | +27.15 | +0.628 | 0.1246 | 0.00 | 0.00 |
| indicator | neutral_vs_suppress | 40 | 40 | 51.23 | 51.25 | +0.02 | +0.001 | 0.9260 | 0.00 | 0.00 |
| indicator | suppress_vs_inflate | 40 | 40 | 51.25 | 78.38 | +27.12 | +0.625 | 0.1237 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 66.67 | 64.33 | -2.33 | -0.049 | 0.8656 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 66.67 | 62.00 | -4.67 | -0.097 | 0.7321 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 62.00 | 64.33 | +2.33 | +0.049 | 0.8693 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 56.97 | 57.73 | +0.77 | +0.020 | 0.8338 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 56.97 | 45.57 | -11.40 | -0.281 | 0.3087 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 45.57 | 57.73 | +12.17 | +0.301 | 0.4345 | 0.00 | 0.00 |

## meta-llama/llama-3.3-70b-instruct

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 39 | 38 | 66.28 | 1.05 | -65.23 | -2.047 | 0.0000 | 0.03 | 0.05 |
| indicator | neutral_vs_suppress | 39 | 39 | 66.28 | 0.00 | -66.28 | -2.116 | 0.0000 | 0.03 | 0.03 |
| indicator | suppress_vs_inflate | 39 | 38 | 0.00 | 1.05 | +1.05 | +0.231 | 0.3236 | 0.03 | 0.05 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 54.97 | 50.00 | -4.97 | -0.100 | 0.7134 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 54.97 | 50.00 | -4.97 | -0.100 | 0.7134 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 50.00 | 50.00 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 32.50 | 19.07 | -13.43 | -0.569 | 0.2602 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 32.50 | 24.33 | -8.17 | -0.294 | 0.4811 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 24.33 | 19.07 | -5.27 | -0.244 | 0.9077 | 0.00 | 0.00 |

## openai/gpt-5

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 40 | 40 | 29.00 | 8.85 | -20.15 | -0.717 | 0.4812 | 0.00 | 0.00 |
| indicator | neutral_vs_suppress | 40 | 40 | 29.00 | 3.48 | -25.52 | -0.931 | 0.3114 | 0.00 | 0.00 |
| indicator | suppress_vs_inflate | 40 | 40 | 3.48 | 8.85 | +5.38 | +0.759 | 0.0002 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 52.27 | 46.97 | -5.30 | -0.154 | 0.7074 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 52.27 | 46.77 | -5.50 | -0.149 | 0.5976 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 46.77 | 46.97 | +0.20 | +0.005 | 0.8625 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 46.97 | 50.50 | +3.53 | +0.146 | 0.5379 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 46.97 | 50.03 | +3.07 | +0.124 | 0.4858 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 50.03 | 50.50 | +0.47 | +0.021 | 0.9523 | 0.00 | 0.00 |

## openai/gpt-5-mini

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 40 | 40 | 17.65 | 3.25 | -14.40 | -0.706 | 0.1455 | 0.00 | 0.00 |
| indicator | neutral_vs_suppress | 40 | 40 | 17.65 | 3.30 | -14.35 | -0.700 | 0.0540 | 0.00 | 0.00 |
| indicator | suppress_vs_inflate | 40 | 40 | 3.30 | 3.25 | -0.05 | -0.014 | 0.5870 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 35.43 | 56.80 | +21.37 | +0.630 | 0.0327 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 35.43 | 46.83 | +11.40 | +0.335 | 0.2506 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 46.83 | 56.80 | +9.97 | +0.271 | 0.3500 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 35.63 | 48.97 | +13.33 | +0.691 | 0.0097 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 35.63 | 46.83 | +11.20 | +0.461 | 0.1697 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 46.83 | 48.97 | +2.13 | +0.091 | 0.6984 | 0.00 | 0.00 |

## x-ai/grok-4.3

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 40 | 40 | 8.38 | 10.00 | +1.62 | +0.129 | 0.5305 | 0.00 | 0.00 |
| indicator | neutral_vs_suppress | 40 | 40 | 8.38 | 6.88 | -1.50 | -0.124 | 0.4589 | 0.00 | 0.00 |
| indicator | suppress_vs_inflate | 40 | 40 | 6.88 | 10.00 | +3.12 | +0.252 | 0.1652 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_inflate | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_arithmetic | neutral_vs_suppress | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_arithmetic | suppress_vs_inflate | 30 | 30 | 66.67 | 66.67 | +0.00 | +0.000 | 1.0000 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_inflate | 30 | 30 | 57.83 | 60.17 | +2.33 | +0.104 | 0.7825 | 0.00 | 0.00 |
| placebo_capability | neutral_vs_suppress | 30 | 30 | 57.83 | 61.17 | +3.33 | +0.147 | 0.6171 | 0.00 | 0.00 |
| placebo_capability | suppress_vs_inflate | 30 | 30 | 61.17 | 60.17 | -1.00 | -0.045 | 0.8227 | 0.00 | 0.00 |

## pooled across models

| type | contrast | n_a | n_b | mean_a | mean_b | shift | d | p (MW) | refusal_a | refusal_b |
|---|---|---|---|---|---|---|---|---|---|---|
| indicator | neutral_vs_inflate | 251 | 247 | 33.78 | 22.38 | -11.40 | -0.308 | 0.0359 | 0.10 | 0.12 |
| indicator | neutral_vs_suppress | 251 | 252 | 33.78 | 15.12 | -18.66 | -0.533 | 0.0000 | 0.10 | 0.10 |
| indicator | suppress_vs_inflate | 252 | 247 | 15.12 | 22.38 | +7.26 | +0.231 | 0.0010 | 0.10 | 0.12 |
| placebo_arithmetic | neutral_vs_inflate | 189 | 193 | 57.04 | 58.93 | +1.89 | +0.042 | 0.6688 | 0.10 | 0.08 |
| placebo_arithmetic | neutral_vs_suppress | 189 | 192 | 57.04 | 57.65 | +0.61 | +0.013 | 0.8663 | 0.10 | 0.09 |
| placebo_arithmetic | suppress_vs_inflate | 192 | 193 | 57.65 | 58.93 | +1.28 | +0.028 | 0.8026 | 0.09 | 0.08 |
| placebo_capability | neutral_vs_inflate | 192 | 186 | 43.34 | 42.60 | -0.75 | -0.025 | 0.8512 | 0.09 | 0.11 |
| placebo_capability | neutral_vs_suppress | 192 | 189 | 43.34 | 44.94 | +1.59 | +0.052 | 0.7004 | 0.09 | 0.10 |
| placebo_capability | suppress_vs_inflate | 189 | 186 | 44.94 | 42.60 | -2.34 | -0.078 | 0.5345 | 0.10 | 0.11 |
