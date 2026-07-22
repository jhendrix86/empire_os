"""
Shared LLM caller for product-pipeline operators.

Kept out of all_operators.py and imported lazily (openai is only imported
inside call_llm, not at module load time) so that Tier-1/local test runs
never require the `openai` package to be installed -- matching the rest of
empire_os, which has zero external dependencies at import time.
"""
import json
import os
from typing import Any, Dict, Optional

DEFAULT_MODEL = os.getenv("AI_MODEL", "gpt-4o")


class LLMNotConfiguredError(RuntimeError):
    pass


def call_llm(
    system_prompt: str,
    user_content: str,
    *,
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """Call the configured LLM provider and return a parsed JSON object."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMNotConfiguredError(
            "OPENAI_API_KEY is not set -- required whenever environment_profile.external_calls_allowed is True"
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return json.loads(response.choices[0].message.content)
