---
name: repo-onboard
description: Inspect a cloned research code repository and ensure it has a local config.yaml for later resource, environment, and baseline stages. Use after paper-repo-discovery has cloned or selected a repository, or whenever Codex acting as AgentOnboard must reuse an existing repository config.yaml or generate one by scanning README files, scripts, dependency files, examples, and entrypoints. This skill only owns onboarding metadata and config creation; it must not download resources, install dependencies, run long evaluations, modify experiment logic, or optimize code.
---

# Repo Onboard

Use this skill when AgentOnboard receives a cloned repository and must leave the repository with a usable local `config.yaml`.

The agent does the onboarding work directly. Do not implement a separate Python or TypeScript pipeline for this logic.

## Agent Contract

Role: `AgentOnboard`

Inputs:

- cloned repository path
- paper name or title, when available
- optional paper PDF/path/URL
- optional `paper_repo_resolution.md` from `paper-repo-discovery`
- optional user overrides for eval command, metric, environment, or protected paths

Required output:

- `<repo>/config.yaml`

Optional output:

- `<repo>/onboard_report.md` when evidence, uncertainty, or user decisions should be audited later

Handoff:

- After `config.yaml` exists, hand off to the resource discovery/download skill.
- Do not continue into resource download, environment setup, baseline execution, or code modification.

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

4. Infer onboarding fields.
   - Determine paper title/name, repository path, likely evaluation or demo command, primary metric, metric direction, setup hints, pre-eval commands, environment hints, protected paths, and confidence.
   - If no evaluation command is evident, choose the safest documented smoke/demo/help command as a placeholder and mark confidence low.
   - If no metric is evident, use an empty metric field plus warnings rather than inventing one.
   - Treat user-provided overrides as policy unless repository evidence clearly contradicts them.

5. Create `<repo>/config.yaml` when missing.
   - Write a concise YAML file at the repository root.
   - Include enough fields for later agents to proceed without re-discovering the same facts.
   - Include `warnings` for uncertain or missing fields.
   - Include `evidence` entries with concrete file paths and snippets or summaries.

6. Verify and report.
   - Re-read `<repo>/config.yaml` after writing.
   - Confirm the path in the final answer.
   - State whether the config was reused or generated.
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

- Mark `onboard_status: ready` only when an eval/demo command and metric or success criterion are supported by repository evidence.
- Mark `onboard_status: partial` when a local config exists but important fields are missing, or when an inferred config is useful but requires user confirmation.
- Mark `onboard_status: blocked` when the repository cannot be inspected or the requested repo path is invalid.
- Prefer a partial but honest config over a confident-looking invented config.

## Boundaries

Do:

- ensure a repository-local `config.yaml` exists
- reuse an existing root config when present
- scan repository files to infer onboarding metadata
- preserve uncertainty in `warnings`
- write an audit-friendly `onboard_report.md` when useful

Do not:

- implement onboarding as a new Python or TypeScript pipeline
- overwrite an existing root `config.yaml` without user approval
- install dependencies, download resources, run long commands, or execute training/evaluation
- change source code, metrics, datasets, evaluation protocol, or generated experiment results
- continue into resource download or environment setup
