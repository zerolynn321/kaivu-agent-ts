from __future__ import annotations

from pathlib import Path

from .models import Idea, PaperConfig, ResearchReport, RunPaths


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def build_master_prompt(
    config: PaperConfig,
    research: ResearchReport,
    paths: RunPaths,
    repo_dir: str,
    output_dir: str,
) -> str:
    template = (TEMPLATE_DIR / "master_prompt.md").read_text(encoding="utf-8")
    return template.format(
        paper_title=config.paper_title or config.paper_name,
        repo_path=repo_dir,
        host_repo_path=str(config.repo_path),
        output_dir=output_dir,
        eval_command=config.eval_command,
        eval_timeout_seconds=config.eval_timeout_seconds,
        primary_metric=config.primary_metric,
        metric_direction=config.metric_direction.value,
        max_iterations=config.max_iterations,
        max_debug_attempts=config.max_debug_attempts,
        max_debug_minutes=config.max_debug_minutes,
        baseline_metrics=config.baseline_metrics,
        env_exports=_env_exports(config.env_vars),
        research_report=research.model_dump_json(indent=2),
        run_paths=paths.model_dump_json(indent=2),
    )


def baseline_setup_prompt(config: PaperConfig, repo_dir: str, output_dir: str) -> str:
    return f"""
You are the Code Agent running the Baseline Setup stage of AutoSOTA Laboratory.

Repository path: {repo_dir}
Output directory: {output_dir}
Evaluation command: {config.eval_command}
Primary metric: {config.primary_metric} ({config.metric_direction.value} is better)

Tasks:
1. Confirm the repository is accessible.
2. Initialize git if needed, configure user.name/user.email, commit the current tree, tag it _baseline and _best.
3. Run the baseline evaluation command without changing the evaluation protocol.
4. Write a concise baseline summary to {output_dir}/memory/baseline.md.

Do not modify datasets, metric code, or evaluation logic.
"""


def repository_analysis_prompt(config: PaperConfig, repo_dir: str, output_dir: str) -> str:
    return f"""
You are AgentMonitor using the Code Agent for the Repository Analysis stage.

Explore {repo_dir} thoroughly enough to optimize {config.paper_title}.
Identify the data flow, model flow, evaluation command, metric parsing, and safe
optimization levers. Write the result to:

{output_dir}/memory/code_analysis.md

Do not edit source code in this phase.
"""


def idea_implementation_prompt(
    config: PaperConfig,
    idea: Idea,
    iteration: int,
    master_prompt: str,
    output_dir: str,
) -> str:
    return f"""
{master_prompt}

Now execute Idea Implementation iteration {iteration}.

Selected idea:
{idea.model_dump_json(indent=2)}

Required steps:
1. Implement exactly one logical change for the selected idea.
2. Evaluate with: {config.eval_command}
3. Parse the primary metric `{config.primary_metric}`.
4. Write {output_dir}/results/iter_{iteration:03d}_metrics.json with:
   {{
     "primary_metric": <float>,
     "metrics": {{"{config.primary_metric}": <float>}},
     "status": "success" or "failed",
     "notes": "brief notes"
   }}
5. If evaluation fails, preserve the error in the JSON notes field.

AutoSOTA manages git checkout, commits, and tags outside this prompt. Do not run
git commit, git tag, git checkout, git reset, or git clean in this phase.

Do not change the dataset, evaluation script, metric computation, or protected paths.
"""


def debug_prompt(config: PaperConfig, idea: Idea, iteration: int, error_text: str, output_dir: str) -> str:
    return f"""
You are AgentFix. Debug iteration {iteration} for idea {idea.idea_id}.

The previous attempt failed. Error/log excerpt:
{error_text[-8000:]}

Fix only the implementation bug introduced by this iteration. Then rerun:
{config.eval_command}

Update {output_dir}/results/iter_{iteration:03d}_metrics.json with the final status.
AutoSOTA manages git commits and tags outside this prompt. Do not run git commit,
git tag, git checkout, git reset, or git clean in this phase.
"""


def _env_exports(env_vars: dict[str, str]) -> str:
    return "\n".join(f"export {key}={value!r}" for key, value in env_vars.items())
