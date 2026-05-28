from __future__ import annotations

import json
import shlex
import shutil
import sys
import time
from pathlib import Path

from pydantic import ValidationError

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.agents import AgentFix, AgentIdeator, AgentMonitor, AgentScheduler, AgentSupervisor
    from autosota_lab.code_agent import create_code_agent
    from autosota_lab.docker_runner import DockerRunner
    from autosota_lab.io import append_jsonl, read_yaml, write_text, write_yaml
    from autosota_lab.local_runner import LocalRunner
    from autosota_lab.models import ExperimentResult, IdeaLibrary, IdeaStatus, PaperConfig, ResearchReport
    from autosota_lab.plot import plot_scores
    from autosota_lab.prompts import (
        baseline_setup_prompt,
        build_master_prompt,
        debug_prompt,
        idea_implementation_prompt,
        repository_analysis_prompt,
    )
    from autosota_lab.research_agent import DeepResearchRunner
    from autosota_lab.state import config_path, create_run_paths
else:
    from .agents import AgentFix, AgentIdeator, AgentMonitor, AgentScheduler, AgentSupervisor
    from .code_agent import create_code_agent
    from .docker_runner import DockerRunner
    from .io import append_jsonl, read_yaml, write_text, write_yaml
    from .local_runner import LocalRunner
    from .models import ExperimentResult, IdeaLibrary, IdeaStatus, PaperConfig, ResearchReport
    from .plot import plot_scores
    from .prompts import (
        baseline_setup_prompt,
        build_master_prompt,
        debug_prompt,
        idea_implementation_prompt,
        repository_analysis_prompt,
    )
    from .research_agent import DeepResearchRunner
    from .state import config_path, create_run_paths


