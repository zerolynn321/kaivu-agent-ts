---
name: repo-onboard
description: Inspect a cloned research code repository, discover the safest evaluation or baseline command, proactively identify documented baseline/reference results from repository docs/examples/configs/saved outputs, run a bounded baseline check when resources and environment are already available, parse and compare reported metrics or success criteria against documented baselines when possible, and ensure the repository has a local config.yaml. Use after paper-repo-discovery has cloned or selected a repository, or whenever Codex acting as AgentOnboard must reuse or generate config.yaml by scanning README files, scripts, dependency files, examples, entrypoints, existing configs, and documented result references. This skill does not download resources, install dependencies, create environments, run long training/full evaluations without approval, modify experiment logic, or optimize code.
---

# Repo Onboard

Use this skill when AgentOnboard receives a cloned repository and must leave the repository with a usable local `config.yaml` backed by repository evidence and, when feasible, a real baseline/smoke result.

The agent does the onboarding work directly. Do not implement a separate Python or TypeScript pipeline for this logic.

## Terminal Output

Keep terminal-facing progress concise. Report only stage status, key decisions, artifact paths, baseline status, blockers, and next steps. Do not print command strings, full command lists, stdout/stderr blocks, file content snippets, or diffs unless the user explicitly asks. Put detailed evidence, command output, and config details in `config.yaml` or `onboard_report.md`.

## Agent Contract

Role: `AgentOnboard`

Inputs:

- cloned repository path
- paper name or title, when available
- optional paper PDF/path/URL
- optional `paper_repo_resolution.md` from `paper-repo-discovery`
- optional user overrides for eval command, metric, environment, or protected paths
- optional user approval for longer baseline checks

Required output:

- `<repo>/config.yaml`

Optional output:

- `<repo>/onboard_report.md` when evidence, uncertainty, or user decisions should be audited later

Handoff:

- After `config.yaml` exists, hand off to the resource discovery/download skill when required resources are missing, or to the environment setup skill when dependencies are missing.
- Do not continue into resource download, environment setup, optimization, or code modification.

## Workflow

1. Confirm repository context.
   - Resolve the repository path and verify it exists.
   - Inspect the repository root first.
   - Read `paper_repo_resolution.md` if it exists in the repository parent or repository root.

2. Look for an existing `config.yaml`.
   - If `<repo>/config.yaml` exists, read and reuse it.
   - If one or more nested `config.yaml` files exist, inspect them as evidence, but still ensure `<repo>/config.yaml` exists for later stages.
   - Do not overwrite an existing root `config.yaml` unless the user explicitly asks.
   - If the existing root config is incomplete, report missing fields and ask before changing it.

3. Scan the repository when root config is missing.
   - Read README files, docs, examples, CLI guides, scripts, notebooks, config files, dependency files, and common entrypoints.
   - Prefer evidence from files such as `README.md`, `docs/`, `examples/`, `scripts/`, `train.py`, `eval.py`, `test.py`, `main.py`, `pyproject.toml`, `setup.py`, `requirements.txt`, `environment.yml`, `package.json`, and shell scripts.
   - Use cheap read-only commands only, such as file listing, text search, `--help`, or import-free static inspection.
   - Do not install packages, download datasets/models, start training, run long evaluation, or edit source code.

4. Infer onboarding fields and baseline target.
   - Determine paper title/name, repository path, likely evaluation or demo command, primary metric, metric direction, setup hints, pre-eval commands, environment hints, protected paths, and confidence.
   - Prefer a documented evaluation command that produces the paper's primary metric.
   - If a full evaluation is too expensive or needs unavailable resources, choose the safest documented smoke/pretrained/demo command and mark the scope clearly.
   - If no metric is evident, use an empty metric field plus warnings rather than inventing one.
   - Search docs, logs, tables, READMEs, examples, and saved outputs for documented baseline values or expected success criteria.
   - Record documented reference values before later stages run the baseline. Include source file, metric name, value, dataset/split/command conditions, whether it is comparable to the selected command, and confidence.
   - If no comparable documented reference exists, record `reference_status: not_found` and include where the search looked.
   - Treat user-provided overrides as policy unless repository evidence clearly contradicts them.

