from __future__ import annotations

import shutil
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
        repo_copy_root: Path | None = None,
        refresh_repo_copy: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.source_repo_path = repo_path.expanduser().resolve()
        self.repo_copy_root = repo_copy_root.expanduser().resolve() if repo_copy_root else None
        self.refresh_repo_copy = refresh_repo_copy
        self.dry_run = dry_run
        self.repo_path = self._prepare_repo_path()
        self.paper_pdf_path = paper_pdf_path
        self.resource_root = resource_root
        self.execution_backend = execution_backend
        self.docker_image = docker_image
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template

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
        conda_env: str | None = None,
        max_iterations: int = 5,
        max_ideas: int = 8,
        setup_commands: list[str] | None = None,
        pre_eval_commands: list[str] | None = None,
        auto_fix: bool = True,
        fix_plan_only: bool = False,
        allow_risky_fix: bool = False,
        max_fix_attempts: int = 2,
        skip_setup: bool = False,
        skip_validation: bool = False,
        skip_baseline: bool = False,
        skip_resource_acquisition: bool = False,
        refresh_resources: bool = False,
        use_acquired_resources: bool = False,
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
        if conda_env is not None:
            config.conda_env = conda_env
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
            refresh_resources=refresh_resources,
            use_acquired_resources=use_acquired_resources,
            auto_fix=auto_fix,
            fix_plan_only=fix_plan_only,
            allow_risky_fix=allow_risky_fix,
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

    def _prepare_repo_path(self) -> Path:
        if self.repo_copy_root is None:
            return self.source_repo_path
        if not self.source_repo_path.exists():
            raise FileNotFoundError(f"source repo does not exist: {self.source_repo_path}")
        copy_root = self.repo_copy_root
        copy_root.mkdir(parents=True, exist_ok=True)
        destination = (copy_root / self.source_repo_path.name).resolve()
        try:
            destination.relative_to(copy_root.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to copy repo outside copy root: {destination}") from exc
        if destination == self.source_repo_path:
            raise ValueError("repo copy destination must be different from source repo")
        if destination.exists() and self.refresh_repo_copy:
            self._remove_repo_copy(destination, copy_root)
        if not destination.exists():
            self._announce("repo_copy", f"Copying {self.source_repo_path} -> {destination}")
            if not self.dry_run:
                shutil.copytree(
                    self.source_repo_path,
                    destination,
                    symlinks=True,
                    ignore=shutil.ignore_patterns(
                        ".autosota_resource_backups",
                        "__pycache__",
                        ".pytest_cache",
                    ),
                )
        else:
            self._announce("repo_copy", f"Using existing repo copy: {destination}")
        return destination

    def _remove_repo_copy(self, destination: Path, copy_root: Path) -> None:
        try:
            destination.resolve().relative_to(copy_root.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to remove repo copy outside copy root: {destination}") from exc
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