class Optimizer:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        repo_path: Path | None = None,
        execution_backend: str | None = None,
        docker_image: str | None = None,
        conda_env: str | None = None,
        code_agent: str = "claude",
        code_agent_command: str | None = None,
        code_agent_command_template: str | None = None,
        research_model: str = "openai/o4-mini-deep-research",
        skip_research: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.config = PaperConfig.model_validate(read_yaml(config_path(self.workspace, paper_name)))
        if repo_path:
            self.config.repo_path = repo_path.expanduser().resolve()
        if execution_backend:
            self.config.execution_backend = execution_backend
        if docker_image:
            self.config.docker_image = docker_image
        if conda_env is not None:
            self.config.conda_env = conda_env
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template
        self.research_model = research_model
        self.skip_research = skip_research
        self.dry_run = dry_run

    def run(
        self,
        max_iterations: int | None = None,
        max_ideas: int | None = None,
        max_debug_attempts: int | None = None,
        max_debug_minutes: int | None = None,
        max_total_minutes: int | None = None,
    ) -> Path:
        if max_iterations is not None:
            self.config.max_iterations = max_iterations
        if max_ideas is not None:
            self.config.max_ideas = max_ideas
        if max_debug_attempts is not None:
            self.config.max_debug_attempts = max_debug_attempts
        if max_debug_minutes is not None:
            self.config.max_debug_minutes = max_debug_minutes

        deadline = time.monotonic() + max_total_minutes * 60 if max_total_minutes else None

        def bounded_timeout(default_seconds: int) -> int:
            if deadline is None:
                return default_seconds
            remaining = int(deadline - time.monotonic())
            return max(1, min(default_seconds, remaining))

        def total_time_expired() -> bool:
            return deadline is not None and time.monotonic() >= deadline

        paths = create_run_paths(self.workspace, self.paper_name)
        write_yaml(paths.logs_dir / "effective_config.yaml", self.config)

        runner = self._create_runner(paths.run_dir)
        self._announce("run_start", f"run_dir={paths.run_dir}")
        self._announce(
            "execution_environment",
            f"backend={self.config.execution_backend}, repo={runner.repo_workdir}, output={runner.output_dir}",
        )
        code_agent = create_code_agent(
            runner,
            agent=self.code_agent,
            command=self.code_agent_command,
            command_template=self.code_agent_command_template,
        )
        research_agent = DeepResearchRunner(model=self.research_model)

        monitor = AgentMonitor(code_agent, research_agent)
        ideator = AgentIdeator(code_agent)
        scheduler = AgentScheduler()
        supervisor = AgentSupervisor()
        fixer = AgentFix()

        self._announce("deep_research", "Preparing research report.")
        if self.skip_research:
            research = ResearchReport(
                summary="Deep research skipped by --skip-research.",
                relevant_techniques=[],
                citations=[],
                risks=["No live literature lookup was performed."],
            )
            write_text(paths.memory_dir / "research_report.md", research.model_dump_json(indent=2))
        else:
            research = monitor.deep_research(
                self.config,
                paths.memory_dir / "research_report.md",
                paths.logs_dir / "agent_monitor_research.log",
                dry_run=self.dry_run,
            )
        self._announce("deep_research", "Research report ready.")
        master_prompt = build_master_prompt(
            self.config,
            research,
            paths,
            repo_dir=runner.repo_workdir,
            output_dir=runner.output_dir,
        )
        write_text(paths.logs_dir / "master_prompt.md", master_prompt)

        self._announce("baseline_setup", "Checking repository, git baseline, and baseline evaluation.")
        code_agent.run_prompt(
            "baseline_setup",
            baseline_setup_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.logs_dir / f"{self.code_agent}_baseline_setup.log",
            timeout_seconds=bounded_timeout(self.config.eval_timeout_seconds + 300),
            dry_run=self.dry_run,
        )
        self._record_baseline_if_available(paths.results_dir / "scores.jsonl")
        self._announce("baseline_setup", "Finished.")

        if total_time_expired():
            return paths.run_dir

        self._announce("repository_analysis", "Inspecting code paths and optimization levers.")
        code_agent.run_prompt(
            "repository_analysis",
            repository_analysis_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.logs_dir / f"{self.code_agent}_repository_analysis.log",
            timeout_seconds=bounded_timeout(1800),
            dry_run=self.dry_run,
        )
        self._announce("repository_analysis", "Finished.")

        if total_time_expired():
            return paths.run_dir

        code_analysis_text = _read_if_exists(paths.memory_dir / "code_analysis.md")
        if code_analysis_text:
            monitor.summarize_code_analysis(
                code_analysis_text,
                paths.memory_dir / "code_analysis.json",
                paths.logs_dir / "agent_monitor_code_analysis.log",
                timeout_seconds=bounded_timeout(900),
                dry_run=self.dry_run,
            )

        self._announce("idea_generation", "Building structured idea library.")
        library = ideator.generate(
            self.config,
            research,
            paths.memory_dir / "idea_library.md",
            paths.logs_dir / "agent_ideator_ideas.log",
            timeout_seconds=bounded_timeout(900),
            dry_run=self.dry_run,
        )
        self._announce("idea_generation", f"Ready with {len(library.ideas)} idea(s).")
        completed: set[str] = set()
        scores_path = paths.results_dir / "scores.jsonl"

        for iteration in range(1, self.config.max_iterations + 1):
            if total_time_expired():
                break
            idea = scheduler.select_next(library, completed)
            if idea is None:
                break
            self._prepare_iteration_git(runner)
            idea.status = IdeaStatus.in_progress
            write_text(paths.memory_dir / "idea_library.md", library.model_dump_json(indent=2))

            self._announce(
                "idea_implementation",
                f"iteration={iteration}, idea={idea.idea_id}, title={idea.title}",
            )
            result = code_agent.run_prompt(
                f"idea_implementation_iter_{iteration:03d}",
                idea_implementation_prompt(self.config, idea, iteration, master_prompt, runner.output_dir),
                paths.logs_dir / f"{self.code_agent}_idea_implementation_iter_{iteration:03d}.log",
                timeout_seconds=bounded_timeout(self.config.eval_timeout_seconds + 900),
                dry_run=self.dry_run,
            )
            metrics_path = paths.results_dir / f"iter_{iteration:03d}_metrics.json"
            experiment = self._load_experiment_result(iteration, idea, metrics_path, result.ok)

            if experiment.status == "failed" and not self.dry_run:
                for attempt in range(1, self.config.max_debug_attempts + 1):
                    if total_time_expired():
                        break
                    self._announce(
                        "debug_repair",
                        f"iteration={iteration}, attempt={attempt}, idea={idea.idea_id}",
                    )
                    debug_result = code_agent.run_prompt(
                        f"debug_repair_iter_{iteration:03d}_attempt_{attempt}",
                        debug_prompt(self.config, idea, iteration, result.stdout + result.stderr, runner.output_dir),
                        paths.logs_dir / f"{self.code_agent}_debug_repair_iter_{iteration:03d}_attempt_{attempt}.log",
                        timeout_seconds=bounded_timeout(self.config.max_debug_minutes * 60),
                        dry_run=False,
                    )
                    experiment = self._load_experiment_result(iteration, idea, metrics_path, debug_result.ok)
                    if experiment.status == "success":
                        break

            commit = self._commit_iteration_git(runner, iteration, idea)
            experiment.commit = commit
            decision = supervisor.decide(scores_path, self.config, experiment.primary_metric, experiment.status)
            append_jsonl(scores_path, experiment)

            if experiment.status == "success":
                idea.status = IdeaStatus.success
                idea.result = experiment.notes or f"{self.config.primary_metric}={experiment.primary_metric}"
                if decision.is_new_best:
                    runner.run(f"git tag -f _best {shlex.quote(commit)}")
                elif decision.should_rollback:
                    self._checkout_best(runner)
            else:
                idea.status = IdeaStatus.failed
                idea.result = experiment.notes
                if decision.should_rollback:
                    self._checkout_best(runner)

            completed.add(idea.idea_id)
            write_text(paths.memory_dir / "idea_library.md", library.model_dump_json(indent=2))
            self._announce(
                "idea_implementation",
                f"iteration={iteration} finished with status={experiment.status}, primary_metric={experiment.primary_metric}",
            )

        plot_scores(scores_path, paths.results_dir / "optimization_curve.png")
        self._export_best(runner, paths.run_dir / "best_code")
        self._announce("run_complete", f"run_dir={paths.run_dir}")
        return paths.run_dir

    def _create_runner(self, run_dir: Path):
        if self.config.execution_backend == "docker":
            return DockerRunner(
                image=self.config.docker_image,
                repo_path=self.config.repo_path,
                run_dir=run_dir,
                env=self.config.env_vars,
            )
        return LocalRunner(
            repo_path=self.config.repo_path,
            run_dir=run_dir,
            env=self.config.env_vars,
            conda_env=self.config.conda_env,
            conda_executable=self.config.conda_executable,
            venv_path=self.config.venv_path,
        )

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota] {timestamp} | {stage} | {message}", flush=True)

    def _record_baseline_if_available(self, scores_path: Path) -> None:
        if not self.config.baseline_metrics:
            return
        primary = self.config.baseline_metrics.get(self.config.primary_metric)
        if primary is None:
            return
        append_jsonl(
            scores_path,
            ExperimentResult(
                iter=0,
                idea_id="baseline",
                idea_title="Paper baseline",
                metrics=self.config.baseline_metrics,
                primary_metric=primary,
                status="success",
                notes="Baseline from onboard config.",
            ),
        )

    def _load_experiment_result(
        self,
        iteration: int,
        idea,
        metrics_path: Path,
        command_ok: bool,
    ) -> ExperimentResult:
        if self.dry_run:
            return ExperimentResult(
                iter=iteration,
                idea_id=idea.idea_id,
                idea_title=idea.title,
                metrics={},
                primary_metric=0.0,
                status="failed",
                notes="Dry run: Claude/Docker command was previewed only.",
            )
        if not metrics_path.exists():
            return ExperimentResult(
                iter=iteration,
                idea_id=idea.idea_id,
                idea_title=idea.title,
                metrics={},
                primary_metric=0.0,
                status="failed",
                notes="Claude did not produce the metrics JSON file." if command_ok else "Claude command failed.",
            )
        try:
            payload = json.loads(metrics_path.read_text(encoding="utf-8"))
            status = payload.get("status", "success")
            primary = float(payload.get("primary_metric"))
            metrics = {k: float(v) for k, v in (payload.get("metrics") or {}).items()}
            return ExperimentResult(
                iter=iteration,
                idea_id=idea.idea_id,
                idea_title=idea.title,
                metrics=metrics,
                primary_metric=primary,
                status="success" if status == "success" else "failed",
                notes=str(payload.get("notes", "")),
            )
        except (json.JSONDecodeError, TypeError, ValueError, ValidationError) as exc:
            return ExperimentResult(
                iter=iteration,
                idea_id=idea.idea_id,
                idea_title=idea.title,
                metrics={},
                primary_metric=0.0,
                status="failed",
                notes=f"Invalid metrics JSON: {exc}",
            )

    def _git_rev_parse(self, runner) -> str:
        if self.dry_run:
            return ""
        proc = runner.run("git rev-parse HEAD")
        return proc.stdout.strip() if proc.returncode == 0 else ""

    def _prepare_iteration_git(self, runner) -> None:
        if self.dry_run:
            return
        self._checkout_best(runner)
        runner.run("git tag -f _pre_iter HEAD")

    def _checkout_best(self, runner) -> None:
        if self.dry_run:
            return
        runner.run("git checkout -f _best && git clean -fd")

    def _commit_iteration_git(self, runner, iteration: int, idea) -> str:
        if self.dry_run:
            return ""
        runner.run("git add -A")
        tag = _iteration_tag(iteration, idea.idea_id)
        message = f"AutoSOTA iter {iteration:03d}: {idea.idea_id} {idea.title}"
        proc = runner.run(f"git commit --allow-empty -m {shlex.quote(message)}")
        if proc.returncode != 0:
            return self._git_rev_parse(runner)
        commit = self._git_rev_parse(runner)
        if commit:
            runner.run(f"git tag -f {shlex.quote(tag)} {shlex.quote(commit)}")
        return commit

    def _export_best(self, runner, export_dir: Path) -> None:
        if self.dry_run:
            return
        runner.run("git checkout _best 2>/dev/null || true")
        if export_dir.exists():
            shutil.rmtree(export_dir)
        ignore = shutil.ignore_patterns(".git", "__pycache__", ".autosota_protected_hashes.json")
        shutil.copytree(self.config.repo_path, export_dir, ignore=ignore)


