---
name: repo-baseline-run
description: Run, record, or audit the configured core-experiment baseline as the final optimization-readiness gate. Use after repo-onboard, resource preparation, and environment setup, or when reviewing an existing passed/partial baseline and its ready_for_optimization claim. Re-evaluate recorded conclusions from underlying commands, outputs, and evidence rather than trusting existing status fields. For specific papers, execute the original method through a paper-aligned evaluation route; dataset-level claims require a representative paper benchmark dataset or justified subset, the paper evaluator, and its primary aggregate metric. Official-checkpoint single-sample or arbitrary-folder inference is demo-only and cannot pass. For open-ended requirements, execute the smallest controlled experiment that answers the question, including necessary comparison branches. Parse and compare results, invoke AgentFix on failures, and write baseline_metrics.yaml plus baseline_run_report.md.
---

# Repo Baseline Run

Use this skill as the final initialization stage.

Interpret the configured minimum baseline as the smallest scope that still reproduces the core experiment. Do not reinterpret it as the cheapest runnable command or the fewest possible resources.

In this project, a passed baseline means the repository can formally enter later optimization experiments. It does not mean every paper experiment was repeated.

- For a specific paper or supplied repository, it means the smallest credible paper-aligned original-method core experiment has been reproduced and preserved as the optimization comparator.
- For an open-ended research requirement, it means the smallest controlled experiment needed to answer the user's question has run and been preserved as the baseline contract for later optimization. If the question is comparative, the required comparison branches and delta are part of that contract.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<run_dir>/experiment_artifacts/`.

- manifest: `<artifact_root>/manifests/baseline_metrics.yaml`
- report: `<artifact_root>/reports/baseline_run_report.md`
- evidence: metrics and produced result files
- logs: detailed command output

## Terminal Output

Report only readiness status, approval needs, baseline result, reference comparison, artifact paths, blockers, and final `ready_for_optimization` state.

Do not say that another formal-experiment preparation stage is required after a passed baseline.

## Agent Contract

Role: `AgentInit`

Inputs:

- final repository path and run directory
- `<artifact_root>/manifests/config.yaml`
- `<artifact_root>/manifests/resource_manifest.yaml`
- `<artifact_root>/reports/resource_acquisition_report.md`
- `<artifact_root>/plans/environment_plan.yaml`
- `<artifact_root>/reports/environment_setup_report.md`
- optional user-approved command, timeout, metric parser, or expected result override

Required outputs:

- `<artifact_root>/manifests/baseline_metrics.yaml`
- `<artifact_root>/reports/baseline_run_report.md`

Final handoff:

- `status: passed` and `ready_for_optimization: true` complete the initialization workflow.
- Later optimization work must preserve this command, dataset/input, metric/output, and result as the baseline comparator.

## Valid Baseline Standard

The final baseline must:

- execute the original method in the final repository;
- for specific-paper reproduction, match the paper-aligned core experiment and evidence unit recorded by `repo-onboard`;
- use the selected representative paper benchmark dataset or justified subset, plus the official checkpoint or released result when applicable;
- produce the paper-aligned primary aggregate metric for dataset-level claims, or another result type only when it directly supports the core claim;
- save enough command, environment, resource, and output evidence to rerun it;
- provide a stable comparison point for later optimization.

An official checkpoint, trained model, or released result can pass when it incorporates the core method and the run reproduces a representative paper-aligned core experiment. When `method_execution_required: true` for a recorded target-specific reason, run the required stages and verify their outputs. Dataset-level claims additionally require the configured representative benchmark dataset or justified subset, paper-aligned evaluator, and primary aggregate metric.

For open-ended comparative requirements, the baseline must additionally:

- run every required branch from `config.yaml`, `benchmark_plan.yaml`, or `repo_experiment_fix.yaml`;
- keep dataset/input, split, primary metric, evaluator, target, model capacity, and budget fixed across branches unless the benchmark plan says otherwise;
- compute and record the branch deltas needed to answer the research question;
- avoid `ready_for_optimization: true` when only the treatment branch ran.

For non-comparative open-ended requirements, do not require comparison branches when one controlled experiment directly answers the stated question.

Runnable checks without the required core-claim evidence are insufficient.

Acceptable efficient routes include:

- paper-aligned benchmark evaluation of an official pretrained model;
- scoring official released predictions/results;
- evaluation on one bundled or public representative dataset;
- the shortest necessary documented training route when no valid released artifact exists.

