---
name: repo-onboard
description: Inspect the final cloned or adapted research repository, identify the minimum scientifically meaningful reproduction or controlled experiment path, discover one representative dataset or official pretrained/released-result evaluation route, find comparable documented reference results when available, and write the Agent-owned config.yaml for resource, environment, and baseline stages. Use after repo-experiment-fix for open-ended requirements, after paper-repo-discovery for a paper without a known repository, or directly when the user supplies a specific paper and repository. For specific-paper reproduction, the selected path must align with a core experiment, official demonstration, task type, or evaluation route used to support the paper's main contribution. For open-ended comparative requirements, preserve the required control/treatment branches in config.yaml; for non-comparative requirements, a single controlled experiment can be sufficient. This skill does not install dependencies, acquire resources, modify experiment logic, or require complete paper reproduction.
---

# Repo Onboard

Use this skill to convert one final repository path into an evidence-backed minimum-reproduction configuration. Treat core-experiment reproduction as a hard constraint and resource minimization as a secondary optimization objective.

The target is not every experiment in the paper. Select one smallest credible paper-aligned core experiment, but keep that experiment's original training and evaluation protocol when it is feasible. Reduce breadth before fidelity: omit extra datasets, seeds, methods, ablations, and sweeps before reducing epochs, steps, data scale, model size, or evaluation episodes.

For open-ended requirements, select the smallest controlled experiment path that answers the user's question. Comparative requirements may require multiple commands or one command matrix, but only for the required branches.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<repo>/experiment_artifacts/`.

- manifest: `<artifact_root>/manifests/config.yaml`
- report: `<artifact_root>/reports/onboard_report.md`
- evidence and logs: repository inspection and optional bounded checks

Do not overwrite repository-native runtime configuration files.

## Terminal Output

Report only stage status, selected minimum-reproduction path, artifact paths, blockers, and next step. Put detailed commands, reference evidence, and repository findings in the artifacts.

## Agent Contract

Role: `AgentOnboard`

Inputs:

- final repository path
- optional paper identity or paper artifact
- optional `paper_repo_resolution.md`
- optional `research_requirement.yaml`, `experiment_repo_plan.yaml`, or `repo_experiment_fix.yaml`
- optional user command or metric override

Required output:

- `<artifact_root>/manifests/config.yaml`

Recommended output:

- `<artifact_root>/reports/onboard_report.md`

Handoff:

- Hand the selected minimum-reproduction command and resource hints to `repo-resource-prepare`.

## Minimum Reproduction Standard

The selected path must:

- execute the original method, not only import modules or print help;
- for a specific paper, align with the paper's core experiment, official example, task type, protocol family, or documented evaluation route used to demonstrate the main contribution;
- use one representative dataset, bundled input, official checkpoint, or released result;
- produce the method's primary metric, prediction, retrieval output, graph, or other meaningful result;
- be reusable as the unchanged comparator for future optimization;
- have enough evidence to identify the command, input, output, and success criterion.

Prefer, in order:

1. official pretrained checkpoint plus documented evaluation;
2. official released prediction/result plus documented evaluator;
3. bundled representative dataset plus documented evaluation;
4. the shortest documented training path that produces the original-method result.

Prefer released artifacts over redundant retraining. Otherwise, do not shorten the selected core experiment merely for convenience. Simplify its protocol only when the closest paper configuration has a concrete material runtime, compute, hardware, data, access, or user-budget constraint. Do not require all datasets, all paper tables, all seeds, or all ablations. Do not select an unrelated demo, generic package example, or toy smoke test when it does not correspond to the paper's core experiment.

## Workflow

1. Confirm repository context.
   - Resolve the final repository path and verify it exists.
   - If the user supplied an existing local repository for this experiment, create or verify an isolated copy under the run/workspace root before onboarding unless the user explicitly asks to operate in place.
   - Tell the user the original local path, the copy path, and that the original repository will not be modified.
   - Read inherited search/fix or paper-resolution artifacts when present.
   - Confirm this is the repository that later stages must run.

2. Reuse existing Agent configuration when valid.
   - Read `<artifact_root>/manifests/config.yaml` if present.
   - Revalidate its repository path, command, minimum-reproduction evidence, and source identity.
   - Treat repository-native configs as runtime evidence, not as the Agent manifest.

3. Inspect repository evidence.
   - Read README, docs, scripts, examples, runtime configs, dependency files, saved outputs, checkpoints, releases, and common entrypoints.
   - Inspect training, evaluation, demo, data loader, checkpoint loader, and metric code.
   - Use only cheap read-only commands such as listing, search, static inspection, and `--help` when dependencies permit.

