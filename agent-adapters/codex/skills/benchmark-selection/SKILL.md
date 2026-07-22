---
name: benchmark-selection
description: Select the smallest scientifically meaningful benchmark contract that is tightly linked to the research requirement or source paper's core claim, method behavior, representative task/data, published metric, and reference result. Use as an auxiliary decision for experiment-repo-search, or during paper/repository onboarding when the core benchmark route is ambiguous and a generic demo could be mistaken for reproduction. Comparative questions require the minimum necessary branches; non-comparative questions may use one controlled experiment. Reject environment, API, random-action, import, and reward-only smoke tests as final baselines unless that exact behavior and output support the paper's core claim. Write benchmark_plan.yaml and benchmark_selection_report.md without selecting repositories, downloading resources, modifying code, or running experiments.
---

# Benchmark Selection

Use this skill as an auxiliary decision index called by `experiment-repo-search` or by `repo-onboard` when a paper/repository route does not yet identify a defensible core benchmark. It is not a top-level workflow stage.

Read [references/benchmark-criteria.md](references/benchmark-criteria.md) before deciding.

## Project Definition

Choose a **minimum credible benchmark unit** that:

- traces the research requirement or paper's main empirical claim to an executable task;
- exercises the original method on one representative dataset or input;
- runs the learned, fitted, planned, or otherwise claim-bearing method path rather than a random/untrained placeholder;
- produces the same metric family used to support the relevant claim, or a justified faithful proxy;
- records a published/documented reference value when one exists;
- has enough protocol evidence to preserve the result as the later optimization baseline;
- fits the user's compute, access, and download constraints.

Interpret **minimum** as the smallest benchmark scope that passes all core-claim gates, not as the lowest-resource runnable route. Scientific sufficiency is a prerequisite; resource efficiency is a secondary selection criterion among sufficient routes.

For open-ended requirements, the benchmark unit must support the smallest controlled experiment needed to answer the question. A single meaningful branch can be sufficient for non-comparative questions. For comparative questions, include the smallest controlled comparison needed; a single treatment branch is insufficient when the user asks whether some information, module, model family, or strategy improves performance.

Prefer official pretrained evaluation, released predictions/results, bundled data, or one established public dataset over unnecessary full retraining.

Do not require all datasets, horizons, seeds, tables, figures, comparisons, or ablations from the paper.

Minimize **breadth before fidelity**. First reduce the number of datasets, seeds, comparison methods, ablations, or sweep points. Keep the selected core experiment's paper-reported epochs/steps, data scale, model configuration, evaluator, and metric when they are feasible. Do not shorten them merely to make the run faster.

## Artifact Location

Use the calling workflow's `artifact_root`.

- plan: `<artifact_root>/plans/benchmark_plan.yaml`
- report: `<artifact_root>/reports/benchmark_selection_report.md`
- evidence and logs: supporting dataset/protocol evidence

## Agent Contract

Advisory role: `BenchmarkIndex`

Inputs:

- `research_requirement.yaml` or equivalent natural-language requirement
- when applicable, the source paper, paper extraction, official repository documentation, or `paper_repo_resolution.md`
- task, modality, target, optimization goal, and minimum original-method behavior
- data, license, privacy, compute, runtime, download, and service constraints
- optional candidate datasets, checkpoints, released results, or evaluation tooling

Required outputs:

- `<artifact_root>/plans/benchmark_plan.yaml`
- `<artifact_root>/reports/benchmark_selection_report.md`

Handoff:

- Return the benchmark contract to `experiment-repo-search`.
- Do not appear as an additional stage in the user-facing main route.

## Workflow

