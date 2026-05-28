from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .io import write_text
from .llm import OpenRouterClient

T = TypeVar("T", bound=BaseModel)


class DeepResearchRunner:
    """Run deep-research style calls independently from the code agent."""

    def __init__(
        self,
        model: str = "openai/o4-mini-deep-research",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.client = OpenRouterClient(api_key=api_key, base_url=base_url, default_model=model)
        self.model = model

    def available(self) -> bool:
        return self.client.available()

    def complete_structured(
        self,
        prompt: str,
        schema: type[T],
        log_path: Path,
        dry_run: bool = False,
    ) -> T:
        if dry_run:
            preview = f"[dry-run] Deep research model: {self.model}\n\n{prompt}"
            write_text(log_path, preview)
            raise RuntimeError("Deep research skipped in dry-run mode.")
        if not self.available():
            write_text(log_path, "OPENROUTER_API_KEY is not configured.\n")
            raise RuntimeError("OPENROUTER_API_KEY is not configured.")

        write_text(log_path, f"[deep-research] model: {self.model}\n\n{prompt}\n")
        result = self.client.complete_structured(prompt, schema, model=self.model)
        write_text(log_path, result.model_dump_json(indent=2))
        return result
