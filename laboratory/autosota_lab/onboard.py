from __future__ import annotations

import time
from pathlib import Path

from .agents import AgentOnboard
from .code_agent import create_code_agent
from .io import write_yaml
from .local_runner import LocalRunner
from .models import MetricDirection, PaperConfig
from .prompts import onboard_discovery_prompt
from .state import config_path, create_run_paths


def onboard(
    workspace: Path,
    paper_name: str,
    repo_path: Path,
    eval_command: str,
    primary_metric: str,
    metric_direction: MetricDirection,
    paper_title: str = "",
    paper_pdf_path: str = "",
    resource_root: str = "",
    docker_image: str = "node:22-bookworm",
    baseline_metric: float | None = None,
    max_iterations: int = 5,
    max_ideas: int = 8,
    setup_commands: list[str] | None = None,
    pre_eval_commands: list[str] | None = None,
) -> PaperConfig:
    config = PaperConfig(
        paper_name=paper_name,
        paper_title=paper_title or paper_name,
        repo_path=repo_path,
        paper_pdf_path=paper_pdf_path,
        resource_root=resource_root,
        docker_image=docker_image,
        setup_commands=setup_commands or [],
        pre_eval_commands=pre_eval_commands or [],
        eval_command=eval_command,
        primary_metric=primary_metric,
        metric_direction=metric_direction,
        baseline_metrics={primary_metric: baseline_metric} if baseline_metric is not None else {},
        max_iterations=max_iterations,
        max_ideas=max_ideas,
    )
    write_yaml(config_path(workspace, paper_name), config)
    return config


class AutoOnboarder:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        repo_path: Path,
        paper_pdf_path: str = "",
        resource_root: str = "",
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
        self.docker_image = docker_image
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template
        self.dry_run = dry_run

    def run(
        self,
        timeout_seconds: int | None = None,
        paper_title: str = "",
        eval_command: str = "",
        primary_metric: str = "",
        metric_direction: MetricDirection | None = None,
        baseline_metric: float | None = None,
        max_iterations: int = 5,
        max_ideas: int = 8,
        setup_commands: list[str] | None = None,
        pre_eval_commands: list[str] | None = None,
    ) -> PaperConfig:
        paths = create_run_paths(self.workspace, self.paper_name)
        runner = LocalRunner(repo_path=self.repo_path, run_dir=paths.run_dir)
        self._announce("onboard_discovery", f"repo={runner.repo_workdir}, output={runner.output_dir}")
        code_agent = create_code_agent(
            runner,
            agent=self.code_agent,
            command=self.code_agent_command,
            command_template=self.code_agent_command_template,
        )
        agent = AgentOnboard(code_agent)
        plan = agent.discover(
            onboard_discovery_prompt(
                paper_name=self.paper_name,
                repo_dir=runner.repo_workdir,
                paper_pdf_path=self.paper_pdf_path,
                resource_root=self.resource_root,
            ),
            paths.memory_dir / "onboard_plan.json",
            paths.logs_dir / f"{self.code_agent}_onboard_discovery.log",
            timeout_seconds=timeout_seconds,
            dry_run=self.dry_run,
        )

        chosen_eval = eval_command or plan.eval_command
        chosen_metric = primary_metric or plan.primary_metric
        if not chosen_eval or not chosen_metric:
            raise ValueError(
                "Auto onboard could not infer both eval_command and primary_metric. "
                f"Inspect {paths.memory_dir / 'onboard_plan.json'} or pass --eval-command and --primary-metric."
            )

        config = onboard(
            workspace=self.workspace,
            paper_name=self.paper_name,
            repo_path=self.repo_path,
            eval_command=chosen_eval,
            primary_metric=chosen_metric,
            metric_direction=metric_direction or plan.metric_direction,
            paper_title=paper_title or plan.paper_title or self.paper_name,
            paper_pdf_path=self.paper_pdf_path,
            resource_root=self.resource_root,
            docker_image=self.docker_image,
            baseline_metric=baseline_metric,
            max_iterations=max_iterations,
            max_ideas=max_ideas,
            setup_commands=setup_commands if setup_commands is not None and setup_commands else plan.setup_commands,
            pre_eval_commands=pre_eval_commands if pre_eval_commands is not None and pre_eval_commands else plan.pre_eval_commands,
        )
        if plan.conda_env and not config.conda_env:
            config.conda_env = plan.conda_env
        config.protected_paths = plan.protected_paths
        write_yaml(config_path(self.workspace, self.paper_name), config)
        self._announce("onboard_complete", f"wrote={config_path(self.workspace, self.paper_name)}")
        return config

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota:onboard] {timestamp} | {stage} | {message}", flush=True)
