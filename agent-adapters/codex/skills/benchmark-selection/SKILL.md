---
name: benchmark-selection
description: Provide an auxiliary benchmark decision for experiment-repo-search by selecting the smallest scientifically meaningful dataset, input, protocol, metric, checkpoint, or released-result route that can reproduce the original method and serve as the baseline for later optimization. Use when an open-ended research requirement needs benchmark evidence before repository comparison. One representative dataset is sufficient; do not require a full benchmark suite, every paper dataset, full retraining, or all paper results. Write benchmark_plan.yaml and benchmark_selection_report.md without selecting repositories, downloading resources, modifying code, or running experiments.
---

# Benchmark Selection

Use this skill as an auxiliary decision index called by `experiment-repo-search`. It is not a top-level workflow stage.

Read [references/benchmark-criteria.md](references/benchmark-criteria.md) before deciding.

## Project Definition

Choose a **minimum credible benchmark unit** that:

- exercises the original method on one representative dataset or input;
- produces a meaningful metric or method output;
- has enough protocol evidence to preserve the result as the later optimization baseline;
- fits the user's compute, access, and download constraints.

Prefer official pretrained evaluation, released predictions/results, bundled data, or one established public dataset over unnecessary full retraining.

Do not require all datasets, horizons, seeds, tables, figures, comparisons, or ablations from the paper.

## Artifact Location

Use the calling workflow's `artifact_root`.

- plan: `<artifact_root>/plans/benchmark_plan.yaml`
- report: `<artifact_root>/reports/benchmark_selection_report.md`
- evidence and logs: supporting dataset/protocol evidence

## Agent Contract

Advisory role: `BenchmarkIndex`

Inputs:

- `research_requirement.yaml` or equivalent natural-language requirement
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
   - Identify the original-method behavior that must be reproduced before optimization.
   - Define one primary metric or meaningful output.
   - Separate hard requirements from preferences.

2. Search benchmark candidates.
   - Consider official paper datasets, established public benchmarks, repository-bundled data, official checkpoints, released predictions/results, and documented evaluators.
   - Verify provenance, availability, license, task fit, split or temporal safety, metric meaning, and expected resource cost.

3. Evaluate candidate routes.
   - Apply the hard gates in the criteria reference.
   - Prefer the smallest route that produces a valid original-method result.
   - Treat a pretrained checkpoint evaluation or released-result evaluation as valid when it preserves the intended method and metric.
   - Reject import-only checks, unrelated toy demos, and outputs that cannot serve as an optimization comparator.

4. Choose a mode.
   - `adopt_existing`: use an established dataset/protocol or official evaluation directly.
   - `adapt_existing`: use a bounded format, loader, alignment, or local evaluator adaptation without changing scientific meaning.
   - `construct_minimal`: combine traceable public sources only when no existing unit satisfies the requirement.
   - Ask only when alternatives imply different scientific targets, licenses, leakage risks, or resource classes.

5. Freeze only the necessary protocol.
   - Record one representative dataset/input, applicable split or evaluation boundary, primary metric/output, original-method command expectations, checkpoint/result source, and fairness invariants needed for later optimization.
   - Record optional broader paper resources separately; do not mark them required.

6. Write artifacts.
   - Include selected route, rejected alternatives, evidence, risks, adaptation obligations, and repository-fit requirements.
   - Mark `status: ready` only when repository search can judge candidates without inventing the baseline target.

## Plan Shape

```yaml
status: "ready" # ready | needs_user_confirmation | blocked
mode: "adopt_existing" # adopt_existing | adapt_existing | construct_minimal | undetermined
research_requirement_path: ""

minimum_reproduction:
  original_method_behavior: ""
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
  reference_target: ""
  expected_cost: ""

protocol:
  task_definition: ""
  split_or_evaluation_boundary: ""
  preprocessing_boundary: ""
  leakage_controls: []
  metric_direction: "unknown"
  fairness_invariants: []

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
- Use the original method's released checkpoint or result when it avoids unnecessary training and remains scientifically valid.
- Missing a full paper benchmark suite is not a blocker.
- A benchmark is invalid if it does not exercise the original method, cannot produce a meaningful result, leaks unavailable information, or cannot support later fair optimization comparison.
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
