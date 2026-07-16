---
name: agent-fix-error-recovery
description: Automatically diagnose and recover from unexpected failures during repo-experiment-fix, resource preparation, environment setup, validation, or minimum-reproduction baseline execution. Apply the smallest protocol-preserving low-risk fix, ask only before risky, expensive, destructive, or scientifically meaningful actions, verify the result, and return to the failed stage. Use for tracebacks, nonzero exits, timeouts, missing resources, dependency or CUDA/framework conflicts, path errors, OOM, build failures, interface errors, and metric parsing failures. Planned source adaptation and repository integration belong to repo-experiment-fix, not AgentFix.
---

# Agent Fix Error Recovery

Use this skill automatically when another stage fails and AgentFix must turn the error into a concrete recovery action.

The user should not need to ask for this skill explicitly during the paper-repo workflow. When a preceding stage fails, switch into AgentFix, load this skill, diagnose the failure, and proceed according to the risk rules below. Ask the user only when a proposed action is not clearly low-risk.

The agent does the diagnosis and repair directly. Do not implement a separate Python or TypeScript repair pipeline.

For difficult or repeated failures, consult `agent-fix-knowledge-base` before proposing a repair. For virtual environment, dependency, mirror, CUDA/framework, NumPy ABI, or validation-command failures, also consult `repo-env-troubleshooting` as a focused reference.

## Artifact Location

Use the calling stage's `artifact_root`, or default to `<run_dir>/experiment_artifacts/`. Write fix reports under `reports/`, diagnostic evidence under `evidence/`, and detailed command output under `logs/`. Do not place recovery reports or logs in the repository root.

## Terminal Output

Keep terminal-facing progress concise. Report only the failure category, whether a safe fix was applied, whether user approval is needed, verification status, artifact path, and next step. Do not print command strings, full command lists, stdout/stderr blocks, file content snippets, or diffs unless the user explicitly asks. Put detailed error excerpts, commands, and logs in the fix report.

## Agent Contract

Role: `AgentFix`

Inputs:

- failed stage: repo_experiment_fix, resource, environment, validation, baseline, optimization_experiment, or unknown
- failed command and working directory
- stdout/stderr/traceback/log excerpt
- repository path and run directory
- current `config.yaml`, manifests, setup plans, and previous fix attempts when available
- user policy such as allow downloads, allow dependency installs, allowed environment name, or protected paths

Default size policy:

- Unless the user provides a stricter limit, downloads or dependency installs up to about 6 GB of new local data for the current reproduction task are acceptable when they are official/trusted, required by the selected baseline, and scoped to the approved run/resource/environment roots.
- If the user has explicitly selected or created a repository-specific environment for this run, dependency fixes required for the selected minimum reproduction may be installed into that environment without asking again for each ordinary package-manager command.
- Do not downgrade the scientific path, replace the official method, or switch to a weaker fallback solely because a required package/resource is several GB but within this default budget.
- Ask before exceeding 6 GB, using credentialed/license-gated resources, using untrusted mirrors, changing global package-manager configuration, installing outside the approved environment, or making scientifically meaningful protocol changes.

Outputs:

- diagnosis
- fix plan
- actions executed automatically, if any
- actions requiring user approval, if any
- verification result
- updated report such as `<artifact_root>/reports/agent_fix_report.md` or a stage-specific fix note

## Workflow

1. Reconstruct the failure.
   - Identify the failed stage, command, working directory, expected output, return code, and relevant log excerpt.
   - Read nearby config/report files only as needed: `research_requirement.yaml`, `experiment_repo_plan.yaml`, `repo_experiment_fix.yaml`, `config.yaml`, `resource_manifest.yaml`, `resource_acquisition_report.md`, `environment_plan.yaml`, `onboard_report.md`, `baseline_metrics.yaml`, and previous fix notes.
   - Preserve the original error text in the report.
   - If the failure is non-trivial or resembles a prior repeated issue, consult `agent-fix-knowledge-base` and record any matched case in the report.

2. Classify the failure.
   - Use one primary category:
     - `missing_resource`
     - `download_failure`
     - `package_missing`
     - `package_version_conflict`
     - `python_version_mismatch`
     - `cuda_pytorch_mismatch`
     - `tensorflow_version_mismatch`
     - `numpy_abi_mismatch`
     - `path_error`
     - `permission_error`
     - `gpu_oom`
     - `command_error`
     - `build_or_test_failure`
     - `interface_mismatch`
     - `baseline_regression`
     - `metric_parse_error`
     - `timeout`
     - `unknown`
   - Prefer the smallest concrete blocker over broad explanations.

