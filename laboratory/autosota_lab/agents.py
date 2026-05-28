from __future__ import annotations

from pathlib import Path

from .code_agent import CodeAgentRunner
from .io import read_jsonl, write_text
from .models import CodeAnalysis, Idea, IdeaLibrary, IdeaStatus, IdeaType, PaperConfig, ResearchReport, SupervisorDecision
from .research_agent import DeepResearchRunner


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
