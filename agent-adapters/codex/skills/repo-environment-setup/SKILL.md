---
name: repo-environment-setup
description: Build and validate the smallest runtime environment needed for the configured minimum original-method reproduction after repo-resource-prepare has staged its representative data, checkpoint, or released-result assets. Use when Codex acting as AgentInit must target the user-selected conda/venv environment, infer only dependencies required by the selected baseline path, handle Python/CUDA/framework compatibility, install approved packages, run cheap pre-baseline validation, write environment_plan.yaml and environment_setup_report.md, and invoke AgentFix on failures. Do not expand the environment for unrelated paper datasets, training paths, or optional experiments.
---

# Repo Environment Setup

Use this skill after `repo-onboard` and `repo-resource-prepare` when AgentInit must make the final repository's selected minimum-reproduction command runnable inside the environment chosen before resource download.

The agent does the setup directly through Codex tool calls and shell commands. Do not implement a separate Python or TypeScript environment pipeline.

For common virtual environment creation, activation, mirror, dependency resolver, CUDA/framework, NumPy ABI, and validation-command failures, consult `repo-env-troubleshooting` as a reference before escalating risky fixes.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<run_dir>/experiment_artifacts/`. Write environment plans under `plans/`, reports under `reports/`, validation evidence under `evidence/`, and logs under `logs/`. Do not place these auxiliary files in the repository root. Keep standard runtime dependency definitions such as `environment.yml`, `requirements*.txt`, lockfiles, and package manifests in their normal codebase locations.

## Terminal Output

Keep terminal-facing progress concise. Report only stage status, key decisions, artifact paths, environment readiness, blockers, and next steps. Do not print command strings, full command lists, stdout/stderr blocks, file content snippets, or diffs unless the user explicitly asks. Put detailed commands, validation output, logs, and evidence in the environment plan/report files.

## Agent Contract

Role: `AgentInit`

Inputs:

- cloned repository path
- `<artifact_root>/manifests/config.yaml`
- run directory
- optional `<artifact_root>/manifests/resource_manifest.yaml`
- optional `<artifact_root>/reports/resource_acquisition_report.md`
- optional user policy: environment name, package manager preference, CUDA/GPU target, allowed installs, maximum setup time, package mirror preference

Default dependency size policy:

- Unless the user provides a stricter limit, dependency installs up to about 6 GB of new downloads for this reproduction task are acceptable when they are required by the selected paper-aligned minimum reproduction and install only into the selected repository-specific environment.
- When the user explicitly chose or created a repository-specific environment during `repo-resource-prepare`, that approval also covers installing the dependencies required by the selected minimum reproduction into that environment. Do not ask again for each ordinary `pip` or `conda` install.
- A recorded environment is valid only when it comes from an explicit current user choice. Do not treat an inferred default name, numbered run directory, existing pattern from previous tests, or an agent-proposed environment name as approval to create or use it.
- Major frameworks such as PyTorch, TensorFlow, JAX, CUDA toolkits, faiss, RAPIDS, or AutoGluon do not require a separate approval when they are documented or inferred requirements for the selected minimum reproduction, install only into the selected environment, and remain within the default budget.
- Ask before installs expected to exceed 6 GB total for this task, installs with unknown but plausibly larger size, global package-manager configuration changes, untrusted or unofficial mirrors, source builds expected to take a long time, installs outside the selected environment, or dependency/version changes beyond what the selected minimum reproduction requires.

Required outputs:

- `<artifact_root>/plans/environment_plan.yaml`
- `<artifact_root>/reports/environment_setup_report.md`
- a runnable environment, or a concrete blocker with next action

Optional outputs:

- small updates to `<artifact_root>/manifests/config.yaml` for environment metadata only, such as `conda_env`, `venv_path`, `setup_commands`, `validation_commands`, or `env_vars`

Handoff:

- After setup passes validation, hand off to baseline/eval execution.
- If setup or validation fails, automatically invoke `agent-fix-error-recovery` with the failed command, stdout/stderr, repo path, run directory, plan, and reports.

## Workflow

1. Confirm context.
   - Resolve the repository path and run directory.
   - Read `<artifact_root>/manifests/config.yaml`.
   - Read resource manifests/reports when present.
   - Extract the expected repository-specific environment from config or manifest: manager, name/path, Python version, and activation command.
   - Inspect only environment-relevant files: README, docs, `requirements*.txt`, `environment*.yml`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `conda*.yml`, Dockerfile, install scripts, examples, CI configs, and eval entrypoints.

2. Verify the current shell is inside the expected virtual environment.
   - Check the active environment before any dependency installation:
     - conda: compare `CONDA_DEFAULT_ENV` and/or `sys.prefix` with the expected conda env name/path.
     - venv: compare `VIRTUAL_ENV` and `sys.prefix` with the expected venv path.
   - If no expected environment is recorded, stop and ask the user to provide one or rerun `repo-resource-prepare` to create/record it.
   - If the expected environment appears inferred from the run directory or generated by the agent without explicit user approval in the current request, mark the plan `blocked` and ask the user to confirm reuse or creation before installing.
   - If the expected environment equals a generic workflow environment such as `autosota`, `base`, or the environment currently used to run Codex, require explicit user confirmation that this repository should reuse it. Otherwise mark the plan `blocked` and ask for a repository-specific environment name.
   - If the current shell is not inside the expected environment, do not install dependencies into the active environment.
   - Report the expected activation command and ask the user to activate it, or ask for explicit approval to run all setup and validation commands through a scoped command such as `conda run -n <env>` or `<venv>/bin/python`.
   - Mark the plan `blocked` until the environment mismatch is resolved.
   - If the mismatch or environment creation behavior is unclear, consult `repo-env-troubleshooting` before proposing a fix.

3. Infer environment requirements.
   - Identify Python version, package manager, dependency files, setup commands, validation commands, and command-scoped environment variables.
   - Identify GPU requirements: CUDA version, PyTorch/TensorFlow/JAX version constraints, compute capability notes, custom CUDA ops, `nvcc`, compiler, and driver assumptions.
   - Prefer explicit repository documentation over generic compatibility guesses.
   - Prefer the smallest environment that can run the configured minimum original-method baseline command.
   - Do not install dependencies used only by unselected datasets, full retraining, appendix experiments, notebooks, or optional comparison methods.
   - When an official pretrained evaluation route is selected, do not add training-only packages unless the same command requires them.
   - If the repository requires old frameworks, preserve that evidence instead of upgrading by default.
   - Infer a safe install-source policy:
     - Prefer fast China-accessible mirrors when they are compatible with the required packages, such as Tsinghua PyPI (`https://pypi.tuna.tsinghua.edu.cn/simple`) for pip installs.
     - For conda installs, prefer user-approved Tsinghua/China-accessible channels or command-scoped channel URLs when official channels are slow or unreachable.
     - Do not change package names, versions, CUDA build selectors, or framework wheel indexes only for speed.
     - Use official package indexes/selectors when required for correctness, especially for PyTorch/TensorFlow/JAX CUDA wheels or project-documented install commands.
     - Do not modify global pip/conda configuration unless the user explicitly approves that configuration change.

