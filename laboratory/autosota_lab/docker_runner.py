from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from .process_utils import run_process


class DockerRunner:
    """Run shell commands inside an isolated Docker container."""

    def __init__(
        self,
        image: str,
        repo_path: Path,
        run_dir: Path,
        env: dict[str, str] | None = None,
        workdir: str = "/workspace/repo",
    ) -> None:
        self.image = image
        self.repo_path = repo_path.resolve()
        self.run_dir = run_dir.resolve()
        self.env = env or {}
        self.workdir = workdir
        self.repo_workdir = workdir
        self.output_dir = "/autosota_run"

    def prompt_path(self, prompt_rel: str) -> str:
        return f"{self.output_dir}/{prompt_rel}"

    def docker_command(self, command: str) -> list[str]:
        args = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{self.repo_path}:/workspace/repo",
            "-v",
            f"{self.run_dir}:/autosota_run",
            "-w",
            self.workdir,
        ]
        for key, value in self.env.items():
            args.extend(["-e", f"{key}={value}"])
        for key in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"):
            if os.environ.get(key) and key not in self.env:
                args.extend(["-e", key])
        args.extend([self.image, "bash", "-lc", command])
        return args

    def run(
        self,
        command: str,
        timeout_seconds: int | None = None,
        stream_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return run_process(
            self.docker_command(command),
            timeout_seconds=timeout_seconds,
            stream_output=stream_output,
        )

    def preview(self, command: str) -> str:
        return " ".join(shlex.quote(part) for part in self.docker_command(command))