3. Decide whether the fix is safe to execute automatically.
   - Execute only low-risk fixes listed in the automatic-safe matrix below.
   - Ask the user before any medium/high-risk fix.
   - If unsure, ask.
   - Do not ask just to start diagnosis or to run read-only checks.
   - If the failure reveals missing planned functionality, an incomplete repository integration, or a requirement-to-code gap, return it to `repo-experiment-fix`; do not disguise intended development as error recovery.

4. Apply the fix when allowed.
   - Run the smallest command or edit needed.
   - Keep changes outside protected paths unless the user explicitly approves.
   - Do not change datasets, labels, splits, metrics, evaluation scripts, model architecture, or experiment logic.
   - Do not run destructive git commands.

5. Verify.
   - Re-run the failed command only when it is cheap and within the current stage boundary.
   - Otherwise run a narrower validation, such as file existence, import check, command `--help`, checksum, archive listing, or symlink resolution.
   - Record whether the fix resolved the original blocker, exposed a new blocker, or requires user action.

6. Report.
   - Write or update `<artifact_root>/reports/agent_fix_report.md` when an artifact root or run directory exists.
   - Include diagnosis, risk level, automatic actions, proposed actions needing approval, verification result, and next step.
   - If the fix resolves a difficult reusable issue, append a compact lesson to the active run report. Promote it to the shared `agent-fix-knowledge-base` only when the user explicitly asks.

## Automatic-Safe Fixes

AgentFix may execute these without asking when they are clearly limited to the current workspace/run directory:

- create a missing run/output/cache directory
- retry an interrupted download with resume flags when the URL was already approved
- re-run an idempotent extraction into an approved resource directory
- replace a broken symlink when both source and target are inside the approved repo/run/resource roots
- create a symlink from an expected repo path to an already staged resource when the expected path does not exist
- set non-destructive environment variables for the current command only, such as `CUDA_VISIBLE_DEVICES`, `TOKENIZERS_PARALLELISM=false`, or cache directories under the run directory
- run read-only diagnostics such as `python --version`, `pip show`, `conda env list`, `nvidia-smi`, `du`, `file`, `tar -tf`, `sha256sum`, `ldd`, or import checks
- install a clearly missing lightweight Python package into an already user-approved active environment only when the project docs or config explicitly name it and the package is not a major framework
- install a documented or directly required dependency, including a major framework, into the already selected repository-specific environment when it is needed for the selected minimum reproduction and remains within the default 6 GB per-task budget
- rerun a failed command with a corrected working directory when the command path was obviously wrong and no files are modified

## Ask Before Fixes

Ask the user before:

- downloading files or installing dependencies expected to exceed the default 6 GB per-task budget, or any credential/license-gated resource
- installing or upgrading major frameworks such as PyTorch, TensorFlow, CUDA, JAX, RAPIDS, faiss, or AutoGluon when they are not required by the selected minimum reproduction, exceed the default budget, or would install outside the approved environment
- installing system packages
- creating, deleting, or replacing conda/venv environments
- changing Python, CUDA, compiler, driver, or system library versions
- editing source code, evaluation scripts, metrics, dataset loaders, or configs that affect protocol
- replacing an existing regular file or directory
- using third-party mirrors or unofficial resources
- running long training/evaluation commands
- changing batch size, sample count, seeds, precision, dataset subset, timeout, or GPU selection when it may affect reported metrics
- any destructive operation, including `rm -rf`, `git reset`, `git clean`, `git checkout`, or moving user data

## Never Do

- Do not modify datasets, labels, train/test splits, metric computation, or protected files without explicit user approval.
- Do not hide a failed fix by changing the success criterion.
- Do not replace a paper-aligned baseline with a weaker fallback only because a required official/trusted dependency or resource is several GB but within the default 6 GB per-task budget.
- Do not mark a scientific result fixed unless the original command or an agreed validation command passes.
- Do not delete partial downloads or generated outputs unless the user approves or they are inside a clearly named temporary path created by this fix attempt.
- Do not keep trying the same failed fix. After two failed attempts, stop and ask with the evidence.

## Fix Report Shape

Use this shape for `agent_fix_report.md`:

```markdown
# AgentFix Report

## Failure
- Stage:
- Command:
- Working directory:
- Return code:
- Error summary:

## Diagnosis
- Category:
- Root cause:
- Confidence:

## Actions
| Action | Risk | Executed | Result | Notes |
|---|---|---:|---|---|

## Verification
- Command/check:
- Result:
- Remaining blockers:

## User Decisions Needed
- ...
```

## Handoff

- If fixed, return to the stage that failed and rerun or continue.
- If diagnosis reveals an implementation, integration, or requirement-fit gap, return to `repo-experiment-fix` with the evidence and required change, then repeat affected downstream stages.
- If blocked by user approval, stop with the exact approval question and proposed command/action.
- If a new blocker appears, classify it and either apply another safe fix or ask.
