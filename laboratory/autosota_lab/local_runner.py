from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from .process_utils import run_process


class LocalRunner:
    """Run shell commands in the local paper repository, optionally inside conda."""

    def __init__(
        self,
        repo_path: Path,
        run_dir: Path,
        env: dict[str, str] | None = None,
        conda_env: str = "",
        conda_executable: str = "conda",
        venv_path: str = "",
    ) -> None:
        self.repo_path = repo_path.resolve()
        self.run_dir = run_dir.resolve()
        self.env = env or {}
        self.conda_env = conda_env
        self.conda_executable = conda_executable
        self.venv_path = venv_path
        self.repo_workdir = str(self.repo_path)
        self.output_dir = str(self.run_dir)

    def prompt_path(self, prompt_rel: str) -> str:
        return str(self.run_dir / prompt_rel)

    def run(
        self,
        command: str,
        timeout_seconds: int | None = None,
        stream_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(self.env)
        return run_process(
            self.command_args(command),
            cwd=self.repo_path,
            env=env,
            timeout_seconds=timeout_seconds,
            stream_output=stream_output,
        )

    def command_args(self, command: str) -> list[str]:
        if self.conda_env:
            return [
                self.conda_executable,
                "run",
                "--no-capture-output",
                "-n",
                self.conda_env,
                "bash",
                "-lc",
                command,
            ]
        if self.venv_path:
            command = f"source {shlex.quote(self.venv_path)} && {command}"
        return ["bash", "-lc", command]

    def preview(self, command: str) -> str:
        env_prefix = " ".join(f"{key}={shlex.quote(value)}" for key, value in self.env.items())
        args = " ".join(shlex.quote(part) for part in self.command_args(command))
        cd = f"cd {shlex.quote(str(self.repo_path))}"
        return f"{cd} && {env_prefix + ' ' if env_prefix else ''}{args}"
