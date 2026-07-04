---
name: repo-experiment-prepare
description: Inspect and modify a baseline-validated research codebase until it is ready for formal experiments without launching the full experiment run. Use after repo-baseline-run for either a specific paper or user-specified repository that must become ready for optimization experiments, or an open-ended research requirement whose selected repository must become ready to validate that requirement. This skill records the repository baseline state, maps research requirements to concrete files, functions, interfaces, benchmark rules, and experiment branches; identifies implementation, adapter, evaluation, configuration, and cross-repository integration gaps; makes approved protocol-preserving code changes; preserves the original baseline mode; configures baselines, controls, and ablations; dry-runs every branch; generates batch scripts; and writes method adaptation, experiment plan, matrix, and readiness artifacts. It never launches full formal experiments.
---

# Repo Experiment Prepare

Use this skill after a baseline has passed or produced an accepted local baseline. Turn a runnable baseline repository into an experiment-ready codebase; do not confuse baseline initialization with formal experiment readiness.

Read [references/experiment-readiness-criteria.md](references/experiment-readiness-criteria.md) before assessing gaps or declaring readiness. Apply its mode-specific checks, modification rules, validation requirements, README handoff requirements, and final gates.

Execute inspection, edits, and bounded validation interactively through Codex tool calls. Do not implement a separate Python or TypeScript orchestration pipeline.

## Terminal Output

Report only readiness mode, current phase, material decisions or approvals, artifact paths, dry-run summary, final status, and blockers. Put commands, diffs, code locations, provenance, logs, and detailed evidence in the stage reports.

## Agent Contract

Role: `AgentExperimentPrepare`

Primary deliverable:

- the actual repository codebase, configurations, formal experiment entrypoint, result summarizer when needed, and README instructions required to start the approved formal experiments

Inputs:

- primary runnable repository path and run directory
- repository-local `config.yaml`
- `resource_manifest.yaml` and environment artifacts
- `baseline_metrics.yaml` and `baseline_run_report.md`
- optional `paper_repo_resolution.md` or user-specified repository context
- for requirement validation: `research_scope.yaml`, `benchmark_plan.yaml`, `experiment_base_plan.yaml`, and `workspace_manifest.yaml`
- optional user optimization objective, method proposal, required comparisons, or protected paths

Required evidence artifacts:

- `method_adaptation_plan.yaml`
- `method_adaptation_report.md`
- `experiment_plan.yaml`
- `experiment_matrix.yaml`
- `experiment_readiness.yaml`
- `experiment_readiness_report.md`
- one platform-appropriate batch entrypoint such as `scripts/run_experiments.sh` or `scripts/run_experiments.ps1`
- a managed formal-experiment section in the primary repository README

Handoff:

- Report `status: ready_for_formal_run` only after directly checking the actual codebase and every readiness gate against real command and output evidence.
- Stop before starting full training, full evaluation, or a batch formal run.
- If an unexpected setup, build, import, test, baseline-regression, or dry-run command fails, invoke `agent-fix-error-recovery`.

## Workflow

1. Select the readiness mode.
   - Use `optimization` for a specific paper or user-specified repository.
   - Use `requirement_validation` for a repository selected from an open-ended research need.
   - In `optimization` mode, distinguish generic structural readiness from method-specific readiness. If the requested optimization objective is missing or materially ambiguous, inspect the codebase but record `needs_user_decision`; do not invent a scientific optimization target.
   - In `requirement_validation` mode, treat `research_scope.yaml` and `benchmark_plan.yaml` as authoritative for the intended claim and protocol.

2. Freeze the starting point.
   - Record repository path, remote, branch, exact baseline commit, submodule or component commits, and current dirty paths.
   - Record the accepted baseline command, environment, resources, metric evidence, and output paths.
   - Preserve user changes. Do not commit, checkout, reset, clean, overwrite, or discard files.
   - If required edits overlap unexplained existing changes, stop and ask before editing those paths.

3. Build requirement-to-code traceability.
   - Map each optimization or research requirement to benchmark clauses, repository or component roles, concrete files, functions, classes, commands, configuration fields, experiment branches, and required evidence.
   - Inspect actual source and interfaces; do not rely only on README claims or planned integration notes.
   - For composed workspaces, record every cross-repository interface and provenance boundary.