4. Select the minimum reproduction path.
   - Identify one representative dataset or input.
   - For specific-paper routes, identify the paper's core experiment or official demonstration path first, then choose the smallest runnable route that still matches it.
   - Compare the chosen route against the paper configuration, including epochs/steps, training examples, model configuration, evaluation episodes, evaluator, and metric.
   - If the paper configuration is feasible, preserve it. If it is materially costly or infeasible, record cost evidence, every protocol reduction, its expected scientific impact, and the closest full-run command.
   - Prefer evaluation-only or released-result paths over retraining.
   - If `repo_experiment_fix.yaml` or `benchmark_plan.yaml` defines `controlled_baseline.required: true` or `baseline_kind: controlled_comparison`, preserve every required branch in the config.
   - Require each branch to share the benchmark invariants unless the benchmark plan explicitly differs.
   - Do not invent comparison branches for a non-comparative requirement when one controlled experiment directly answers the question.
   - Reject generic demos that only prove the package works but do not exercise the paper's claimed method or core scientific workflow.
   - Record the original method entrypoint, command, working directory, pre-eval steps, expected outputs, primary metric or success criterion, and estimated cost.
   - A cheap smoke command may be used as an intermediate check, but it is not the final baseline target unless it produces the meaningful original-method result required above.

5. Discover reference evidence.
   - Search README, paper tables, docs, configs, examples, logs, saved outputs, and release notes for a result comparable to the selected path.
   - Record source, dataset/input, split, checkpoint, metric, value, command conditions, confidence, and comparability.
   - If no comparable reference exists, record `reference_status: not_found`; later stages may establish a local baseline.
   - Do not expand to additional datasets solely to find a reference.

6. Run a bounded check only when already feasible.
   - If dependencies and resources already exist, a cheap execution of the selected command is allowed.
   - Do not install, download, create environments, modify source, or start expensive training here.
   - Record pending resource or environment blockers honestly.

7. Write and verify `config.yaml`.
   - Include enough evidence for resource, environment, and baseline stages to proceed without rediscovery.
   - Mark `onboard_status: ready` only when a meaningful minimum-reproduction target is identified.

## Config Shape

```yaml
paper_name: ""
paper_title: ""
repo_path: ""
onboard_status: "ready" # ready | partial | blocked
confidence: "high" # high | medium | low

minimum_reproduction:
  original_method: ""
  paper_core_experiment:
    aligned: false
    paper_claim_or_experiment: ""
    alignment_evidence: []
  purpose: "optimization_baseline"
  baseline_kind: "single_method" # single_method | controlled_comparison
  route: "pretrained_eval" # pretrained_eval | released_result_eval | documented_training | bundled_example
  representative_dataset_or_input: ""
  checkpoint_or_result: ""
  command: ""
  working_directory: ""
  pre_eval_commands: []
  primary_metric_or_output: ""
  metric_direction: "unknown" # higher | lower | unknown
  expected_result_files: []
  estimated_cost: ""
  protocol_fidelity: "paper_exact" # paper_exact | paper_reduced_scope | shortened_core_protocol
  simplification:
    applied: false
    reason: ""
    cost_evidence: ""
    changed_parameters: []
    expected_scientific_impact: ""
    full_protocol_command: ""
  full_paper_reproduction_required: false
  comparison_branches:
    - name: ""
      role: "control"
      command: ""
      expected_result_files: []
  fairness_invariants: []

baseline:
  status: "not_run" # passed | failed | not_run | pending_resources | pending_environment | blocked
  command: ""
  metrics: {}
  documented_baseline: {}
  reference_status: "not_found" # found | not_found | ambiguous
  reference_sources: []
  comparison: "not_available"

setup_commands: []
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
next_skill: "repo-resource-prepare"
```

## Decision Rules

- `ready`: the original method, paper-core alignment when applicable, one representative input, meaningful result, and command path are supported by evidence.
- A shortened core protocol without a material constraint and explicit impact record is not `ready` for a specific-paper route.
- Matching a shortened-run golden value proves that shortened configuration is reproducible; it does not by itself prove the paper's reported result.
- `partial`: useful evidence exists but the command, result, or representative input remains ambiguous.
- `blocked`: the repository is invalid or no meaningful original-method path can be identified.
- Missing resources or dependencies do not block onboarding when their exact requirements can be handed to later stages.
- A missing documented reference does not invalidate a meaningful local baseline.
- For open-ended comparative requirements, missing a required control branch is not `ready`; return to `repo-experiment-fix` unless the user explicitly narrows the task.
- For non-comparative open-ended requirements, do not block readiness solely because no control branch exists.

## Boundaries

Do:

- identify the smallest credible original-method reproduction path
- preserve paper-core alignment for specific-paper reproduction
- prefer released checkpoints/results over unnecessary retraining
- discover comparable documented results
- write the Agent-owned `config.yaml`
- preserve uncertainty and evidence

Do not:

- require all paper datasets, tables, seeds, or ablations
- install dependencies, create environments, or acquire resources
- modify repository source or scientific protocol
- treat an import-only or help-only check as the final baseline
- treat an unrelated generic demo as the final baseline for a specific paper