Do not regenerate a valid released artifact merely because the paper originally trained or generated it. Require that process only when it is part of the current reproduction target. Do not require peripheral paper scope.

For a selected paper core experiment, preserve the paper's convergence- and performance-bearing protocol when feasible. Reduce breadth before fidelity. Do not reduce epochs/steps, training examples, model size, evaluation episodes, or similar parameters merely to save ordinary runtime.

## Workflow

1. Confirm readiness.
   - Read config, resource, and environment artifacts.
   - Confirm the command exercises the original method and matches the selected minimum reproduction.
   - For specific-paper routes, confirm `config.yaml` records paper-core alignment evidence and the correct evidence unit.
   - Confirm `core_contribution_type`, `method_execution_required`, its recorded reason, and any required stages or generated artifact.
   - For dataset-level claims, require a representative benchmark dataset or justified subset, evaluator, aggregate metric parser, and comparable reference evidence when available.
   - Compare the configured epochs/steps, data scale, model configuration, evaluator, metric, and evaluation budget with the paper or official reproduction command.
   - Reject an undocumented or convenience-only shortened core protocol. Require either the feasible paper protocol or recorded material cost evidence, changed parameters, expected scientific impact, and the closest full-run command.
   - For `baseline_kind: controlled_comparison`, confirm every required branch has a command, resource path, metric parser, and success criterion.
   - Recheck every required resource path directly; do not trust `available` from the manifest alone. Confirm non-empty command-required contents, bindings, and environment readiness.
   - If not, return to the owning stage or record a blocker.

2. Confirm environment targeting.
   - Run only inside the environment selected during `repo-resource-prepare`.
   - Use scoped execution such as `conda run` or the venv interpreter when approved.

3. Load reference evidence.
   - Read documented references from `config.yaml` and `onboard_report.md`.
   - Preserve dataset/input, checkpoint, split, metric, and command conditions.
   - If no comparable reference exists, use the produced result as the initial local optimization baseline.
   - Missing reference evidence does not block readiness when the original method and meaningful result are verified.

4. Freeze the baseline invocation.
   - Record repository path, working directory, command, pre-eval commands, environment, resource paths, selected dataset/input, checkpoint/result artifact, metric parser, expected outputs, and timeout.
   - For controlled comparisons, record all branch commands before executing the first branch.
   - Preserve the configured scientific path.
   - Ask before changing the representative dataset, metric, checkpoint, split, model behavior, or result-selection rule.

5. Ask only when execution is risky.
   - Ask before a large download, materially expensive or long hardware use not already approved, overwriting results, or a materially different command. GPU use alone is not a reason to ask or switch to CPU.
   - Prefer official pretrained or released-result evaluation when it avoids unnecessary expensive training.

6. Run the baseline.
   - Execute from the configured working directory.
   - Capture return code, elapsed time, complete raw logs, produced files, parsed metrics, and relevant result metadata under the run artifact directories.
   - Keep generated outputs under the run directory when configurable.
   - For controlled comparisons, run each required branch and stop only for a real blocker or user-approved risk decision.

7. Validate the result.
   - Confirm the result is non-empty and came from the intended original-method path.
   - For specific-paper routes, confirm the result came from the configured claim-bearing method and evaluation route.
   - Parse the primary metric or validate the defined method output.
   - Confirm the raw log, raw metric/result file, and every required produced output exist and are non-empty after execution. A report summary or copied numeric value is not raw evidence.
   - Confirm recorded resource paths still exist after execution and are sufficient to rerun the same command.
   - For controlled comparisons, compute the treatment-control delta for the primary metric and record whether it improves, worsens, or is inconclusive under the chosen metric direction.
   - Compare with a documented reference when conditions are comparable.
   - Do not require exact numerical equality when hardware, versions, or stochastic behavior justify a recorded tolerance.
   - Do not change the success criterion after observing the result.

8. Handle failures.
   - Invoke `agent-fix-error-recovery` automatically for resource, environment, command, timeout, path, or metric-parsing failures.
   - Return a missing source feature, broken integration, or requirement mismatch to `repo-experiment-fix`, then repeat onboarding and affected preparation stages.
   - After a safe fix, rerun the same scientifically meaningful baseline path.

9. Write and verify artifacts.
   - Write the manifest and report.
   - Set `ready_for_optimization: true` only for `status: passed`.
   - Before writing `passed`, re-open the manifest, raw log, raw metric/result file, and required output paths. Record their paths and checksums when practical.
   - During an audit, preserve prior raw evidence and status history. Do not delete or overwrite historical logs/results; distinguish the previous recorded state from current verified readiness.
   - Include the exact baseline comparator identity for future optimization work.

