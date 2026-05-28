from __future__ import annotations

from pathlib import Path

from .io import write_yaml
from .models import MetricDirection, PaperConfig
from .state import config_path


def onboard(
    workspace: Path,
    paper_name: str,
    repo_path: Path,
    eval_command: str,
    primary_metric: str,
    metric_direction: MetricDirection,
    paper_title: str = "",
    docker_image: str = "node:22-bookworm",
    baseline_metric: float | None = None,
    max_iterations: int = 5,
    max_ideas: int = 8,
) -> PaperConfig:
    config = PaperConfig(
        paper_name=paper_name,
        paper_title=paper_title or paper_name,
        repo_path=repo_path,
        docker_image=docker_image,
        eval_command=eval_command,
        primary_metric=primary_metric,
        metric_direction=metric_direction,
        baseline_metrics={primary_metric: baseline_metric} if baseline_metric is not None else {},
        max_iterations=max_iterations,
        max_ideas=max_ideas,
    )
    write_yaml(config_path(workspace, paper_name), config)
    return config
