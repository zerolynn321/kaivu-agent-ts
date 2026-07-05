---
name: repo-experiment-prepare
description: Inspect and modify a baseline-validated research codebase until it is ready for formal experiments on the current machine without launching them. Use after repo-baseline-run for a paper/repository needing optimization experiments or a selected repository that must validate an open-ended requirement. This skill maps requirements to code and experiment branches; implements configuration, adapter, evaluation, and method gaps; turns composed workspaces into one locally complete codebase with explicit component interfaces, a unified root entrypoint and control plane, and real end-to-end dataflow; preserves the baseline; dry-runs all branches; generates launch, summary, and README instructions; and writes a consolidated human-readable experiment_readiness_report.md. It does not require Git initialization, commits, tracked files, or clean-clone reconstruction.
---

# Repo Experiment Prepare

Use this skill after a baseline has passed or produced an accepted local baseline. Turn a runnable baseline repository into an experiment-ready codebase; do not confuse baseline initialization with formal experiment readiness.

Read [references/experiment-readiness-criteria.md](references/experiment-readiness-criteria.md) before assessing gaps or declaring readiness. Apply its mode-specific checks, modification rules, validation requirements, README handoff requirements, and final gates.

Execute inspection, edits, and bounded validation interactively through Codex tool calls. Do not implement a separate Python or TypeScript orchestration pipeline.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<repo>/experiment_artifacts/`. Write method and experiment plans/matrices under `plans/`, readiness state under `manifests/`, human-readable reports under `reports/`, validation artifacts under `evidence/`, and command output under `logs/`. Do not place these auxiliary files in the repository root. Keep source code, `README.md`, formal runtime configs, launchers, summarizers, dependency definitions, and result directories in the normal codebase structure. Bare artifact filenames below refer to their categorized path under `artifact_root`. For an existing cluttered repository, inventory root-level auxiliary artifacts, move them into the categorized layout when safe, update all references and commands, and avoid keeping duplicate authoritative copies.

## Terminal Output

Report only readiness mode, current phase, material decisions or approvals, artifact paths, dry-run summary, final status, and blockers. Put commands, diffs, code locations, provenance, logs, and detailed evidence in the stage reports.

## Agent Contract

Role: `AgentExperimentPrepare`

Primary deliverable:

- the actual repository codebase, configurations, formal experiment entrypoint, result summarizer when needed, and README instructions required to start the approved formal experiments
- for multi-repository solutions, one locally complete experiment workspace whose root entrypoint can run the connected workflow without manual cross-component handoffs or missing source trees
- `<artifact_root>/reports/experiment_readiness_report.md` as the single consolidated human-readable explanation of what changed, where it changed, why it satisfies the requirement, and how to run the formal experiments

Inputs:

- primary runnable repository path and run directory
- `<artifact_root>/manifests/config.yaml`
- `<artifact_root>/manifests/resource_manifest.yaml` and environment artifacts
- `<artifact_root>/manifests/baseline_metrics.yaml` and `<artifact_root>/reports/baseline_run_report.md`
- optional `paper_repo_resolution.md` or user-specified repository context
- for requirement validation: `research_scope.yaml`, `benchmark_plan.yaml`, `experiment_base_plan.yaml`, and `workspace_manifest.yaml`
- optional user optimization objective, method proposal, required comparisons, or protected paths

Required evidence artifacts:

- `method_adaptation_plan.yaml`
- `method_adaptation_report.md`
- `experiment_plan.yaml`
- `experiment_matrix.yaml`
- `experiment_readiness.yaml`
- one platform-appropriate batch entrypoint such as `scripts/run_experiments.sh` or `scripts/run_experiments.ps1`
- a managed formal-experiment section in the primary repository README

Handoff:

- Report `status: ready_for_formal_run` only after directly checking the actual codebase and every readiness gate against real command and output evidence.
- Stop before starting full training, full evaluation, or a batch formal run.
- If an unexpected setup, build, import, test, baseline-regression, or dry-run command fails, invoke `agent-fix-error-recovery`.

## Re-entry and Idempotency

Treat an existing `ready_for_formal_run` codebase as a re-validation task, not a new preparation run.

Before planning edits:

1. Read the existing readiness manifest, human report, formal plan/matrix, README instructions, and recorded validation evidence.
2. Check whether the research requirement, benchmark contract, relevant source/configuration, environment/resource identity, launcher, or expected outputs changed after the recorded validation. Use an existing protocol lock, checksums, or explicit file inventory when available; do not add a new tracking mechanism merely because the skill was invoked again.
3. Run only cheap read-only checks needed to confirm the formal command and required paths still resolve. A print-only/preflight command is allowed when it does not train, fit a graph, overwrite evidence, or create formal results.
4. If nothing relevant changed and existing evidence is complete and readable, make no file changes, do not archive or regenerate evidence, do not rerun baseline or smoke training, preserve `ready_for_formal_run`, and report that the codebase was already ready.

Reopen preparation only when concrete evidence shows at least one existing readiness gate is no longer satisfied, for example:

- an authoritative requirement or benchmark decision changed;
- relevant experiment source, configuration, environment, resource identity, or launcher changed after validation;
- a required artifact or command is missing, corrupt, or no longer resolves;
- a bounded preflight fails;
- inspected code proves an existing correctness, leakage, branch-wiring, result-isolation, or unsafe-resume defect.

Do not reopen readiness merely to add optional hardening, newer conventions, extra tests, stronger documentation, refactoring, or a newly imagined best practice. When reopening, state exactly which prior gate is invalid and why. Reuse unaffected evidence and rerun only the baseline path or experiment branches affected by the change.

Idempotency requirement: invoking this skill twice on an unchanged ready codebase must produce no source/configuration changes and no training runs on the second invocation.

## Workflow

1. Select the readiness mode.
   - Apply the re-entry check first. Continue through the preparation workflow only for a new/incomplete codebase or after a prior readiness gate is concretely invalidated.
   - Use `optimization` for a specific paper or user-specified repository.
   - Use `requirement_validation` for a repository selected from an open-ended research need.
   - In `optimization` mode, distinguish generic structural readiness from method-specific readiness. If the requested optimization objective is missing or materially ambiguous, inspect the codebase but record `needs_user_decision`; do not invent a scientific optimization target.
   - In `requirement_validation` mode, treat `research_scope.yaml` and `benchmark_plan.yaml` as authoritative for the intended claim and protocol.

2. Freeze the starting point.
   - Record the repository/workspace path and, when already available, remotes, branches, commits, and dirty paths as provenance only. Missing Git metadata is not a readiness gap.
   - Record the accepted baseline command, environment, resources, metric evidence, and output paths.
   - Preserve user changes. Do not initialize Git, stage files, commit, configure author identity, checkout, reset, clean, overwrite, remove nested Git metadata, or discard files merely to satisfy readiness.
   - If required edits overlap unexplained existing changes, stop and ask before editing those paths.

3. Build requirement-to-code traceability.
   - Map each optimization or research requirement to benchmark clauses, repository or component roles, concrete files, functions, classes, commands, configuration fields, experiment branches, and required evidence.
   - Inspect actual source and interfaces; do not rely only on README claims or planned integration notes.
   - For composed workspaces, record every cross-repository interface and provenance boundary.

4. Classify readiness gaps.
   - Use one or more categories: `configuration_gap`, `data_adapter_gap`, `evaluation_gap`, `method_implementation_gap`, `cross_repo_integration_gap`, `workspace_completeness_gap`, `protocol_decision_gap`, or `resource_or_environment_gap`.
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

7. Integrate a multi-repository solution into one coherent experiment codebase.
   - Apply this step whenever the runnable solution depends on more than one source repository or a composed workspace.
   - First define the integrated architecture: the primary package/root, each component's role, the module boundaries, the complete scientific dataflow, and the one user-facing formal experiment entrypoint.
   - Connect components through explicit in-code interfaces. Specify input/output schemas, shapes, dtypes, variable ordering, split and normalization boundaries, artifact formats, error behavior, and provenance. Do not treat shell scripts that manually copy files between unchanged repositories as integration.
   - Make the root entrypoint execute the complete required workflow. For a staged workflow, it must produce each upstream artifact, validate it, pass it to the downstream stage, and retain traceable metadata without requiring the user to change directories, edit paths, or move files manually.
   - Unify the experiment control plane at the root: formal configuration, environment/dependency setup, seeds, dataset and split selection, metrics, output naming, checkpointing, logging, resume behavior, launch, and summarization. Component-local configuration may remain only as an implementation detail driven by the root.
   - Remove duplicate or conflicting data loading, preprocessing, evaluation, and result-selection logic when it could change the scientific comparison. All branches must share the frozen benchmark contract.
   - Keep the original baseline and component CLIs when useful, but expose the baseline and every proposed/control branch through the same root-level interface.
   - Ensure the integrated codebase can be installed or set up from the root using documented commands. Do not require users to independently reconstruct undocumented component environments.
   - Add focused interface tests and one bounded end-to-end integration run that exercises the real component boundary and complete artifact flow. Mocks may test edge cases but cannot be the sole evidence of integration.
   - Treat colocated source directories, a wrapper that merely launches unrelated repositories, or successfully importing both packages as insufficient unless the required scientific workflow is connected end to end.

8. Make the current server workspace locally complete.
   - Keep all source components, integration code, formal configs, launchers, tests, README, and reports needed by the experiment under the selected workspace root or in documented installed dependencies.
   - Remove runtime dependence on undocumented source trees outside the workspace. External datasets, checkpoints, services, and environment packages may remain external when they are explicitly recorded, available on the current machine, and resolved by the root configuration.
   - Prefer workspace-relative paths and root-driven path resolution. Machine-specific resource locations may be configurable but must not be hard-coded into component internals.
   - Confirm the documented setup and formal entrypoint work from the current workspace and selected environment without copying files manually between components.
   - Treat nested `.git` directories, untracked files, missing commits, and the absence of a top-level Git repository as irrelevant to experiment readiness. Do not reorganize or publish version control unless the user separately requests it.

9. Freeze the formal experiment design.
   - Write `experiment_plan.yaml` with dataset/version, splits, preprocessing boundary, inputs, targets, horizons, metrics, aggregation, seeds, tuning policy, compute budget, checkpoint rule, and output layout.
   - Keep baseline, proposed method, controls, and ablations under the same benchmark and evaluation contract.
   - Write `experiment_matrix.yaml` with one entry per formal branch, including purpose, config, command, expected outputs, resource estimate, and dry-run command.
   - Separate smoke parameters from formal parameters so dry-run reductions cannot silently alter the formal plan.

10. Validate the prepared codebase.
   - Run relevant static checks, imports, compilation, unit or interface tests, and tiny fixtures.
   - Revalidate the preserved original-baseline mode after the code changes through the cheapest scientifically faithful regression path. Save the command and a non-empty evidence file; an unchanged old artifact checksum is not a post-change regression.
   - Run a bounded dry run for every formal experiment branch through the same code path used by its formal command.
   - Save a non-empty dry-run evidence file for every matrix branch and set its status from execution evidence, not from planned intent.
   - Validate metric parsing, output isolation, checkpoint creation or loading, resume behavior when relevant, and generated configuration resolution.
   - Invoke `agent-fix-error-recovery` for unexpected command failures, then return to this stage. Keep intended method development and experiment design in this skill.
   - On a reopened ready codebase, reuse validation evidence for unaffected paths. Do not rerun every branch or the baseline solely because the skill was invoked again.

11. Generate batch entrypoints without running them.
   - Generate a platform-appropriate batch script from `experiment_matrix.yaml`.
   - Make environment targeting, working directory, config, output directory, and failure behavior explicit.
   - Add a clearly documented dry-run or print-only mode when practical.
   - Check script syntax and command expansion without launching full formal experiments.
   - Add or update a managed `## Formal Experiments` section in the primary repository README between `<!-- kaivu-formal-experiment:start -->` and `<!-- kaivu-formal-experiment:end -->`.
   - Include prerequisites, environment activation, working directory, the exact guarded formal command, matrix scope, output locations, result summarization, and the fact that formal execution has not started.
   - Preserve all README content outside the managed markers.