## Metrics Shape

```yaml
repo_path: ""
run_dir: ""
status: "not_run" # passed | failed | blocked | partial | not_run
ready_for_optimization: false
original_method: ""
minimum_reproduction:
  route: ""
  baseline_kind: "single_method" # single_method | controlled_comparison
  paper_core_experiment:
    aligned: false
    paper_claim_or_experiment: ""
    alignment_evidence: []
  core_contribution_type: "artifact_evaluation"
  method_execution_required: false
  method_execution_reason: ""
  required_method_stages: []
  generated_artifact: ""
  representative_dataset_or_input: ""
  checkpoint_or_result: ""
  protocol_fidelity: "paper_exact" # paper_exact | paper_reduced_scope | shortened_core_protocol
  simplification:
    applied: false
    reason: ""
    cost_evidence: ""
    changed_parameters: []
    expected_scientific_impact: ""
    full_protocol_command: ""
  working_directory: ""
environment:
  manager: ""
  name: ""
  path: ""
command: ""
pre_eval_commands: []
returncode:
elapsed_seconds:
primary_metric_or_output: ""
primary_metric_value:
metric_direction: "unknown"
metrics: {}
branches: []
comparison_delta: {}
output_validation:
  expected_files: []
  produced_files: []
  meaningful_result_verified: false
  demo_only: false
  aggregate_metric_verified: false
  method_stages_verified: false
  generated_artifact_verified: false
  raw_metric_or_result_path: ""
  required_output_paths: []
  evidence_checksums: {}
  resources_reverified: false
  rerun_assets_verified: false
documented_baseline: {}
reference_status: "not_found" # found | not_found | ambiguous | missing_from_onboard
reference_sources: []
comparison: "not_available" # matches | better | worse | not_available
accepted_tolerance: ""
log_path: ""
agentfix_invoked: false
optimization_baseline_id: ""
notes: ""
```

Use this shape for `baseline_run_report.md`:

```markdown
# Baseline Run Report

## Minimum Reproduction
- Original method:
- Paper-core experiment alignment:
- Route:
- Representative dataset/input:
- Checkpoint or released result:
- Command and environment:

## Result
| Metric or output | Value/path | Reference | Comparison | Evidence |
|---|---|---|---|---|

## Controlled Comparison
- Required:
- Branches:
- Primary delta:
- Research-question answer:

## Optimization Readiness
- Status:
- Ready for optimization:
- Baseline comparator ID:
- Preserved command:
- Remaining blockers:

## AgentFix
- Invoked:
- Outcome:
```

## Decision Rules

- `passed`: the original-method command succeeds, paper-core alignment is verified when applicable, a meaningful result is verified, and its rerun evidence is recorded.
- `passed` additionally requires all required resources and rerun assets to exist at their recorded paths, plus non-empty raw logs and raw metric/result evidence. A narrative report or historical metric alone cannot pass.
- For specific-paper routes, `passed` additionally requires `paper_exact` or `paper_reduced_scope`, unless a `shortened_core_protocol` has a material constraint and is explicitly reported as a local optimization baseline rather than paper-result reproduction.
- For `baseline_kind: controlled_comparison`, `passed` additionally requires every required branch to succeed and the primary delta to be recorded.
- `partial`: execution succeeds but required method execution, generated artifact, evidence unit, or metric cannot be verified. Record `evaluation_only` or `demo_only` when applicable and keep `ready_for_optimization: false`.
- `failed`: command fails, times out, produces invalid output, or a comparable result is outside an evidence-backed tolerance.
- `blocked`: required resources, environment, credentials, approval, or hardware are missing.
- Set `ready_for_optimization: true` only for `passed`.
- A passed baseline is the final initialization state for this project.

## Boundaries

Do:

- run the configured minimum original-method reproduction
- follow the classified contribution when choosing evaluation-only assets or method execution
- preserve command, resource, environment, metric, and output evidence
- compare with documented references when available
- establish the result as the later optimization comparator
- invoke AgentFix automatically on unexpected failures

Do not:

- require complete paper reproduction
- require all datasets, tables, seeds, horizons, or ablations
- add a post-baseline experiment-readiness stage
- accept runnable checks without required core-claim evidence as the final baseline
- modify source, metrics, dataset semantics, or model logic in this stage
- install dependencies or acquire resources
