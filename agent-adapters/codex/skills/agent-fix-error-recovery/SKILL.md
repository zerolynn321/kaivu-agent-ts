---
name: agent-fix-error-recovery
description: Automatically invoke AgentFix error recovery when resource download, dependency installation, environment setup, validation, baseline evaluation, or experiment runs fail; diagnose the error, propose the smallest protocol-preserving fix, automatically execute common low-risk fixes, and ask the user only before risky, expensive, destructive, or scientifically meaningful changes. Use when Codex receives stderr/stdout, a failed command, traceback, nonzero exit code, timeout, missing resource error, package conflict, CUDA/PyTorch/TensorFlow mismatch, path error, GPU OOM, metric parsing failure, or failed baseline/experiment during the paper-repo workflow.
---

# Agent Fix Error Recovery

Use this skill automatically when another stage fails and AgentFix must turn the error into a concrete recovery action.

The user should not need to ask for this skill explicitly during the paper-repo workflow. When a preceding stage fails, switch into AgentFix, load this skill, diagnose the failure, and proceed according to the risk rules below. Ask the user only when a proposed action is not clearly low-risk.

The agent does the diagnosis and repair directly. Do not implement a separate Python or TypeScript repair pipeline.

## Agent Contract

Role: `AgentFix`

Inputs:

- failed stage: resource, environment, validation, baseline, experiment, or unknown
- failed command and working directory
- stdout/stderr/traceback/log excerpt
- repository path and run directory
- current `config.yaml`, manifests, setup plans, and previous fix attempts when available
- user policy such as allow downloads, allow dependency installs, allowed environment name, or protected paths

Outputs:

- diagnosis
- fix plan
- actions executed automatically, if any
- actions requiring user approval, if any
- verification result
- updated report such as `<run_dir>/agent_fix_report.md` or a stage-specific fix note

## Workflow

1. Reconstruct the failure.
   - Identify the failed stage, command, working directory, expected output, return code, and relevant log excerpt.
   - Read nearby config/report files only as needed: `config.yaml`, `resource_manifest.yaml`, `resource_acquisition_report.md`, `environment_plan.yaml`, `onboard_report.md`, and previous fix notes.
   - Preserve the original error text in the report.

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
     - `metric_parse_error`
     - `timeout`
     - `unknown`
   - Prefer the smallest concrete blocker over broad explanations.

3. Decide whether the fix is safe to execute automatically.
   - Execute only low-risk fixes listed in the automatic-safe matrix below.
   - Ask the user before any medium/high-risk fix.
   - If unsure, ask.
   - Do not ask just to start diagnosis or to run read-only checks.

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
   - Write or update an `agent_fix_report.md` in the run directory when a run directory exists.
   - Include diagnosis, risk level, automatic actions, proposed actions needing approval, verification result, and next step.

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
- rerun a failed command with a corrected working directory when the command path was obviously wrong and no files are modified

## Ask Before Fixes

Ask the user before:

- downloading large files or any credential/license-gated resource
- installing or upgrading major frameworks such as PyTorch, TensorFlow, CUDA, JAX, RAPIDS, faiss, AutoGluon, or system packages
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
- If blocked by user approval, stop with the exact approval question and proposed command/action.
- If a new blocker appears, classify it and either apply another safe fix or ask.