12. Decide readiness.
    - Write `experiment_readiness.yaml`.
    - Use `ready_for_formal_run`, `needs_user_decision`, `needs_implementation`, or `blocked`.
    - Mark `ready_for_formal_run` only when requirement traceability is complete, the scientific workflow is functionally integrated behind one root interface, the current workspace is locally complete, the baseline mode is preserved through post-change regression, the protocol and matrix are frozen, every branch passes its dry run with evidence, batch scripts and README instructions are validated, and no scientific decision remains open.
    - Re-read the modified source, formal configurations, launcher, README, matrix, readiness artifacts, baseline-regression evidence, and dry-run evidence before deciding.
    - Confirm that recorded commands are the commands actually executed and that expected outputs exist and are parseable.
    - If any required code, command, output, evidence, or decision is missing, use `needs_user_decision`, `needs_implementation`, or `blocked`; do not let self-reported YAML fields override the observed codebase state.

13. Write the consolidated human-readable report.
    - Write `experiment_readiness_report.md` after the final codebase inspection so it reflects actual implementation rather than the original plan.
    - Preserve the user's original requirement verbatim when it is available. If it was not recorded, ask the user instead of reconstructing it from code.
    - Include a requirement-to-code table that maps every requirement to repository/component, repo-relative file, function/class/symbol, actual change, experiment branch, and verification evidence.
    - For multi-repository solutions, explain the integrated architecture, component responsibilities, real data and artifact flow, root entrypoint, unified configuration and environment, interface tests, bounded end-to-end evidence, component paths, provenance, and current-workspace execution procedure.
    - Explain the baseline starting point, unchanged scientific protocol, implementation changes, experiment design, matrix scope, dry-run results, readiness decision, and remaining limitations in concise prose and readable tables.
    - Include copyable formal-run and result-summary commands, environment, working directory, expected output paths, resume behavior, and the README location.
    - Link to detailed YAML and log artifacts rather than dumping their raw content.
    - Use clear headings, short paragraphs, descriptive tables, and terminology understandable to a researcher who did not follow the terminal session.