1. Define the minimum evidence requirement.
   - Preserve the research question and optimization goal.
   - Extract a claim-linked benchmark tuple: claim, claim-bearing method behavior, representative task/data, primary metric, documented reference result, and optional comparator.
   - Classify the core contribution and decide whether the current reproduction target requires rerunning training or artifact generation. Do not infer this solely from how the paper produced its released artifact.
   - Cite where each tuple element comes from: paper table/figure/section, official repository evaluation instructions, benchmark documentation, or released result metadata.
   - Identify the original-method behavior that must be reproduced before optimization.
   - Identify whether the question is comparative.
   - For comparative questions, define required branches and fairness invariants before repository search.
   - Define one primary metric or meaningful output.
   - Freeze a claim-bearing evidence unit before considering commands or resource convenience: representative input set, original-method output, evaluator, aggregate metric or claim-specific result, comparator when required, and reference evidence when available.
   - State the scientific question that this evidence unit answers. Reject a route whose outputs cannot answer that question even if the model, checkpoint, or interface runs successfully.
   - Separate hard requirements from preferences.

2. Search benchmark candidates.
   - Consider official paper datasets, established public benchmarks, repository-bundled data, official checkpoints, released predictions/results, and documented evaluators.
   - Verify provenance, availability, license, task fit, split or temporal safety, metric meaning, and expected resource cost.

3. Evaluate candidate routes.
   - Apply the hard gates in the criteria reference.
   - Require an end-to-end evidence chain from the core claim to the executable evaluator; do not infer scientific validity merely because an official repository exposes a runnable example.
   - Prefer the smallest route that produces a valid original-method result.
   - Accept an official checkpoint, trained model, or released result when it incorporates the core method and supports the claim-bearing experiment and metric.
   - Require method execution only when the stated target concerns the training or generation process, no valid released artifact exists, or later optimization requires proving that process runs.
   - Mark runnable checks without core-claim evidence as `smoke_only` or `demo_only`, reject them as the final benchmark, and record the missing evidence.
   - Do not substitute intermediate model outputs, scores, probabilities, embeddings, generated samples, or interface responses for the paper's claim-bearing evaluation. They are sufficient only when those outputs are themselves the documented evidence unit for the selected claim.
   - For dataset-level empirical claims, require at least one representative paper benchmark dataset or a justified subset, the paper-aligned evaluator, and its primary aggregate metric.
   - When the claim concerns downstream selection, ranking, retrieval, control, or decision quality, evaluate the downstream outcome. Component-level scoring or classification is auxiliary evidence unless the selected paper claim is specifically about that component metric.
   - Estimate the cost of the closest paper configuration before considering a shortened protocol.
   - Allow protocol simplification only for a concrete material constraint such as excessive runtime/compute, unavailable hardware/data, access restrictions, or a user-imposed budget. Record the evidence, changed parameters, expected scientific impact, and the closest later full-run command.

4. Choose a mode.
   - `adopt_existing`: use an established dataset/protocol or official evaluation directly.
   - `adapt_existing`: use a bounded format, loader, alignment, or local evaluator adaptation without changing scientific meaning.
   - `construct_minimal`: combine traceable public sources only when no existing unit satisfies the requirement.
   - Ask only when alternatives imply different scientific targets, licenses, leakage risks, or resource classes.

5. Freeze only the necessary protocol.
   - Record one representative dataset/input, applicable split or evaluation boundary, primary metric/output, original-method command expectations, checkpoint/result source, and fairness invariants needed for later optimization.
   - Record optional broader paper resources separately; do not mark them required.
   - If required benchmark resources are unavailable, keep the claim-bearing route blocked or request confirmation for a scientifically different target. Do not silently replace it with a cheaper runnable task and retain `status: ready`.

6. Write artifacts.
   - Include selected route, rejected alternatives, evidence, risks, adaptation obligations, and repository-fit requirements.
   - Mark `status: ready` only when repository search can judge candidates without inventing the baseline target.

## Plan Shape