4. Write the plan before installing.
   - Write `<artifact_root>/plans/environment_plan.yaml`.
   - Include `status: planned` or `blocked`, the expected environment name/path, active environment check result, install commands, validation commands, mirror/install-source policy, evidence, assumptions, risks, and approval requirements.
   - Present the plan before installing packages, but do not stop for another approval when the user has already selected the target environment and the planned installs are required for the minimum reproduction, scoped to that environment, and within policy.

5. Ask before environment-changing actions.
   - Ask before creating, deleting, replacing, or switching away from the repository-specific conda/venv environment.
   - Do not ask again before installing or upgrading dependencies that are required for the selected minimum reproduction when the user has already chosen the repository-specific environment and the install stays inside it.
   - Do not ask again before installing major frameworks such as PyTorch, TensorFlow, JAX, CUDA toolkits, faiss, RAPIDS, or AutoGluon when they are required for the selected minimum reproduction, scoped to the selected environment, and within the default 6 GB per-task budget.
   - Ask before installing system packages.
   - Ask before using non-official mirrors unless the user has already requested or approved a fast mirror policy for this setup.
   - Ask before dependency installs expected to exceed the default 6 GB per-task budget, or when package-manager resolution indicates an unexpectedly large install above that budget.
   - Ask before changing global pip/conda configuration, using editable installs that modify the repo, long source builds, or commands expected to take a long time.
   - If the user has already approved a specific environment policy in this turn, apply it without asking repeatedly for ordinary required installs.

6. Execute approved setup.
   - Use the package manager implied by the repo when clear; otherwise prefer conda for Python/CUDA-heavy ML repos and venv/pip for simple CPU-only repos.
   - All dependency installation commands must install into the environment selected or created by `repo-resource-prepare`.
   - Never install dependencies into any other environment unless the user explicitly changes the environment policy.
   - Prefer command-scoped mirror flags over global configuration changes:
     - pip: prefer per-command `-i https://pypi.tuna.tsinghua.edu.cn/simple` when a fast China-accessible mirror is appropriate.
     - conda: prefer command-scoped channels or an environment-local approach when possible; ask before editing global `.condarc`.
   - Fall back to official indexes/channels when a mirror lacks required packages, serves incompatible builds, or conflicts with documented framework install selectors.
   - Keep cache/output directories under the run directory when practical.
   - Keep commands scoped to the selected environment.
   - Record every executed command and result in the setup report.
   - Do not edit source code, dataset code, metrics, or evaluation protocol during environment setup.

