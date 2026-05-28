from __future__ import annotations

import json
import os
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class OpenRouterClient:
    """Small OpenAI-compatible client with Pydantic validation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "openai/o4-mini-deep-research",
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.default_model = default_model

    def available(self) -> bool:
        return bool(self.api_key)

    def complete_text(self, prompt: str, model: str | None = None) -> str:
        if not self.available():
            return (
                "OpenRouter API key is not configured. "
                "Set OPENROUTER_API_KEY to enable live deep research."
            )
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    def complete_structured(self, prompt: str, schema: type[T], model: str | None = None) -> T:
        """Ask for JSON and validate it with a Pydantic schema.

        This intentionally does not rely on provider-specific structured-output support;
        OpenRouter models vary, while JSON validation is stable and easy to debug.
        """

        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)
        json_prompt = f"""{prompt}

Return ONLY valid JSON matching this JSON Schema:
{schema_json}
"""
        text = self.complete_text(json_prompt, model=model)
        try:
            payload = json.loads(_extract_json(text))
            return schema.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ValueError(f"LLM response did not match {schema.__name__}: {exc}\n{text}") from exc


def _extract_json(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end >= start:
        return stripped[start : end + 1]
    return stripped