```yaml
status: "ready" # ready | needs_user_confirmation | blocked
mode: "adopt_existing" # adopt_existing | adapt_existing | construct_minimal | undetermined
research_requirement_path: ""

minimum_reproduction:
  baseline_kind: "single_method" # single_method | controlled_comparison
  original_method_behavior: ""
  core_claim: ""
  claim_evidence: []
  core_contribution_type: "artifact_evaluation" # artifact_generation | artifact_evaluation | system_execution | analysis
  method_execution_required: false
  method_execution_reason: ""
  required_method_stages: []
  generated_artifact: ""
  representative_dataset_or_input:
    name: ""
    version: ""
    source: ""
    license: ""
  route: "pretrained_eval" # pretrained_eval | released_result_eval | documented_training | bundled_example
  checkpoint_or_released_result:
    name: ""
    source: ""
    required: false
  primary_metric_or_output: ""
  evidence_unit:
    scientific_question: ""
    representative_inputs: ""
    method_output: ""
    evaluator: ""
    aggregate_or_claim_specific_result: ""
    comparator_requirement: ""
  metric_evaluator: ""
  reference_target: ""
  reference_evidence: []
  expected_cost: ""
  protocol_fidelity: "paper_exact" # paper_exact | paper_reduced_scope | shortened_core_protocol
  simplification:
    applied: false
    reason: ""
    cost_evidence: ""
    changed_parameters: []
    expected_scientific_impact: ""
    full_protocol_command: ""
  required_branches:
    - name: ""
      role: "control" # control | treatment | reference
      description: ""

protocol:
  task_definition: ""
  split_or_evaluation_boundary: ""
  preprocessing_boundary: ""
  leakage_controls: []
  metric_direction: "unknown"
  fairness_invariants:
    - "same dataset/input"
    - "same split or evaluation boundary"
    - "same primary metric"

claim_alignment:
  task_matches_claim: false
  method_path_is_claim_bearing: false
  metric_matches_paper_or_requirement: false
  reference_is_traceable: false
  smoke_only: false
  demo_only: false
  evaluation_only: false
  dataset_level_evaluation_required: false
  representative_benchmark_coverage: ""
  evidence_unit_complete: false
  downstream_outcome_required: false
  downstream_outcome_verified_by_plan: false
  missing_elements: []

adaptation:
  required: false
  obligations: []
  acceptance_checks: []

optional_full_paper_scope: []
repository_fit_requirements: []
open_questions: []
evidence: []
handoff:
  next_skill: "experiment-repo-search"
```

## Decision Rules

- One representative dataset or input is sufficient.
- One treatment branch alone is not sufficient for a comparative open-ended requirement.
- Required branches should be minimal; do not expand to a full ablation suite unless the user asks.
- Prefer `paper_exact` or `paper_reduced_scope`: reduce experiment breadth before changing the selected core experiment's training or evaluation protocol.
- Do not reduce epochs, optimization steps, training examples, model size, evaluation episodes, or other convergence/performance-bearing parameters solely for convenience.
- A shortened core protocol is acceptable only when the closest paper configuration is materially costly or infeasible and the reduction still exercises the claim-bearing path. It establishes a local optimization baseline, not paper-level metric reproduction, unless evidence shows equivalence.
- Use the original method's released checkpoint or result when it avoids unnecessary training and remains scientifically valid.
- Missing a full paper benchmark suite is not a blocker.
- A benchmark is invalid if it does not exercise the original method, cannot produce a meaningful result, leaks unavailable information, or cannot support later fair optimization comparison.
- Repository authority establishes provenance, not core-result reproduction.
- Runnable output without the paper-aligned evidence unit does not establish the reported claim.
- Availability of official code, data, or a checkpoint proves provenance and feasibility only. It does not justify changing the evidence unit from the paper's downstream or aggregate result to an easier component-level output.
- A small batch of per-example outputs cannot pass an aggregate empirical claim without a representative sampling rule, labels or targets when applicable, the aligned evaluator, and the primary aggregate metric.
- Do not require regeneration merely because the paper originally created or changed an artifact. A released artifact is sufficient when it incorporates the core method and the selected evaluation reproduces a representative core experiment.
- When `method_execution_required: true`, record the target-specific reason and the stages that must run.
- If no feasible claim-bearing route exists, return `blocked` or `needs_user_confirmation`; do not weaken the benchmark to obtain `ready`.
- Keep optional broader experiments outside the required resource scope.

## Boundaries

Do:

- select the minimum credible benchmark unit
- define the necessary metric, evaluation boundary, leakage controls, and reference evidence
- provide repository-fit requirements to `experiment-repo-search`

Do not:

- select or clone repositories
- download datasets or checkpoints
- implement adapters or modify source
- run baseline or training
- require complete paper reproduction
