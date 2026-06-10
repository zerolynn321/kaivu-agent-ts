from __future__ import annotations

import time
from pathlib import Path

from .models import MetricDirection, PaperConfig
from .onboard import AutoOnboarder
from .prepare import Preparer


class ZerolinePipeline:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        repo_path: Path,
        paper_pdf_path: str = "",
        resource_root: str = "",
        execution_backend: str | None = None,
        docker_image: str = "node:22-bookworm",
        code_agent: str = "codex",
        code_agent_command: str | None = None,
        code_agent_command_template: str | None = None,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.repo_path = repo_path.expanduser().resolve()
        self.paper_pdf_path = paper_pdf_path
        self.resource_root = resource_root
        self.execution_backend = execution_backend
        self.docker_image = docker_image
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template
        self.dry_run = dry_run

    def run(
        self,
        timeout_seconds: int | None = None,
        setup_timeout_seconds: int | None = None,
        fix_timeout_seconds: int | None = None,
        baseline_timeout_seconds: int | None = None,
        paper_title: str = "",
        eval_command: str = "",
        primary_metric: str = "",
        metric_direction: MetricDirection | None = None,
        baseline_metric: float | None = None,
        max_iterations: int = 5,
        max_ideas: int = 8,
        setup_commands: list[str] | None = None,
        pre_eval_commands: list[str] | None = None,
        auto_fix: bool = True,
        max_fix_attempts: int = 2,
        skip_setup: bool = False,
        skip_validation: bool = False,
        skip_baseline: bool = False,
        skip_resource_acquisition: bool = False,
    ) -> Path:
        self._announce("onboard", "Inferring paper config with the Code Agent.")
        config = AutoOnboarder(
            workspace=self.workspace,
            paper_name=self.paper_name,
            repo_path=self.repo_path,
            paper_pdf_path=self.paper_pdf_path,
            resource_root=self.resource_root,
            docker_image=self.docker_image,
            code_agent=self.code_agent,
            code_agent_command=self.code_agent_command,
            code_agent_command_template=self.code_agent_command_template,
            dry_run=self.dry_run,
        ).run(
            timeout_seconds=timeout_seconds,
            paper_title=paper_title,
            eval_command=eval_command,
            primary_metric=primary_metric,
            metric_direction=metric_direction,
            baseline_metric=baseline_metric,
            max_iterations=max_iterations,
            max_ideas=max_ideas,
            setup_commands=setup_commands,
            pre_eval_commands=pre_eval_commands,
        )
        self._announce("onboard", f"Config ready: eval_command={config.eval_command!r}, metric={config.primary_metric}.")

        self._announce("prepare", "Discovering/acquiring resources, preparing environment, and running zeroline baseline.")
        run_dir = Preparer(
            workspace=self.workspace,
            paper_name=self.paper_name,
            repo_path=self.repo_path,
            execution_backend=self.execution_backend,
            docker_image=self.docker_image,
            conda_env=config.conda_env,
            paper_pdf_path=self.paper_pdf_path,
            resource_root=self.resource_root,
            code_agent=self.code_agent,
            code_agent_command=self.code_agent_command,
            code_agent_command_template=self.code_agent_command_template,
            execute_setup=not skip_setup,
            execute_validation=not skip_validation,
            execute_baseline=not skip_baseline,
            acquire_resources=not skip_resource_acquisition,
            auto_fix=auto_fix,
            max_fix_attempts=max_fix_attempts,
            dry_run=self.dry_run,
        ).run(
            timeout_seconds=timeout_seconds,
            setup_timeout_seconds=setup_timeout_seconds,
            fix_timeout_seconds=fix_timeout_seconds,
            baseline_timeout_seconds=baseline_timeout_seconds,
        )
        self._announce("complete", f"run_dir={run_dir}")
        return run_dir

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota:zeroline] {timestamp} | {stage} | {message}", flush=True)
