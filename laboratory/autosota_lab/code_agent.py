from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from .io import write_text
from .models import CodeAgentRunResult

T = TypeVar("T", bound=BaseModel)


class CodeAgentRunner:
    """Execute a code agent CLI with a shared prompt/result interface."""

    DEFAULT_COMMANDS = {
        "claude": "claude",
        "codex": "codex",
    }
    DEFAULT_TEMPLATES = {
        "claude": "{command} -p {output_schema_arg} < {prompt}",
        "codex": "{command} exec --dangerously-bypass-approvals-and-sandbox {output_schema_arg} < {prompt}",
    }

    def __init__(
        self,
        runner,
        agent: str = "claude",
        command: str | None = None,
        command_template: str | None = None,
    ) -> None:
        if agent not in self.DEFAULT_COMMANDS:
            raise ValueError(f"Unsupported code agent: {agent}")
        self.runner = runner
        self.agent = agent
        self.command = command or self.DEFAULT_COMMANDS[agent]
        self.command_template = command_template or self.DEFAULT_TEMPLATES[agent]

    def run_prompt(
        self,
        phase: str,
        prompt: str,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
        output_schema: type[BaseModel] | None = None,
    ) -> CodeAgentRunResult:
        prompt_rel = f"logs/{phase}_prompt.md"
        prompt_path = self.runner.run_dir / prompt_rel
        write_text(prompt_path, prompt)

        quoted_prompt = shlex.quote(self.runner.prompt_path(prompt_rel))
        output_schema_arg = self._output_schema_arg(phase, output_schema)
        command = self.command_template.format(
            command=self.command,
            prompt=quoted_prompt,
            output_dir=shlex.quote(self.runner.output_dir),
            repo_workdir=shlex.quote(self.runner.repo_workdir),
            output_schema_arg=output_schema_arg,
        )
        preview = self.runner.preview(command)
        print(f"\n[code-agent:{self.agent}] stage={phase}", flush=True)
        print(f"[code-agent:{self.agent}] command: {preview}", flush=True)
        print(f"[code-agent:{self.agent}] log: {log_path}", flush=True)
        if dry_run:
            write_text(log_path, preview + "\n")
            return CodeAgentRunResult(phase=phase, returncode=0, stdout=preview, log_path=log_path)

        proc = self.runner.run(command, timeout_seconds=timeout_seconds, stream_output=True)
        stderr_text = "\nSTDERR:\n" + proc.stderr if proc.stderr else ""
        log_text = f"$ {preview}\n\nSTDOUT:\n{proc.stdout}{stderr_text}"
        write_text(log_path, log_text)
        print(f"[code-agent:{self.agent}] stage={phase} exit={proc.returncode}", flush=True)
        return CodeAgentRunResult(
            phase=phase,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            log_path=log_path,
        )

    def complete_structured(
        self,
        phase: str,
        prompt: str,
        schema: type[T],
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> T:
        schema_json = _strict_json_schema(schema)
        structured_prompt = f"""
{prompt}

Return only valid JSON matching this JSON schema. Do not wrap the JSON in
Markdown fences and do not include explanatory text.

JSON schema:
{json.dumps(schema_json, indent=2)}
"""
        result = self.run_prompt(
            phase=phase,
            prompt=structured_prompt,
            log_path=log_path,
            timeout_seconds=timeout_seconds,
            dry_run=dry_run,
            output_schema=schema,
        )
        if not result.ok:
            detail = (result.stderr or result.stdout)[-2000:].strip()
            suffix = f": {detail}" if detail else ""
            raise RuntimeError(f"{self.agent} returned non-zero exit code {result.returncode}{suffix}")
        payload = _extract_json(result.stdout)
        try:
            return schema.model_validate(payload)
        except ValidationError:
            if isinstance(payload, str):
                return schema.model_validate_json(payload)
            raise

    def _output_schema_arg(self, phase: str, schema: type[BaseModel] | None) -> str:
        if schema is None:
            return ""

        schema_dict = _strict_json_schema(schema)
        schema_json = json.dumps(schema_dict, separators=(",", ":"))
        if self.agent == "claude":
            return "--json-schema " + shlex.quote(schema_json)
        if self.agent == "codex":
            schema_rel = f"logs/{phase}_schema.json"
            write_text(self.runner.run_dir / schema_rel, json.dumps(schema_dict, indent=2))
            return "--output-schema " + shlex.quote(self.runner.prompt_path(schema_rel))
        return ""


def create_code_agent(
    runner,
    agent: str = "claude",
    command: str | None = None,
    command_template: str | None = None,
) -> CodeAgentRunner:
    return CodeAgentRunner(
        runner=runner,
        agent=agent,
        command=command,
        command_template=command_template,
    )


def _extract_json(text: str) -> object:
    stripped = text.strip()
    if not stripped:
        raise ValueError("Code agent returned empty output.")
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    start = min((pos for pos in (stripped.find("{"), stripped.find("[")) if pos >= 0), default=-1)
    if start < 0:
        raise ValueError("Code agent output did not contain JSON.")

    decoder = json.JSONDecoder()
    payload, _ = decoder.raw_decode(stripped[start:])
    return payload


def _strict_json_schema(schema: type[BaseModel]) -> dict[str, object]:
    schema_dict = schema.model_json_schema()

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" or "properties" in node:
                node["additionalProperties"] = False
                properties = node.get("properties")
                if isinstance(properties, dict):
                    node["required"] = list(properties.keys())
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(schema_dict)
    return schema_dict
