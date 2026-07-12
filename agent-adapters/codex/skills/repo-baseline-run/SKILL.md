---
name: repo-baseline-run
description: Run and record the configured minimum baseline as the final AgentInit stage and the project's formal optimization-readiness gate. Use after repo-onboard, repo-resource-prepare, and repo-environment-setup have prepared one coherent repository, the required representative dataset or official pretrained/released-result assets, and the selected environment. For specific papers or supplied repositories, execute the meaningful original-method reproduction on a paper-aligned core experiment or official demonstration path. For open-ended research requirements, execute at least one smallest controlled experiment that answers the research question; comparative questions additionally require the minimum necessary on/off, method/control, component/no-component, or reference-model branches. Parse results, compare with documented evidence when available, invoke AgentFix on failures, and write baseline_metrics.yaml plus baseline_run_report.md. A passed baseline means ready_for_optimization in this project; no separate formal-experiment preparation stage follows.
---

# Repo Baseline Run

Use this skill as the final initialization stage.

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
- for specific-paper reproduction, match the paper-aligned core experiment or official demonstration path recorded by `repo-onboard`;
- use the selected representative dataset/input, official checkpoint, or released result;
- produce a meaningful metric or method output;
- save enough command, environment, resource, and output evidence to rerun it;
- provide a stable comparison point for later optimization.

For open-ended comparative requirements, the baseline must additionally:

- run every required branch from `config.yaml`, `benchmark_plan.yaml`, or `repo_experiment_fix.yaml`;
- keep dataset/input, split, primary metric, evaluator, target, model capacity, and budget fixed across branches unless the benchmark plan says otherwise;
- compute and record the branch deltas needed to answer the research question;
- avoid `ready_for_optimization: true` when only the treatment branch ran.

For non-comparative open-ended requirements, do not require comparison branches when one controlled experiment directly answers the stated question.

An import check, `--help`, empty dry run, unrelated toy output, or generic demo that is not aligned with the paper's core experiment is insufficient.

Acceptable efficient routes include:

- evaluation of an official pretrained model;
- scoring official released predictions/results;
- evaluation on one bundled or public representative dataset;
- the shortest necessary documented training route when no valid released artifact exists.

Do not retrain merely to recreate an artifact that the official repository already releases. Do not require every dataset, seed, horizon, table, or ablation.

## Workflow

1. Confirm readiness.
   - Read config, resource, and environment artifacts.
   - Confirm the command exercises the original method and matches the selected minimum reproduction.
   - For specific-paper routes, confirm `config.yaml` records paper-core alignment evidence and do not run a generic demo as the final baseline unless it is the paper's official demonstration path.
   - For `baseline_kind: controlled_comparison`, confirm every required branch has a command, resource path, metric parser, and success criterion.
   - Confirm every required resource is available and the environment is ready.
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
   - Ask before a large download, long training, GPU-heavy execution, overwriting results, or a materially different command.
   - Prefer official pretrained or released-result evaluation when it avoids unnecessary expensive training.

6. Run the baseline.
   - Execute from the configured working directory.
   - Capture return code, elapsed time, logs, produced files, metrics, and relevant result metadata.
   - Keep generated outputs under the run directory when configurable.
   - For controlled comparisons, run each required branch and stop only for a real blocker or user-approved risk decision.

7. Validate the result.
   - Confirm the result is non-empty and came from the intended original-method path.
   - For specific-paper routes, confirm the result came from the configured paper-core experiment path, official example, or documented evaluation route.
   - Parse the primary metric or validate the defined method output.
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
  representative_dataset_or_input: ""
  checkpoint_or_result: ""
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
- For `baseline_kind: controlled_comparison`, `passed` additionally requires every required branch to succeed and the primary delta to be recorded.
- `partial`: execution succeeds but the meaningful output, method path, or metric cannot be verified; this is not ready for optimization.
- `failed`: command fails, times out, produces invalid output, or a comparable result is outside an evidence-backed tolerance.
- `blocked`: required resources, environment, credentials, approval, or hardware are missing.
- Set `ready_for_optimization: true` only for `passed`.
- A passed baseline is the final initialization state for this project.

## Boundaries

Do:

- run the configured minimum original-method reproduction
- prefer evaluation-only released assets over unnecessary retraining
- preserve command, resource, environment, metric, and output evidence
- compare with documented references when available
- establish the result as the later optimization comparator
- invoke AgentFix automatically on unexpected failures

Do not:

- require complete paper reproduction
- require all datasets, tables, seeds, horizons, or ablations
- add a post-baseline experiment-readiness stage
- accept import-only or empty smoke success as the final baseline
- accept an unrelated generic demo as the final baseline for a specific paper
- modify source, metrics, dataset semantics, or model logic in this stage
- install dependencies or acquire resources