4. Classify readiness gaps.
   - Use one or more categories: `configuration_gap`, `data_adapter_gap`, `evaluation_gap`, `method_implementation_gap`, `cross_repo_integration_gap`, `protocol_decision_gap`, or `resource_or_environment_gap`.
   - Distinguish missing implementation from runtime defects.
   - Write `method_adaptation_plan.yaml` before material code changes. Include current behavior, target behavior, files and symbols, invariants, approval state, implementation steps, and validation plan.

5. Resolve decisions and approval gates.
   - Proceed without repeated approval for small, reversible, protocol-preserving edits directly required by the already approved optimization goal or research scope.
   - Ask before changing the scientific claim, labels, population, split semantics, primary metrics, evaluation timing, model objective, major architecture, major dependency/CUDA stack, or resource class.
   - Ask before copying or merging code with unclear license/provenance, replacing existing implementations, destructive operations, or high-cost validation.
   - Record decisions in the plan and report; never encode an unresolved scientific choice as an implementation assumption.

6. Implement the missing experiment capability.
   - Prefer adapters, wrappers, explicit interfaces, configuration, and isolated modules over copying or entangling repositories.
   - Preserve an explicit original-baseline mode and its command path.
   - Keep benchmark fairness invariants unchanged unless the user approves a new benchmark version.
   - Record imported code or design provenance, source URL, commit, license, and local integration point.
   - Make small reviewable changes and add focused tests or fixtures where they materially protect the new interface.
   - Update `method_adaptation_report.md` with actual files, symbols, behavior changes, deviations from plan, and verification evidence.

7. Freeze the formal experiment design.
   - Write `experiment_plan.yaml` with dataset/version, splits, preprocessing boundary, inputs, targets, horizons, metrics, aggregation, seeds, tuning policy, compute budget, checkpoint rule, and output layout.
   - Keep baseline, proposed method, controls, and ablations under the same benchmark and evaluation contract.
   - Write `experiment_matrix.yaml` with one entry per formal branch, including purpose, config, command, expected outputs, resource estimate, and dry-run command.
   - Separate smoke parameters from formal parameters so dry-run reductions cannot silently alter the formal plan.

8. Validate the prepared codebase.
   - Run relevant static checks, imports, compilation, unit or interface tests, and tiny fixtures.
   - Revalidate the preserved original-baseline mode after the code changes through the cheapest scientifically faithful regression path. Save the command and a non-empty evidence file; an unchanged old artifact checksum is not a post-change regression.
   - Run a bounded dry run for every formal experiment branch through the same code path used by its formal command.
   - Save a non-empty dry-run evidence file for every matrix branch and set its status from execution evidence, not from planned intent.
   - Validate metric parsing, output isolation, checkpoint creation or loading, resume behavior when relevant, and generated configuration resolution.
   - Invoke `agent-fix-error-recovery` for unexpected command failures, then return to this stage. Keep intended method development and experiment design in this skill.

9. Generate batch entrypoints without running them.
   - Generate a platform-appropriate batch script from `experiment_matrix.yaml`.
   - Make environment targeting, working directory, config, output directory, and failure behavior explicit.
   - Add a clearly documented dry-run or print-only mode when practical.
   - Check script syntax and command expansion without launching full formal experiments.
   - Add or update a managed `## Formal Experiments` section in the primary repository README between `<!-- kaivu-formal-experiment:start -->` and `<!-- kaivu-formal-experiment:end -->`.
   - Include prerequisites, environment activation, working directory, the exact guarded formal command, matrix scope, output locations, result summarization, and the fact that formal execution has not started.
   - Preserve all README content outside the managed markers.

10. Decide readiness.
    - Write `experiment_readiness.yaml` and `experiment_readiness_report.md`.
    - Use `ready_for_formal_run`, `needs_user_decision`, `needs_implementation`, or `blocked`.
    - Mark `ready_for_formal_run` only when requirement traceability is complete, implementation is finished, the baseline mode is preserved through post-change regression, the protocol and matrix are frozen, every branch passes its dry run with evidence, batch scripts and README instructions are validated, and no scientific decision remains open.
    - Re-read the modified source, formal configurations, launcher, README, matrix, readiness artifacts, baseline-regression evidence, and dry-run evidence before deciding.
    - Confirm that recorded commands are the commands actually executed and that expected outputs exist and are parseable.
    - If any required code, command, output, evidence, or decision is missing, use `needs_user_decision`, `needs_implementation`, or `blocked`; do not let self-reported YAML fields override the observed codebase state.

11. Hand off the formal command.
    - In the final user-facing response, state that formal experiments have not started.
    - Give the exact repository path, environment, formal command copied from `experiment_readiness.yaml`, output location, and summarizer command when one exists.
    - Point the user to the managed README section and readiness artifacts.

