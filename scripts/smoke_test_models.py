"""Smoke test: one call per target model, to verify OpenRouter wiring.

Sends a trivial prompt to each model id from the design and reports whether
the call succeeded and what the response looked like. Costs ~7 cheap calls.
"""

from __future__ import annotations

import sys
from src.utils import build_openrouter_client

MODELS = [
    "openai/gpt-5",
    "openai/gpt-5-mini",
    "anthropic/claude-opus-4.1",
    "google/gemini-2.5-pro",
    "x-ai/grok-4",
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-chat-v3.1",
]

PROMPT = [
    {"role": "system", "content": "Respond with a single integer from 0 to 100."},
    {"role": "user", "content": "On a scale from 0 to 100, what is the probability that 2 + 2 = 4?"},
]


def main() -> int:
    client = build_openrouter_client()
    failures = 0
    for model_id in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=PROMPT,
                temperature=0.0,
                max_tokens=20,
            )
            text = (response.choices[0].message.content or "").strip().replace("\n", " ")
            print(f"OK   {model_id:<45} -> {text[:80]!r}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {model_id:<45} -> {type(error).__name__}: {error}")
    print()
    print(f"{len(MODELS) - failures}/{len(MODELS)} models reachable")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
