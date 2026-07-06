---
name: repo-onboard
description: Inspect the final cloned or adapted research repository, identify the minimum scientifically meaningful original-method reproduction path, discover one representative dataset or official pretrained/released-result evaluation route, find comparable documented reference results when available, and write the Agent-owned config.yaml for resource, environment, and baseline stages. Use after repo-experiment-fix for open-ended requirements, after paper-repo-discovery for a paper without a known repository, or directly when the user supplies a specific paper and repository. This skill does not install dependencies, acquire resources, modify experiment logic, or require complete paper reproduction.
---

# Repo Onboard

Use this skill to convert one final repository path into an evidence-backed minimum-reproduction configuration.

The target is not every experiment in the paper. Select the smallest credible path that exercises the original method, produces a meaningful result, and can serve as the baseline for later optimization.

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
- use one representative dataset, bundled input, official checkpoint, or released result;
- produce the method's primary metric, prediction, retrieval output, graph, or other meaningful result;
- be reusable as the unchanged comparator for future optimization;
- have enough evidence to identify the command, input, output, and success criterion.

Prefer, in order:

1. official pretrained checkpoint plus documented evaluation;
2. official released prediction/result plus documented evaluator;
3. bundled representative dataset plus documented evaluation;
4. the shortest documented training path that produces the original-method result.

Do not select expensive full retraining when an earlier option is valid. Do not require all datasets, all paper tables, all seeds, or all ablations.

## Workflow

1. Confirm repository context.
   - Resolve the final repository path and verify it exists.
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
   - Prefer evaluation-only or released-result paths over retraining.
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
  purpose: "optimization_baseline"
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
  full_paper_reproduction_required: false

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

- `ready`: the original method, one representative input, meaningful result, and command path are supported by evidence.
- `partial`: useful evidence exists but the command, result, or representative input remains ambiguous.
- `blocked`: the repository is invalid or no meaningful original-method path can be identified.
- Missing resources or dependencies do not block onboarding when their exact requirements can be handed to later stages.
- A missing documented reference does not invalidate a meaningful local baseline.

## Boundaries

Do:

- identify the smallest credible original-method reproduction path
- prefer released checkpoints/results over unnecessary retraining
- discover comparable documented results
- write the Agent-owned `config.yaml`
- preserve uncertainty and evidence

Do not:

- require all paper datasets, tables, seeds, or ablations
- install dependencies, create environments, or acquire resources
- modify repository source or scientific protocol
- treat an import-only or help-only check as the final baseline
