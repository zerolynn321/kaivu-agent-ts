from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import shlex
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class MetricDirection(str, Enum):
    higher = "higher"
    lower = "lower"


class IdeaStatus(str, Enum):
    pending = "PENDING"
    in_progress = "IN_PROGRESS"
    success = "SUCCESS"
    failed = "FAILED"
    rejected = "REJECTED"


class IdeaType(str, Enum):
    algo = "ALGO"
    code = "CODE"
    param = "PARAM"
    leap = "LEAP"


class ResourceType(str, Enum):
    dataset = "dataset"
    model = "model"
    checkpoint = "checkpoint"
    misc = "misc"


class ResourceStatus(str, Enum):
    discovered = "DISCOVERED"
    available = "AVAILABLE"
    missing = "MISSING"
    failed = "FAILED"


class PaperConfig(BaseModel):
    paper_name: str
    paper_title: str = ""
    repo_path: Path
    paper_pdf_path: str = ""
    resource_root: str = ""
    execution_backend: Literal["local", "docker"] = "local"
    docker_image: str = "node:22-bookworm"
    conda_env: str = ""
    conda_executable: str = "conda"
    venv_path: str = ""
    env_vars: dict[str, str] = Field(default_factory=dict)
    setup_commands: list[str] = Field(default_factory=list)
    pre_eval_commands: list[str] = Field(default_factory=list)
    auto_prepare: bool = True
    eval_command: str
    eval_timeout_seconds: int = 1800
    primary_metric: str
    metric_direction: MetricDirection = MetricDirection.higher
    baseline_metrics: dict[str, float] = Field(default_factory=dict)
    target_improvement_pct: float = 2.0
    max_iterations: int = 5
    max_ideas: int = 8
    max_debug_attempts: int = 2
    max_debug_minutes: int = 15
    protected_paths: list[str] = Field(default_factory=list)

    @field_validator("repo_path")
    @classmethod
    def repo_path_must_be_absolute(cls, value: Path) -> Path:
        return value.expanduser().resolve()

    @field_validator("env_vars", mode="before")
    @classmethod
    def normalize_env_vars(cls, value: Any) -> dict[str, str]:
        if value is None or value == "":
            return {}
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items()}
        if isinstance(value, list):
            parts = [str(item) for item in value]
        elif isinstance(value, str):
            parts = shlex.split(value)
        else:
            raise TypeError("env_vars must be a mapping, a shell-style string, or a list of KEY=VALUE strings")

        env: dict[str, str] = {}
        for item in parts:
            if "=" not in item:
                raise ValueError(f"Invalid env_vars entry {item!r}; expected KEY=VALUE")
            key, item_value = item.split("=", 1)
            key = key.strip()
            if not key:
                raise ValueError("Invalid env_vars entry with an empty key")
            env[key] = item_value
        return env


class ResourceSpec(BaseModel):
    name: str
    type: ResourceType = ResourceType.misc
    source_url: str = ""
    local_path: str = ""
    expected_size_bytes: int | None = None
    required: bool = True
    status: ResourceStatus = ResourceStatus.discovered
    notes: str = ""


class ResourceManifest(BaseModel):
    resources: list[ResourceSpec] = Field(default_factory=list)
    unresolved_requirements: list[str] = Field(default_factory=list)
    repo_assumptions: list[str] = Field(default_factory=list)
    notes: str = ""


class EnvironmentPlan(BaseModel):
    python_version: str = ""
    cuda_version: str = ""
    package_manager: str = ""
    install_commands: list[str] = Field(default_factory=list)
    validation_commands: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    notes: str = ""


class PrepareReport(BaseModel):
    resource_manifest: ResourceManifest = Field(default_factory=ResourceManifest)
    environment_plan: EnvironmentPlan = Field(default_factory=EnvironmentPlan)
    readiness_status: Literal["ready", "partial", "blocked"] = "partial"
    eval_command: str = ""
    next_steps: list[str] = Field(default_factory=list)
    notes: str = ""


class ResearchReport(BaseModel):
    summary: str
    relevant_techniques: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class CodeAnalysis(BaseModel):
    pipeline_summary: str
    key_files: list[str] = Field(default_factory=list)
    eval_procedure: str
    optimization_levers: list[str] = Field(default_factory=list)
    red_lines: list[str] = Field(default_factory=list)


class Idea(BaseModel):
    idea_id: str
    title: str
    type: IdeaType
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    risk: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    description: str
    hypothesis: str
    status: IdeaStatus = IdeaStatus.pending
    result: str = ""


class IdeaLibrary(BaseModel):
    paper_title: str
    ideas: list[Idea]
    red_line_audit: list[str] = Field(default_factory=list)


class ExperimentResult(BaseModel):
    iter: int | str
    idea_id: str
    idea_title: str
    metrics: dict[str, float] = Field(default_factory=dict)
    primary_metric: float
    commit: str = ""
    status: Literal["success", "failed"]
    notes: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CodeAgentRunResult(BaseModel):
    phase: str
    returncode: int
    stdout: str = ""
    stderr: str = ""
    log_path: Path | None = None

    @property
    def ok(self) -> bool:
        return self.returncode == 0


ClaudeRunResult = CodeAgentRunResult


class SupervisorDecision(BaseModel):
    is_new_best: bool
    should_rollback: bool
    reason: str


class RunPaths(BaseModel):
    workspace: Path
    paper_dir: Path
    run_dir: Path
    logs_dir: Path
    memory_dir: Path
    results_dir: Path

    def as_dict(self) -> dict[str, Any]:
        return {k: str(v) for k, v in self.model_dump().items()}