5. Run a bounded baseline check when feasible.
   - Run only commands that are cheap, documented, and supported by currently available resources and dependencies.
   - Run pre-eval commands only when they are local, reversible, and required for the selected eval command, such as extracting a bundled checkpoint.
   - Do not install packages, download resources, create environments, start training, or run long/full evaluations unless the user explicitly approves.
   - Capture stdout, stderr, return code, elapsed time, and parsed metrics.
   - Compare parsed metrics with documented baseline values when available; otherwise record the observed result as the initial local baseline and mark comparison as `not_available`.
   - If the command cannot run because resources or dependencies are missing, do not guess. Record `baseline_status: pending_resources`, `pending_environment`, or `blocked` with concrete next steps.

6. Create or update `<repo>/config.yaml`.
   - Write a concise YAML file at the repository root.
   - Include enough fields for later agents to proceed without re-discovering the same facts.
   - Include baseline result fields when a bounded baseline check ran.
   - Include `warnings` for uncertain or missing fields.
   - Include `evidence` entries with concrete file paths and snippets or summaries.
   - Do not overwrite an existing root `config.yaml` without approval; if it exists, preserve user-authored values and append missing onboarding/baseline fields only when approved.

7. Verify and report.
   - Re-read `<repo>/config.yaml` after writing.
   - Confirm the path in the final answer.
   - State whether the config was reused or generated.
   - State whether baseline was run, passed, pending, or blocked.
   - List missing or low-confidence fields that the user should confirm before resource or environment setup.

## Config Shape

Use this shape for generated configs. Preserve existing config schemas when reusing a root `config.yaml`.

```yaml
paper_name: ""
paper_title: ""
repo_path: ""
paper_pdf_path: ""

onboard_status: "ready" # ready | partial | blocked
confidence: "low" # high | medium | low

eval_command: ""
primary_metric: ""
metric_direction: "higher" # higher | lower | unknown
baseline:
  status: "not_run" # passed | failed | not_run | pending_resources | pending_environment | blocked
  command: ""
  pre_eval_commands: []
  returncode:
  metrics: {}
  primary_metric_value:
  documented_baseline:
  reference_status: "not_found" # found | not_found | ambiguous
  reference_sources: []
  comparison: "not_available" # matches | better | worse | not_available
  stdout_excerpt: ""
  stderr_excerpt: ""
  notes: ""

setup_commands: []
pre_eval_commands: []
environment:
  package_manager: ""
  python_version: ""
  cuda_version: ""
  conda_env: ""
  venv_path: ""
  env_vars: {}

protected_paths: []
resource_hints: []
warnings: []
evidence: []
notes: ""
```

## Decision Rules

- Mark `onboard_status: ready` only when an eval/demo command and metric or success criterion are supported by repository evidence, and either a bounded baseline check passed or the only missing work belongs to later approved resource/environment stages.
- Mark `onboard_status: partial` when a local config exists but important fields are missing, or when an inferred config is useful but requires user confirmation.
- Mark `onboard_status: blocked` when the repository cannot be inspected or the requested repo path is invalid.
- Mark `baseline.status: passed` when the selected command runs successfully and reported metrics match, improve on, or have no documented baseline to compare against.
- Mark `baseline.status: failed` when the command runs but exits nonzero, emits invalid output, or reported metrics are clearly worse than a documented baseline beyond stated tolerance.
- Mark `baseline.status: pending_resources` when required datasets, checkpoints, or model files are missing.
- Mark `baseline.status: pending_environment` when dependencies, interpreters, compilers, CUDA, or package environments are missing.
- Prefer a partial but honest config over a confident-looking invented config.

## Boundaries

Do:

- ensure a repository-local `config.yaml` exists
- reuse an existing root config when present
- scan repository files to infer onboarding metadata
- run a cheap documented baseline/smoke check when resources and environment are already available
- parse and record metrics when the selected command prints or writes them
- compare against documented baselines when the repository provides them
- preserve uncertainty in `warnings`
- write an audit-friendly `onboard_report.md` when useful

Do not:

- implement onboarding as a new Python or TypeScript pipeline
- overwrite an existing root `config.yaml` without user approval
- install dependencies, download resources, create environments, or run long training/full evaluation without explicit user approval
- change source code, metrics, datasets, evaluation protocol, or generated experiment results
- continue into resource download or environment setup