def _read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _iteration_tag(iteration: int, idea_id: str) -> str:
    safe_id = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in idea_id).strip("-")
    return f"_iter_{iteration:03d}_{safe_id or 'idea'}"


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the AutoSOTA optimize pipeline.")
    parser.add_argument("paper_name", help="Paper name under <workspace>/.autosota/papers/.")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Directory for AutoSOTA state and run outputs. Defaults to the current working directory.",
    )
    parser.add_argument("--repo", type=Path, help="Override repo_path from the paper config.")
    parser.add_argument(
        "--execution-backend",
        choices=["local", "docker"],
        help="Where to run Code Agent commands. Defaults to the paper config, usually local.",
    )
    parser.add_argument("--docker-image", help="Override docker_image from the paper config.")
    parser.add_argument("--conda-env", help="Run local commands with `conda run -n <env>`.")
    parser.add_argument("--code-agent", choices=["claude", "codex"], default="codex")
    parser.add_argument("--code-agent-command", help="Code Agent executable or command prefix.")
    parser.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    parser.add_argument(
        "--research-model",
        default="openai/o4-mini-deep-research",
        help="Deep research model. This is separate from the Code Agent used for code changes.",
    )
    parser.add_argument(
        "--skip-onboard",
        action="store_true",
        help="Accepted for compatibility; optimize.py always uses an existing paper config.",
    )
    parser.add_argument("--skip-research", action="store_true", help="Use a local placeholder research report.")
    parser.add_argument("--max-iterations", "--max-iter", dest="max_iterations", type=int)
    parser.add_argument("--max-ideas", type=int, help="Number of candidate ideas to generate before scheduling.")
    parser.add_argument("--max-debug", dest="max_debug_attempts", type=int)
    parser.add_argument("--max-debug-min", dest="max_debug_minutes", type=int)
    parser.add_argument("--max-total-minutes", type=int)
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and preview commands only.")
    args = parser.parse_args(argv)

    run_dir = Optimizer(
        workspace=args.workspace,
        paper_name=args.paper_name,
        repo_path=args.repo,
        execution_backend=args.execution_backend,
        docker_image=args.docker_image,
        conda_env=args.conda_env,
        code_agent=args.code_agent,
        code_agent_command=args.code_agent_command,
        code_agent_command_template=args.code_agent_command_template,
        research_model=args.research_model,
        skip_research=args.skip_research,
        dry_run=args.dry_run,
    ).run(
        max_iterations=args.max_iterations,
        max_ideas=args.max_ideas,
        max_debug_attempts=args.max_debug_attempts,
        max_debug_minutes=args.max_debug_minutes,
        max_total_minutes=args.max_total_minutes,
    )
    print(f"[optimize] run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
