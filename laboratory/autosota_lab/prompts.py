from __future__ import annotations

from pathlib import Path

from .models import EnvironmentFixPlan, EnvironmentPlan, FixAttemptSummary, Idea, OnboardPlan, PaperConfig, PrepareReport, ResourceManifest, ResearchReport, RunPaths


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def onboard_discovery_prompt(
    paper_name: str,
    repo_dir: str,
    paper_pdf_path: str = "",
    resource_root: str = "",
) -> str:
    return f"""
You are AgentOnboard running the AutoSOTA Laboratory onboarding discovery stage.

Repository path: {repo_dir}
Paper name: {paper_name}
Paper PDF path, if available: {paper_pdf_path or "(not provided)"}
Resource root, if available: {resource_root or "(not provided)"}

Tasks:
1. Inspect the local repository without modifying files.
2. Find the most likely evaluation or baseline command for a quick reference run.
3. Identify the primary metric printed or saved by that evaluation, and whether higher or lower is better.
4. Infer a paper title, useful setup commands, pre-eval commands, conda env name, and protected paths when there is clear repo evidence.
5. Prefer README, scripts, config files, examples, and entrypoint code over guesses.

Rules:
- Do not install dependencies, download resources, start training, or run long evaluations.
- Do not edit the repository.
- If multiple eval commands are plausible, choose the safest baseline/inference command and explain alternatives in warnings.
- Keep commands relative to the repository root.
- Return only valid JSON matching the OnboardPlan schema.

OnboardPlan schema:
{OnboardPlan.model_json_schema()}
"""


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


def resource_discovery_prompt(config: PaperConfig, repo_dir: str, output_dir: str) -> str:
    return f"""
You are AgentResource running the Resource Discovery stage of AutoSOTA Laboratory.

Repository path: {repo_dir}
Paper title: {config.paper_title or config.paper_name}
Paper PDF path, if available: {config.paper_pdf_path or "(not provided)"}
Resource root, if available: {config.resource_root or "(not provided)"}
Evaluation command: {config.eval_command}

Tasks:
1. Inspect the repository without downloading files or modifying source code.
2. Read README files, dependency files, config files, scripts, examples, and evaluation entrypoints.
3. Identify required datasets, pretrained models, checkpoints, caches, local path assumptions, API tokens, and external URLs.
4. For every resource the repository expects to read, set local_path to the path as seen from the repository root, especially symlinked paths.
5. Prefer concrete evidence from the repository over guesses. Put uncertain items in unresolved_requirements.
6. Write a JSON resource manifest to {output_dir}/memory/resource_manifest.json.

Return only valid JSON matching the ResourceManifest schema. Do not execute downloads,
do not install packages, and do not edit the repository.

ResourceManifest schema:
{ResourceManifest.model_json_schema()}
"""


def environment_planning_prompt(config: PaperConfig, repo_dir: str, output_dir: str) -> str:
    return f"""
You are AgentInit running the Environment Planning stage of AutoSOTA Laboratory.

Repository path: {repo_dir}
Paper title: {config.paper_title or config.paper_name}
Evaluation command: {config.eval_command}
Configured setup commands: {config.setup_commands}
Configured pre-eval commands: {config.pre_eval_commands}
Configured conda env: {config.conda_env or "(not provided)"}
Configured venv path: {config.venv_path or "(not provided)"}
Configured environment variables: {config.env_vars}

Tasks:
1. Inspect the repository and infer the intended Python, CUDA, PyTorch, package manager, and dependency setup.
2. Produce a conservative setup plan that a user or later agent can execute.
3. Include validation commands that are cheap and diagnostic, such as Python import checks, CUDA visibility checks, and command help checks.
4. Preserve the scientific protocol: do not propose changes to datasets, metric computation, evaluation splits, or target metric semantics.
5. Write a JSON environment plan to {output_dir}/memory/environment_plan.json.

If configured setup commands are provided, treat them as user-approved environment
policy and preserve them unless the repository clearly proves they are invalid.
For RTX 5090 / sm_120 CUDA failures, prefer a CUDA 12.8-capable PyTorch setup in
a Python 3.10 environment, then validate that faiss imports with numpy<2.0.

Return only valid JSON matching the EnvironmentPlan schema. Do not install packages,
do not run long training/evaluation, and do not edit the repository.

EnvironmentPlan schema:
{EnvironmentPlan.model_json_schema()}
"""


