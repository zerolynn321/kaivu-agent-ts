---
name: repo-onboard
description: Inspect or audit a research repository, identify the minimum core-experiment reproduction or controlled experiment path, discover a representative benchmark dataset or justified subset and official pretrained/released-result route when available, find comparable references, and write or re-evaluate config.yaml. Use after repo-experiment-fix or paper-repo-discovery, when a paper repository is supplied, or when reviewing whether an existing baseline configuration truly represents the paper's core experiment. For dataset-level paper claims, require the paper-aligned evaluator and primary aggregate metric; do not accept single-sample or arbitrary-folder inference as the final baseline merely because it uses official code or weights. Preserve required comparison branches for comparative requirements. This skill does not install dependencies, acquire resources, modify experiment logic, or require complete paper reproduction.
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
- for a specific paper, align with the paper's core experiment and documented evidence route used to demonstrate the main contribution;
- use a representative benchmark dataset or justified subset and reuse an official checkpoint or released result when valid;
- produce the paper-aligned primary aggregate metric for dataset-level claims, or another core result only when that result type directly supports the paper's claim;
- be reusable as the unchanged comparator for future optimization;
- have enough evidence to identify the command, input, output, and success criterion.

Classify the core contribution and the current reproduction target before selecting a route. Set `method_execution_required: true` only when the target concerns training or artifact generation, no valid released artifact exists, or later optimization requires proving that process runs. An official checkpoint, trained model, or released result may otherwise support `ready` when it incorporates the core method and is evaluated on a representative core experiment. Dataset-level claims require a representative benchmark dataset or justified subset, the paper-aligned evaluator, and the primary aggregate metric.

Choose the least costly route that supplies the required core evidence. Prefer valid released artifacts over unnecessary retraining. Do not shorten the selected core experiment merely for convenience; simplify only for a material constraint and record its impact. Do not require peripheral paper scope.

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
   - Identify one representative paper benchmark dataset or justified subset; use a single input only when the paper's core evidence is genuinely single-instance or qualitative rather than dataset-level.
   - For specific-paper routes, identify the paper's core experiment and evidence unit first: dataset, split, evaluator, aggregate metric, and reference result when applicable.
   - Classify `core_contribution_type`, `method_execution_required`, its target-specific reason, and any required stages or generated artifact.
   - Compare the chosen route against the paper configuration, including epochs/steps, training examples, model configuration, evaluation episodes, evaluator, and metric.
   - If the paper configuration is feasible, preserve it. If it is materially costly or infeasible, record cost evidence, every protocol reduction, its expected scientific impact, and the closest full-run command.
   - Prefer evaluation-only or released-result paths only when they reproduce the classified contribution; otherwise use them as supporting references.
   - If `repo_experiment_fix.yaml` or `benchmark_plan.yaml` defines `controlled_baseline.required: true` or `baseline_kind: controlled_comparison`, preserve every required branch in the config.
   - Require each branch to share the benchmark invariants unless the benchmark plan explicitly differs.
   - Do not invent comparison branches for a non-comparative requirement when one controlled experiment directly answers the question.
   - Reject runnable checks that do not produce the required core-claim evidence.
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
  core_contribution_type: "artifact_evaluation" # artifact_generation | artifact_evaluation | system_execution | analysis
  method_execution_required: false
  method_execution_reason: ""
  required_method_stages: []
  generated_artifact: ""
  purpose: "optimization_baseline"
  baseline_kind: "single_method" # single_method | controlled_comparison
  route: "pretrained_eval" # pretrained_eval | released_result_eval | documented_training | bundled_example
  representative_dataset_or_input: ""
  checkpoint_or_result: ""
  command: ""
  working_directory: ""
  pre_eval_commands: []
  primary_metric_or_output: ""
  evidence_unit: "dataset_metric" # dataset_metric | structured_result | qualitative_core_output
  demo_only: false
  evaluator: ""
  benchmark_subset_justification: ""
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

- `ready`: the original method, paper-core alignment, required evidence unit, meaningful result, and command path are supported. Method-execution routes additionally require all claim-bearing stages and a declared generated artifact.
- A shortened core protocol without a material constraint and explicit impact record is not `ready` for a specific-paper route.
- Matching a shortened-run golden value proves that shortened configuration is reproducible; it does not by itself prove the paper's reported result.
- `partial`: useful evidence exists, but required method execution, generated artifact, representative input, evaluator, metric, or command remains unverified.
- `blocked`: the repository is invalid or no meaningful original-method path can be identified.
- Missing resources or dependencies do not block onboarding when their exact requirements can be handed to later stages.
- A missing documented reference does not invalidate a meaningful local baseline.
- For open-ended comparative requirements, missing a required control branch is not `ready`; return to `repo-experiment-fix` unless the user explicitly narrows the task.
- For non-comparative open-ended requirements, do not block readiness solely because no control branch exists.

## Boundaries

Do:

- identify the smallest credible original-method reproduction path
- preserve paper-core alignment for specific-paper reproduction
- prefer valid released artifacts and require method execution only when the reproduction target needs it
- discover comparable documented results
- write the Agent-owned `config.yaml`
- preserve uncertainty and evidence

Do not:

- require all paper datasets, tables, seeds, or ablations
- install dependencies, create environments, or acquire resources
- modify repository source or scientific protocol
- treat runnable checks without required core-claim evidence as the final baseline
