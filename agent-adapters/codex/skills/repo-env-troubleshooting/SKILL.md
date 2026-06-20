---
name: repo-env-troubleshooting
description: Reference common virtual environment creation, activation, dependency installation, package mirror, CUDA/PyTorch/TensorFlow, and validation failures during repo-resource-prepare, repo-environment-setup, AgentInit, or AgentFix work. Use when Codex must diagnose or plan fixes for conda/venv creation problems, slow or failed package installs, Python version conflicts, dependency resolver errors, framework/GPU mismatches, absl --help false failures, NumPy ABI issues, or environment validation failures without changing experiment protocol.
---

# Repo Env Troubleshooting

Use this skill as a reference during `repo-resource-prepare`, `repo-environment-setup`, or `agent-fix-error-recovery` when the blocker is about virtual environments, dependencies, mirrors, or environment validation.

Do not use this skill to install dependencies by itself. The active stage still owns execution:

- `repo-resource-prepare` owns the user decision about current environment vs new repository-specific environment.
- `repo-environment-setup` owns dependency installation and validation inside the selected environment.
- `agent-fix-error-recovery` owns failure diagnosis and repair approval.

## Non-Negotiable Gate

Before any resource download or dependency download, confirm that the current user request explicitly chose one of:

- reuse the current active environment for this repository, or
- create/use a repository-specific conda/venv environment with a concrete name/path.

Old `config.yaml`, previous reports, or the active shell environment are not enough. If the choice is missing, stop and ask. Do not scan-download resources, install dependencies, or start package-manager downloads before this gate is satisfied.

## Common Cases

### Environment creation

- `conda create` is slow: prefer a user-approved fast mirror or command-scoped channel; do not change global `.condarc` without approval.
- Environment name already exists: record and reuse only if the user selected it for this repository; otherwise ask for a new name.
- Python version conflict: prefer the version required by repo docs or dependency pins; do not upgrade only for convenience.
- `venv` missing `pip`: bootstrap inside that venv only, or ask before switching managers.

### Activation and target environment

- Shell is not in the selected environment: do not install into the active shell by accident.
- Prefer scoped execution such as `conda run -n <env>` or `<venv>/bin/python` after user approval when the shell is not activated.
- Treat generic workflow envs such as `base`, `autosota`, or the Codex runtime env as unsafe unless the user explicitly chose them.

### Package mirrors and downloads

- Prefer command-scoped fast mirrors when safe, such as Tsinghua PyPI for pip.
- Do not change package versions, CUDA build selectors, or framework wheel indexes only for speed.
- Use official selectors/indexes when required for PyTorch, TensorFlow, JAX, CUDA wheels, or repo-documented commands.
- Ask before changing global pip/conda config.

### Dependency resolver failures

- Read explicit pins first.
- Prefer the smallest compatible pin change.
- For old repos, an older Python environment is often safer than upgrading old libraries.
- For `pip` resolver conflicts, inspect the conflict pair before relaxing constraints.

### CUDA and framework failures

- Check repo docs, Python version, GPU driver, and installed CUDA-visible framework versions.
- Do not assume newest PyTorch/TensorFlow is correct.
- For TensorFlow 1.x, prefer isolated old-Python CPU/GPU-compatible environments and document limitations.
- For PyTorch CUDA wheels, prefer the official wheel index unless the repo explicitly documents another source.

### NumPy ABI failures

- Symptoms include binary import errors, `numpy.dtype size changed`, or extension modules compiled against a different NumPy.
- Prefer pinning NumPy to the range expected by the framework or compiled extension.
- Validate by import checks, not by full baseline.

### Validation false failures

- Some `absl` apps print valid `--help` text and exit with code 1.
- Classify this as a validation-command issue when dependency imports pass and help text is complete.
- Replace with narrower import/entrypoint validation; do not mark environment failed only because of this convention.

## Risk Rules

Safe to do automatically when scoped to the selected environment:

- read-only diagnostics
- import checks
- command-scoped mirror use already approved by user policy
- creating missing cache/output dirs under the run directory

Ask before:

- creating/replacing/deleting environments
- installing or upgrading major frameworks
- changing Python/CUDA/framework versions
- changing global pip/conda config
- using unofficial mirrors not already approved
- editing source, datasets, metrics, or benchmark commands

## Reporting

When this skill informs a fix or setup decision, record a short note in the owning stage report:

- issue category
- evidence
- chosen fix or blocker
- whether user approval was required
- validation result
