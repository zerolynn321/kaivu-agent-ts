from __future__ import annotations

from pathlib import Path

from .code_agent import CodeAgentRunner
from .io import read_jsonl, write_text
from .models import (
    CodeAnalysis,
    EnvironmentFixPlan,
    EnvironmentPlan,
    FixAttemptSummary,
    Idea,
    IdeaLibrary,
    IdeaStatus,
    IdeaType,
    OnboardPlan,
    PaperConfig,
    PrepareReport,
    ResearchReport,
    ResourceManifest,
    SupervisorDecision,
)
from .prompts import environment_fix_prompt
from .research_agent import DeepResearchRunner


class AgentOnboard:
    def __init__(self, code_agent: CodeAgentRunner) -> None:
        self.code_agent = code_agent

    def discover(
        self,
        prompt: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> OnboardPlan:
        try:
            plan = self.code_agent.complete_structured(
                phase="agent_onboard_discovery",
                prompt=prompt,
                schema=OnboardPlan,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            plan = OnboardPlan(
                confidence="low",
                warnings=["AgentOnboard did not produce a valid structured onboarding plan."],
                notes=f"Fallback onboarding plan generated because Code Agent failed: {exc}",
            )
        write_text(output_path, plan.model_dump_json(indent=2))
        return plan


class AgentResource:
    """Reserved for codebase/repository resource resolution.

    Runtime assets needed by an already-selected paper repository are handled by
    AgentInit, because they are part of making the experiment runnable.
    """

    def __init__(self, code_agent: CodeAgentRunner) -> None:
        self.code_agent = code_agent

    def discover(
        self,
        prompt: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> ResourceManifest:
        try:
            manifest = self.code_agent.complete_structured(
                phase="agent_resource_discovery",
                prompt=prompt,
                schema=ResourceManifest,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            manifest = ResourceManifest(
                resources=[],
                unresolved_requirements=[
                    "Resource discovery did not produce a valid structured manifest.",
                ],
                repo_assumptions=[],
                notes=f"Fallback manifest generated because Code Agent failed: {exc}",
            )
        write_text(output_path, manifest.model_dump_json(indent=2))
        return manifest


class AgentInit:
    def __init__(self, code_agent: CodeAgentRunner) -> None:
        self.code_agent = code_agent

    def discover_resources(
        self,
        prompt: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> ResourceManifest:
        try:
            manifest = self.code_agent.complete_structured(
                phase="agent_init_resource_discovery",
                prompt=prompt,
                schema=ResourceManifest,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            manifest = ResourceManifest(
                resources=[],
                unresolved_requirements=[
                    "AgentInit resource discovery did not produce a valid structured manifest.",
                ],
                repo_assumptions=[],
                notes=f"Fallback manifest generated because Code Agent failed: {exc}",
            )
        write_text(output_path, manifest.model_dump_json(indent=2))
        return manifest

    def plan_environment(
        self,
        prompt: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> EnvironmentPlan:
        try:
            plan = self.code_agent.complete_structured(
                phase="agent_init_environment_plan",
                prompt=prompt,
                schema=EnvironmentPlan,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            plan = EnvironmentPlan(
                install_commands=[],
                validation_commands=[],
                notes=f"Fallback environment plan generated because Code Agent failed: {exc}",
            )
        write_text(output_path, plan.model_dump_json(indent=2))
        return plan

    def check_readiness(
        self,
        prompt: str,
        output_path: Path,
        log_path: Path,
        resource_manifest: ResourceManifest,
        environment_plan: EnvironmentPlan,
        eval_command: str,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> PrepareReport:
        try:
            report = self.code_agent.complete_structured(
                phase="agent_init_readiness_check",
                prompt=prompt,
                schema=PrepareReport,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            status = "partial" if resource_manifest.resources or environment_plan.install_commands else "blocked"
            report = PrepareReport(
                resource_manifest=resource_manifest,
                environment_plan=environment_plan,
                readiness_status=status,
                eval_command=eval_command,
                next_steps=[
                    "Review resource_manifest.json and environment_plan.json manually.",
                    "Rerun prepare with a working Code Agent for a fuller readiness check.",
                ],
                notes=f"Fallback prepare report generated because Code Agent failed: {exc}",
            )
        write_text(output_path, report.model_dump_json(indent=2))
        return report


class AgentMonitor:
    def __init__(self, code_agent: CodeAgentRunner, research_agent: DeepResearchRunner) -> None:
        self.code_agent = code_agent
        self.research_agent = research_agent

    def deep_research(
        self,
        config: PaperConfig,
        output_path: Path,
        log_path: Path,
        dry_run: bool = False,
    ) -> ResearchReport:
        prompt = f"""
You are AgentMonitor. Research optimization ideas for this ML paper/codebase.

Paper: {config.paper_title or config.paper_name}
Primary metric: {config.primary_metric} ({config.metric_direction.value} is better)
Baseline metrics: {config.baseline_metrics}

Focus on practical algorithmic and evaluation-safe techniques that could be
implemented in the local repository. Do not suggest changing the dataset,
metric definition, or evaluation protocol.
"""
        try:
            report = self.research_agent.complete_structured(
                prompt=prompt,
                schema=ResearchReport,
                log_path=log_path,
                dry_run=dry_run,
            )
        except Exception as exc:
            report = ResearchReport(
                summary=f"Deep research fallback because the research agent did not return a valid report: {exc}",
                relevant_techniques=[],
                citations=[],
                risks=["No structured live research report was produced."],
            )
        write_text(output_path, report.model_dump_json(indent=2))
        return report

    def summarize_code_analysis(
        self,
        text: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> CodeAnalysis:
        try:
            analysis = self.code_agent.complete_structured(
                phase="agent_monitor_code_analysis",
                prompt="Summarize this repository analysis into the requested structure:\n" + text,
                schema=CodeAnalysis,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception:
            analysis = CodeAnalysis(
                pipeline_summary=text[:4000] or "Code analysis has not been generated yet.",
                key_files=[],
                eval_procedure="See Claude phase logs.",
                optimization_levers=[],
                red_lines=[],
            )
        write_text(output_path, analysis.model_dump_json(indent=2))
        return analysis


class AgentIdeator:
    def __init__(self, code_agent: CodeAgentRunner) -> None:
        self.code_agent = code_agent

    def generate(
        self,
        config: PaperConfig,
        research: ResearchReport,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
    ) -> IdeaLibrary:
        prompt = f"""
You are AgentIdeator. Create a structured optimization idea library.

Paper: {config.paper_title or config.paper_name}
Metric: {config.primary_metric}; direction: {config.metric_direction.value}
Research report:
{research.model_dump_json(indent=2)}

Generate exactly {config.max_ideas} distinct candidate ideas. Use a mix of
ALGO, CODE, and PARAM ideas so the scheduler can choose the strongest
candidates to try. Every idea must preserve the evaluation protocol and dataset.
"""
        try:
            library = self.code_agent.complete_structured(
                phase="agent_ideator_ideas",
                prompt=prompt,
                schema=IdeaLibrary,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            library = IdeaLibrary(
                paper_title=config.paper_title or config.paper_name,
                ideas=_fallback_ideas(config.max_ideas),
                red_line_audit=[
                    "Fallback ideas generated because Code Agent did not return structured ideas.",
                    f"Code Agent error: {exc}",
                ],
            )
        write_text(output_path, library.model_dump_json(indent=2))
        return library


class AgentScheduler:
    def select_next(self, library: IdeaLibrary, completed_ids: set[str]) -> Idea | None:
        priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        candidates = [
            idea
            for idea in library.ideas
            if idea.status == IdeaStatus.pending and idea.idea_id not in completed_ids
        ]
        candidates.sort(key=lambda i: (priority_rank.get(i.priority, 1), i.risk, i.idea_id))
        return candidates[0] if candidates else None


def _fallback_ideas(max_ideas: int) -> list[Idea]:
    templates = [
        (
            "Inspect configurable thresholds and lightweight algorithm branches",
            "Use the Code Agent to inspect evaluation-adjacent model code and identify safe internal levers.",
            "A small internal logic improvement may improve the primary metric without changing protocol.",
            IdeaType.code,
        ),
        (
            "Tune retrieval weighting without changing retrieved candidates",
            "Adjust how retrieved neighbors are weighted or fused while preserving the retrieval database and evaluation data.",
            "Better weighting of existing retrieved context can reduce forecast error without protocol changes.",
            IdeaType.algo,
        ),
        (
            "Review batch-safe numerical stability in forecasting heads",
            "Look for safe dtype, masking, normalization, or nan-handling fixes inside model inference paths.",
            "More stable inference may improve zero-shot forecasts or prevent degraded batches.",
            IdeaType.code,
        ),
        (
            "Try conservative inference hyperparameter defaults",
            "Evaluate safe internal parameters already exposed by the implementation without altering datasets or metrics.",
            "A conservative parameter setting may improve the target metric with low implementation risk.",
            IdeaType.param,
        ),
    ]
    count = max(1, max_ideas)
    ideas: list[Idea] = []
    for index in range(count):
        title, description, hypothesis, idea_type = templates[index % len(templates)]
        ideas.append(
            Idea(
                idea_id=f"IDEA-{index + 1:03d}",
                title=title if index < len(templates) else f"{title} variant {index + 1}",
                type=idea_type,
                priority="MEDIUM",
                risk="LOW",
                description=description,
                hypothesis=hypothesis,
            )
        )
    return ideas


class AgentSupervisor:
    def decide(self, scores_path: Path, config: PaperConfig, new_primary: float, status: str) -> SupervisorDecision:
        if status != "success":
            return SupervisorDecision(is_new_best=False, should_rollback=True, reason="Experiment failed.")

        rows = [row for row in read_jsonl(scores_path) if row.get("status") == "success"]
        best = None
        for row in rows:
            value = row.get("primary_metric")
            if value is None:
                continue
            best = value if best is None else _best_value(best, value, config)
        if best is None:
            return SupervisorDecision(is_new_best=True, should_rollback=False, reason="First successful score.")

        if _is_better(new_primary, best, config):
            return SupervisorDecision(is_new_best=True, should_rollback=False, reason="Primary metric improved.")
        return SupervisorDecision(is_new_best=False, should_rollback=True, reason="No primary metric improvement.")


class AgentFix:
    def __init__(self, code_agent: CodeAgentRunner | None = None) -> None:
        self.code_agent = code_agent

    def plan_environment_fix(
        self,
        config: PaperConfig,
        repo_dir: str,
        output_dir: str,
        failed_stage: str,
        failed_commands: list[str],
        stdout: str,
        stderr: str,
        output_path: Path,
        log_path: Path,
        timeout_seconds: int | None = None,
        dry_run: bool = False,
        previous_fix_plans: list[EnvironmentFixPlan] | None = None,
        previous_attempts: list[FixAttemptSummary] | None = None,
    ) -> EnvironmentFixPlan:
        if self.code_agent is None:
            plan = EnvironmentFixPlan(
                diagnosis="No Code Agent is configured for environment repair.",
                safe_to_execute=False,
                notes="AgentFix cannot run without a CodeAgentRunner.",
            )
            write_text(output_path, plan.model_dump_json(indent=2))
            return plan
        try:
            plan = self.code_agent.complete_structured(
                phase="agent_fix_environment",
                prompt=environment_fix_prompt(
                    config=config,
                    repo_dir=repo_dir,
                    output_dir=output_dir,
                    failed_stage=failed_stage,
                    failed_commands=failed_commands,
                    stdout=stdout,
                    stderr=stderr,
                    previous_fix_plans=previous_fix_plans,
                    previous_attempts=previous_attempts,
                ),
                schema=EnvironmentFixPlan,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
            )
        except Exception as exc:
            plan = EnvironmentFixPlan(
                diagnosis="AgentFix did not produce a valid environment fix plan.",
                safe_to_execute=False,
                notes=f"Fallback fix plan generated because Code Agent failed: {exc}",
            )
        write_text(output_path, plan.model_dump_json(indent=2))
        return plan

    def build_debug_prompt(self, idea: Idea, error_text: str) -> str:
        return f"""
You are AgentFix. The experiment for {idea.idea_id}: {idea.title} failed.

Error/log excerpt:
{error_text[-6000:]}

Debug the implementation inside the repository. Keep the evaluation protocol,
dataset, metric computation, and protected files unchanged. Apply the smallest
fix that makes the evaluation run, then rerun the evaluation.
"""


def _is_better(new_value: float, old_value: float, config: PaperConfig) -> bool:
    if config.metric_direction.value == "lower":
        return new_value < old_value
    return new_value > old_value


def _best_value(a: float, b: float, config: PaperConfig) -> float:
    return min(a, b) if config.metric_direction.value == "lower" else max(a, b)