7. Validate.
   - Run cheap checks before any full baseline:
     - `python --version`
     - package import/version checks for core dependencies
     - `nvidia-smi` or CUDA visibility checks when GPU is required
     - `python -c` framework checks, such as importing torch/tensorflow and checking CUDA availability
     - command `--help`, import check, bounded preflight, or the configured validation command when documented
   - Do not run long training or full evaluation unless the user explicitly approves.
   - If validation fails, automatically invoke `agent-fix-error-recovery`.
   - For validation failures that look like known environment conventions, such as absl `--help` returning nonzero after printing valid help, consult `repo-env-troubleshooting` and record the classification before invoking broad fixes.

8. Update reports.
   - Write `<artifact_root>/reports/environment_setup_report.md`.
   - If useful, update `<artifact_root>/manifests/config.yaml` with environment metadata only.
   - Re-read plan/report and confirm whether the status is `ready`, `partial`, or `blocked`.

## Plan Shape

Use this shape for `environment_plan.yaml`:

```yaml
repo_path: ""
run_dir: ""
status: "planned" # planned | ready | partial | blocked | failed
environment:
  manager: "" # conda | venv | system | docker | unknown
  name: ""
  path: ""
  activation: ""
  active: false
  active_check: ""
  python_version: ""
  cuda_version: ""
  gpu_required: false
  framework: "" # pytorch | tensorflow | jax | none | unknown
  framework_version: ""
install_commands: []
validation_commands: []
install_source_policy:
  prefer_fast_mirrors: true
  pip_index_url: "https://pypi.tuna.tsinghua.edu.cn/simple"
  conda_channels: []
  global_config_changes_allowed: false
  notes: ""
env_vars: {}
evidence:
  - file: ""
    detail: ""
approval_required:
  - action: ""
    reason: ""
risks: []
assumptions: []
notes: ""
```

Use this shape for `environment_setup_report.md`:

```markdown
# Environment Setup Report

## Summary
- Status:
- Environment:
- Python:
- CUDA/GPU:
- Framework:

## Commands
| Command | Executed | Return code | Result | Notes |
|---|---:|---:|---|---|

## Validation
| Check | Result | Notes |
|---|---|---|

## AgentFix
- Invoked:
- Outcome:

## Remaining Blockers
- ...
```

## Decision Rules

- `ready`: approved setup commands completed and cheap validation passed.
- `partial`: some setup completed, but optional validation or non-blocking dependency checks remain.
- `blocked`: the expected virtual environment is missing, inactive, or setup requires user approval, credentials, incompatible hardware, unavailable system packages, or manual action.
- `failed`: attempted setup or validation failed and AgentFix could not resolve it automatically.

## CUDA and Framework Guidance

- Treat GPU compatibility as evidence-driven:
  - Check repository docs and dependency pins first.
  - Check host GPU/driver only with read-only commands.
  - Match PyTorch/TensorFlow/JAX packages to the available driver/CUDA and the repo's supported Python version.
- Do not assume the newest framework version is correct.
- For old TensorFlow 1.x projects, prefer an isolated old-Python environment when feasible and document GPU limitations.
- For modern PyTorch projects on new GPUs, prefer official framework install selectors or documented wheel indexes; ask before changing major versions.
- For NumPy ABI failures, fix the smallest compatible pin and validate imports.

## Boundaries

Do:

- plan before installing
- verify commands target the repository-specific virtual environment before installing dependencies
- install all dependencies only into the environment selected or created by `repo-resource-prepare`
- prefer fast safe package mirrors such as Tsinghua mirrors when appropriate, using command-scoped options when possible
- reject generic/current workflow environments unless the user explicitly chose them for this repository
- ask before changing environments, installing outside the selected environment, using system packages, or changing major dependency versions beyond the selected minimum-reproduction requirements
- allow required official/trusted dependency downloads within the default 6 GB per-task budget when they preserve the paper-aligned baseline path
- ask before changing global pip/conda mirror configuration
- keep commands auditable and scoped to the selected environment
- invoke `agent-fix-error-recovery` automatically after setup or validation failures
- preserve scientific protocol and resource provenance
- scope the environment to the selected minimum reproduction and later optimization of that same code path

Do not:

- implement environment setup as a new Python or TypeScript pipeline
- download datasets or checkpoints; those belong to `repo-resource-prepare`
- run full baseline/training unless explicitly approved
- install optional full-paper or unrelated training dependencies merely because they appear elsewhere in the repository
- modify datasets, splits, metrics, evaluation scripts, or model logic
- delete or replace existing environments, files, or directories without explicit user approval
- hide environment failures by changing the benchmark command or success criterion
- hide environment or dependency cost by replacing a paper-aligned baseline with a weaker fallback when the required install is within the default 6 GB per-task budget
- silently install into or validate against the current active environment when it is not the repository-specific environment
- install dependencies into any environment other than the one selected during `repo-resource-prepare` without explicit user approval
- change package versions, framework wheel indexes, CUDA selectors, or experiment requirements only to make downloads faster
- silently modify global pip, conda, or system package-manager configuration