def readiness_check_prompt(config: PaperConfig, repo_dir: str, output_dir: str) -> str:
    return f"""
You are AgentInit running the Readiness Check stage of AutoSOTA Laboratory.

Repository path: {repo_dir}
Output directory: {output_dir}
Evaluation command: {config.eval_command}
Primary metric: {config.primary_metric} ({config.metric_direction.value} is better)

Available prepare artifacts, if present:
- {output_dir}/memory/resource_manifest.json
- {output_dir}/memory/resource_acquisition_report.json
- {output_dir}/memory/environment_plan.json
- {output_dir}/memory/setup_status.json
- {output_dir}/logs/setup_commands.log
- {output_dir}/logs/validation_commands.log
- {output_dir}/logs/baseline_eval.log
- {output_dir}/results/baseline_metrics.json

Tasks:
1. Inspect the prepare artifacts, command logs, setup_status.json, and the repository.
2. Decide whether the repository is ready for baseline evaluation, partially ready, or blocked.
3. Identify the next concrete steps required before running the baseline.
4. Write a JSON prepare report to {output_dir}/memory/prepare_report.json.

Return only valid JSON matching the PrepareReport schema. Do not download resources,
do not install packages, do not run long evaluations, and do not edit the repository.

PrepareReport schema:
{PrepareReport.model_json_schema()}
"""


def environment_fix_prompt(
    config: PaperConfig,
    repo_dir: str,
    output_dir: str,
    failed_stage: str,
    failed_commands: list[str],
    stdout: str,
    stderr: str,
    previous_fix_plans: list[EnvironmentFixPlan] | None = None,
    previous_attempts: list[FixAttemptSummary] | None = None,
) -> str:
    previous = [plan.model_dump(mode="json") for plan in previous_fix_plans or []]
    attempts = [attempt.model_dump(mode="json") for attempt in previous_attempts or []]
    return f"""
You are AgentFix repairing an AutoSOTA environment preparation failure.

Repository path: {repo_dir}
Output directory: {output_dir}
Paper title: {config.paper_title or config.paper_name}
Evaluation command: {config.eval_command}
Configured conda env: {config.conda_env or "(not provided)"}
Resource root: {config.resource_root or "(not provided)"}
Failed stage: {failed_stage}
Failed commands:
{failed_commands}

Previous fix plans:
{previous}

Previous fix attempts and results:
{attempts}

STDOUT excerpt:
{stdout[-7000:]}

STDERR excerpt:
{stderr[-7000:]}

Tasks:
1. Diagnose the smallest environment/resource issue that blocks the failed stage.
2. Propose only protocol-preserving environment fixes. Prefer dependency, CUDA/PyTorch,
   NumPy/faiss ABI, conda/pip, missing resource path, and GPU selection fixes.
3. For PyTorch/CUDA/GPU errors, infer a compatible install or validation command.
4. For GPU OOM, prefer a command that selects an available GPU or sets CUDA_VISIBLE_DEVICES.
5. For missing resources, propose download or symlink/path-binding commands only when the
   source or resource_root is explicit.
6. If previous attempts already tried the obvious fix, propose a different next step or set safe_to_execute=false.

Rules:
- Do not modify datasets, labels, evaluation scripts, metric computation, or train/test splits.
- Do not propose git reset, git checkout, git clean, git commit, or destructive deletes.
- Do not propose source-code edits unless they are narrow path/output compatibility fixes outside protected paths.
- Set safe_to_execute=false unless every command is limited to environment setup,
  resource placement, path/output compatibility, or validation.
- Return only valid JSON matching the EnvironmentFixPlan schema.

EnvironmentFixPlan schema:
{EnvironmentFixPlan.model_json_schema()}
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