14. Hand off the formal command.
    - In the final user-facing response, state that formal experiments have not started.
    - Give the exact repository path, environment, formal command copied from `experiment_readiness.yaml`, output location, and summarizer command when one exists.
    - Point the user first to `experiment_readiness_report.md`, then to the managed README section and machine-readable artifacts.

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
workspace_integration:
  status: "passed"
  architecture_root: ""
  formal_entrypoint: ""
  component_roles: []
  pipeline_stages: []
  interface_contracts: []
  shared_control_plane:
    configuration: ""
    environment_setup: ""
    benchmark_data: ""
    evaluation: ""
    outputs_and_resume: ""
  end_to_end_dataflow_check: "passed"
  manual_handoffs: []
  duplicated_scientific_control_planes: []
  components: []
  undocumented_external_source_paths: []
  local_workspace_run_check: "passed"
checks:
  requirement_traceability: "passed"
  implementation_complete: "passed"
  functional_integration_complete: "passed"
  local_workspace_complete: "passed"
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
  method_adaptation_plan: "experiment_artifacts/plans/method_adaptation_plan.yaml"
  method_adaptation_report: "experiment_artifacts/reports/method_adaptation_report.md"
  experiment_plan: "experiment_artifacts/plans/experiment_plan.yaml"
  experiment_matrix: "experiment_artifacts/plans/experiment_matrix.yaml"
  experiment_readiness_report: "experiment_artifacts/reports/experiment_readiness_report.md"
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
- Do not claim multi-repository readiness from directory or Git topology. Require one coherent architecture, a root-level entrypoint, explicit component contracts, unified experiment controls, a real bounded end-to-end dataflow check, and all source needed by the current server run.
- Git tracking, commits, author identity, and clean-clone reconstruction are outside this skill's readiness gates. Perform them only when the user explicitly asks for version-control or publishing work.
- Treat successful command exit as one piece of evidence; verify outputs, metrics, code paths, and artifact traceability.
- Treat artifact fields as summaries of observed code and command evidence, never as substitutes for direct inspection and execution.
- Treat `experiment_readiness_report.md` as the human-facing source of truth; keep detailed machine state in the YAML artifacts it references.
- Prefer the existing completion contract over expanding the definition of done during re-entry. Optional improvements do not invalidate a ready codebase.
- Preserve idempotency: an unchanged `ready_for_formal_run` codebase must remain unchanged and must not incur repeated baseline or smoke execution.
- Never interpret dry-run metrics as scientific findings.

## Boundaries

Do:

- inspect and modify experiment code inside the approved workspace
- implement adapters, methods, evaluation hooks, configurations, and cross-repository interfaces required by the approved goal
- integrate multi-repository solutions into one locally complete experiment workspace with a unified runnable root
- preserve and regression-check the original baseline mode
- configure and dry-run every formal branch
- generate but not launch formal batch scripts
- document the exact formal command in the repository README and final response
- produce one readable final report that connects requirements, code locations, changes, experiments, and execution instructions

Do not:

- invent missing research or optimization objectives
- silently change benchmark invariants or scientific meaning
- discard user changes or use destructive Git operations
- copy code without provenance and license review
- launch full formal experiments
- mark readiness from artifact fields without checking the actual codebase and commands