## Artifact Shapes

### `method_adaptation_plan.yaml`

```yaml
readiness_mode: "optimization" # optimization | requirement_validation
status: "planned" # planned | needs_user_decision | in_progress | implemented | blocked
repo_path: ""
baseline_state:
  remote: ""
  branch: ""
  commit: ""
  dirty_paths: []
  baseline_command: ""
  baseline_metrics_path: ""
authoritative_inputs:
  research_scope_path: ""
  benchmark_plan_path: ""
  experiment_base_plan_path: ""
requirements:
  - id: ""
    statement: ""
    benchmark_clauses: []
    repositories: []
    code_locations: []
    experiment_branches: []
    evidence_required: []
gaps:
  - id: ""
    category: "method_implementation_gap"
    current_behavior: ""
    target_behavior: ""
    files_and_symbols: []
    protocol_invariants: []
    implementation_steps: []
    approval_required: false
    approval_status: "not_required"
validation_plan: []
```

### `experiment_plan.yaml`

```yaml
readiness_mode: "optimization"
objective: ""
benchmark_plan_path: ""
method_adaptation_plan_path: ""
protocol:
  datasets: []
  split_definition: ""
  preprocessing_boundary: ""
  inputs: []
  targets: []
  horizons: []
  primary_metrics: []
  secondary_metrics: []
  metric_aggregation: ""
  seeds: []
  tuning_policy: ""
  compute_budget: ""
  checkpoint_rule: ""
  output_layout: ""
fairness_invariants: []
matrix_requirements:
  required_branch_kinds: ["baseline", "proposed"]
  require_all_branches_dry_run: true
formal_run_requires_user_approval: true
```

### `experiment_matrix.yaml`

```yaml
branches:
  - id: ""
    kind: "baseline" # baseline | proposed | control | ablation
    purpose: ""
    config: ""
    formal_command: ""
    dry_run_command: ""
    expected_outputs: []
    resource_estimate: {}
    implementation_status: "ready"
    dry_run_status: "passed"
    dry_run_evidence: ""
```

### `experiment_readiness.yaml`

```yaml
status: "ready_for_formal_run" # ready_for_formal_run | needs_user_decision | needs_implementation | blocked
readiness_mode: "optimization" # optimization | requirement_validation
repo_path: ""
baseline_commit: ""
checks:
  requirement_traceability: "passed"
  implementation_complete: "passed"
  baseline_mode_preserved: "passed"
  benchmark_protocol_frozen: "passed"
  experiment_matrix_complete: "passed"
  all_branches_dry_run: "passed"
  batch_entrypoint_validated: "passed"
  readme_instructions_written: "passed"
  approvals_resolved: "passed"
baseline_regression:
  status: "passed"
  executed_after_changes: true
  command: ""
  evidence_path: ""
artifacts:
  method_adaptation_plan: "method_adaptation_plan.yaml"
  method_adaptation_report: "method_adaptation_report.md"
  experiment_plan: "experiment_plan.yaml"
  experiment_matrix: "experiment_matrix.yaml"
  experiment_readiness_report: "experiment_readiness_report.md"
  batch_entrypoint: ""
  readme: ""
formal_run:
  launcher_path: ""
  command: ""
  summarizer_command: ""
  readme_path: ""
  instructions_written: true
remaining_blockers: []
formal_run_started: false
```

## Decision Rules

- A passing baseline is an input to this stage, not evidence that the codebase is experiment-ready.
- Do not claim method-specific optimization readiness without an optimization goal.
- Do not claim requirement-validation readiness unless every research requirement maps to implemented code and a benchmark-preserving experiment branch.
- Treat successful command exit as one piece of evidence; verify outputs, metrics, code paths, and artifact traceability.
- Treat artifact fields as summaries of observed code and command evidence, never as substitutes for direct inspection and execution.
- Never interpret dry-run metrics as scientific findings.

## Boundaries

Do:

- inspect and modify experiment code inside the approved workspace
- implement adapters, methods, evaluation hooks, configurations, and cross-repository interfaces required by the approved goal
- preserve and regression-check the original baseline mode
- configure and dry-run every formal branch
- generate but not launch formal batch scripts
- document the exact formal command in the repository README and final response

Do not:

- invent missing research or optimization objectives
- silently change benchmark invariants or scientific meaning
- discard user changes or use destructive Git operations
- copy code without provenance and license review
- launch full formal experiments
- mark readiness from artifact fields without checking the actual codebase and commands
