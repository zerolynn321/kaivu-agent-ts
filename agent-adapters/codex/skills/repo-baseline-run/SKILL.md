---
name: repo-baseline-run
description: Interactively run and record the configured baseline or evaluation command for a prepared research repository. Use after repo-onboard, repo-resource-prepare, and repo-environment-setup have produced config.yaml, resource manifests, and a ready environment; when Codex acting as AgentBaseline must verify readiness, ask before long or risky baseline execution, run the baseline only inside the environment selected by resource preparation, parse primary metrics, compare with documented baselines when available, write baseline_metrics.yaml and baseline_run_report.md, and automatically invoke AgentFix when baseline execution, metric parsing, path binding, or runtime validation fails.
---

# Repo Baseline Run

Use this skill after resource and environment preparation when AgentBaseline must run the repository's configured baseline/eval command and record the result.

The agent runs the baseline directly through Codex tool calls. Do not implement a separate Python or TypeScript baseline runner.

## Terminal Output

Keep terminal-facing progress concise. Report only readiness status, approval needs, baseline result, metric summary, artifact paths, blockers, and next step. Do not print command strings, full command lists, stdout/stderr blocks, file content snippets, or diffs unless the user explicitly asks. Put detailed commands, logs, metric evidence, and comparisons in the baseline report.

## Agent Contract

Role: `AgentBaseline`

Inputs:

- cloned repository path
- run directory
- repository-local `config.yaml`
- `<run_dir>/resource_manifest.yaml`
- `<run_dir>/resource_acquisition_report.md`
- `<run_dir>/environment_plan.yaml`
- `<run_dir>/environment_setup_report.md`
- optional user approval for long/full evaluation
- optional user override for baseline command, timeout, metric parser, or expected metric

Required outputs:

- `<run_dir>/baseline_metrics.yaml`
- `<run_dir>/baseline_run_report.md`

Optional outputs:

- small updates to `<repo>/config.yaml` baseline metadata only

Handoff:

- If the baseline passes, hand off to experiment/optimization stages.
- If baseline execution, metric parsing, or validation fails, automatically invoke `agent-fix-error-recovery` with the failed command, stdout/stderr, repo path, run directory, baseline report, and prior stage reports.

## Workflow

1. Confirm readiness.
   - Read `<repo>/config.yaml`.
   - Read resource and environment reports.
   - Confirm required resources are available.
   - Confirm environment status is `ready` or explicitly accepted by the user.
   - Confirm the baseline command, primary metric, metric direction, pre-eval commands, timeout, and expected/documented baseline when present.
   - If required resources or environment are blocked, do not run baseline. Write a blocked report and hand off to the appropriate previous stage.

2. Confirm environment targeting.
   - Run baseline only inside the environment selected or created by `repo-resource-prepare`.
   - Never run baseline in a different active environment unless the user explicitly changes the environment policy.
   - If the current shell is not inside the selected environment, ask the user to activate it or approve a scoped execution method such as `conda run -n <env>` or `<venv>/bin/python`.

3. Build the baseline plan.
   - Use the configured `baseline.command` when present; otherwise use `eval_command`.
   - Include pre-eval commands only when they are already configured and needed.
   - Preserve the scientific protocol: do not change datasets, splits, metric computation, model architecture, seed, sample count, precision, batch size, or command flags unless the user explicitly approves a protocol change.
   - Decide whether the command is cheap smoke/baseline or long/full evaluation.

4. Ask before execution when needed.
   - Ask before running long/full evaluation, GPU-heavy commands, expensive commands, or commands with unclear runtime.
   - Ask before changing timeout, GPU selection, batch size, seed, precision, dataset subset, or checkpoint.
   - Ask before running any command that may overwrite existing results.
   - Cheap configured smoke/baseline commands may run without extra approval when resources and environment are ready and the command is already in `config.yaml`.

5. Run baseline.
   - Execute in the repository root unless config evidence says otherwise.
   - Keep outputs under the run directory when configurable.
   - Capture return code, elapsed time, stdout/stderr excerpts, and produced metric/result files.
   - Do not commit, tag, reset, clean, or mutate experiment logic.

6. Parse metrics.
   - Parse the configured primary metric first.
   - Capture additional printed or file-written metrics when obvious.
   - If no numeric metric exists, record a success criterion such as command completion or generated artifact presence.
   - Compare with documented baseline values when available and record `matches`, `better`, `worse`, or `not_available`.
   - Do not change success criteria after seeing a failure.

7. Handle failure.
   - If the command exits nonzero, times out, cannot find resources, uses the wrong environment, or metrics cannot be parsed, automatically invoke `agent-fix-error-recovery`.
   - Let AgentFix apply only low-risk repairs automatically.
   - Ask before any protocol-affecting change or long rerun.
   - After AgentFix resolves the issue, rerun the same baseline command unless the user approved a changed command.

8. Write reports.
   - Write `<run_dir>/baseline_metrics.yaml`.
   - Write `<run_dir>/baseline_run_report.md`.
   - If useful, update `<repo>/config.yaml` baseline metadata only.
   - Re-read outputs and report final status: `passed`, `failed`, `blocked`, or `partial`.

## Metrics Shape

Use this shape for `baseline_metrics.yaml`:

```yaml
repo_path: ""
run_dir: ""
status: "not_run" # passed | failed | blocked | partial | not_run
environment:
  manager: ""
  name: ""
  path: ""
command: ""
pre_eval_commands: []
returncode:
elapsed_seconds:
primary_metric: ""
primary_metric_value:
metric_direction: "unknown" # higher | lower | unknown
metrics: {}
documented_baseline: {}
comparison: "not_available" # matches | better | worse | not_available
log_path: ""
result_files: []
agentfix_invoked: false
notes: ""
```

Use this shape for `baseline_run_report.md`:

```markdown
# Baseline Run Report

## Summary
- Status:
- Environment:
- Command source:
- Primary metric:
- Comparison:

## Readiness
| Check | Status | Notes |
|---|---|---|

## Result
| Metric | Value | Direction | Documented baseline | Comparison |
|---|---:|---|---:|---|

## AgentFix
- Invoked:
- Outcome:

## Remaining Blockers
- ...
```

## Decision Rules

- `passed`: baseline command exits successfully and the primary metric or success criterion is captured.
- `partial`: command succeeds but metric extraction is incomplete or comparison is unavailable.
- `failed`: command fails, times out, or metric comparison is clearly worse than a documented baseline beyond known tolerance.
- `blocked`: required resources, environment, approval, or credentials are missing.

## Boundaries

Do:

- run only the configured baseline/eval command or a user-approved override
- run inside the environment selected by `repo-resource-prepare`
- preserve resource paths and scientific protocol
- parse and record metrics
- compare with documented baselines when available
- invoke `agent-fix-error-recovery` automatically on failures

Do not:

- implement baseline execution as a new Python or TypeScript pipeline
- install dependencies or download resources; those belong to earlier stages
- modify datasets, splits, metrics, model logic, or evaluation protocol without explicit approval
- run long/full evaluation without approval
- change command flags to make a failing result look successful
- write results outside the run directory unless the repository requires it and the user approves
- run git commit, tag, checkout, reset, clean, or destructive file operations
