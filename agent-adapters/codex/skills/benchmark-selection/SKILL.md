---
name: benchmark-selection
description: Select, adapt, or specify a benchmark for a research experiment as an external decision index used by the normal research workflow. Use when Codex must translate a research requirement into a benchmark contract; compare existing datasets, protocols, metrics, splits, baselines, and evaluation tooling; determine whether an established benchmark can be adopted directly, requires a scientifically safe adaptation, or must be constructed from available data; define leakage controls, comparability rules, resource limits, and acceptance criteria; and write benchmark_plan.yaml plus benchmark_selection_report.md for repository selection and later experiment preparation. This skill does not select the primary experiment repository, clone code, download data, implement adapters, or run experiments.
---

# Benchmark Selection

Use this skill as an external benchmark decision index. Produce the benchmark contract that repository selection and later experiment stages must follow; do not own the main workflow sequence.

Read [references/benchmark-criteria.md](references/benchmark-criteria.md) before making a benchmark decision. Apply its hard gates, comparison rubric, construction standard, and readiness rules.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<run_dir>/experiment_artifacts/`. Write `benchmark_plan.yaml` under `plans/`, `benchmark_selection_report.md` under `reports/`, and supporting evidence or logs under `evidence/` or `logs/`. Do not place these auxiliary files in the repository root. Bare artifact filenames below refer to these categorized paths.

## Terminal Output

Report only the decision mode, selected or proposed benchmark, approval needs, artifact paths, blockers, and handoff. Put candidate evidence, scorecards, rejected alternatives, protocol details, and leakage analysis in the report.

## Agent Contract

Advisory role: `BenchmarkIndex`

Inputs:

- natural-language research need or `research_scope.yaml`
- task definition, input and target modalities, domain, population, and expected evidence
- constraints on data, license, privacy, compute, runtime, framework, downloads, and external services
- optional candidate datasets, benchmarks, evaluation suites, repositories, or local data

Required outputs:

- `benchmark_plan.yaml`
- `benchmark_selection_report.md`

Handoff:

- Return the benchmark mode and protocol to `research-repo-setup` for repository comparison.
- Treat `benchmark_plan.yaml` as the source of truth for benchmark fit; downstream artifacts may summarize it but must reference its path.
- If the benchmark cannot be determined without a scientifically meaningful user choice, record `status: needs_user_confirmation` and stop before repository selection.

## Workflow

1. Define the benchmark contract.
   - Translate the research question into task unit, inputs, targets, prediction or decision point, population/domain, temporal or spatial scope, expected output, and intended claim.
   - Separate hard requirements from preferences.
   - Define what the benchmark must measure and what evidence would count as success.
   - Record prohibited shortcuts, leakage risks, unavailable data, and resource ceilings.

2. Search benchmark candidates.
   - Search official benchmark pages, dataset publishers, original papers, evaluation repositories, leaderboards, and maintained task libraries.
   - Verify current availability, provenance, license, version, split definitions, metrics, evaluation code, baseline coverage, and known limitations from primary sources.
   - Include a custom benchmark candidate when no existing benchmark plausibly covers the required task.

3. Evaluate candidates.
   - Apply every hard gate in the criteria reference before scoring convenience or popularity.
   - Compare task and protocol fit, data validity, split and leakage safety, metric validity, baseline and tooling support, reproducibility, resource feasibility, maintenance, and scientific usefulness.
   - Record uncertainty and evidence for each judgment. Do not hide a failed hard gate inside an aggregate score.

4. Choose the benchmark mode and status.
   - Choose `adopt_existing` when an established benchmark satisfies the research contract without changing its scientific meaning.
   - Choose `adapt_existing` when the data or protocol is suitable but a bounded adapter, modality alignment, split correction, metric addition, or local evaluation wrapper is required.
   - Choose `construct_new` when no existing benchmark can test the required claim without material mismatch or invalid assumptions.
   - Set `status: needs_user_confirmation` and leave `mode: undetermined` when multiple defensible choices imply different scientific claims, costs, licenses, or data policies.
   - Set `status: blocked` and leave `mode: undetermined` when required data, labels, legal access, or a valid evaluation design cannot be established.

5. Freeze the evaluation protocol.
   - Specify dataset and version, task unit, target, features, eligibility rules, preprocessing boundaries, train/validation/test split, temporal cutoff, horizons, metrics and direction, aggregation, uncertainty reporting, baseline families, seeds, compute budget, and allowed tuning.
   - State which fields are fixed for fairness and which may vary during method development.
   - For adapted or constructed benchmarks, define provenance, alignment, deduplication, leakage checks, missing-data policy, versioning, and acceptance tests.

6. Write artifacts.
   - Write `benchmark_plan.yaml` and `benchmark_selection_report.md` beside the research scope artifacts.
   - Include candidate scorecards, selected mode, rationale, rejected candidates, evidence links, unresolved risks, required user approvals, and downstream implementation obligations.
   - Mark `status: ready` only when repository selection can evaluate benchmark fit without inventing datasets, metrics, splits, or success criteria.

## `benchmark_plan.yaml` Shape

```yaml
status: "ready" # ready | needs_user_confirmation | blocked
mode: "adopt_existing" # adopt_existing | adapt_existing | construct_new | undetermined
research_scope_path: ""

benchmark_contract:
  research_question: ""
  intended_claim: ""
  task_type: ""
  task_unit: ""
  inputs: []
  targets: []
  domain_or_population: ""
  expected_evidence: ""
  hard_requirements: []
  preferences: []
  exclusions: []
  resource_limits: {}

candidates:
  - name: ""
    version: ""
    source: ""
    mode: "adopt_existing"
    hard_gates:
      task_protocol_fit: "pass"
      lawful_access: "pass"
      data_provenance: "pass"
      split_leakage_safety: "pass"
      metric_validity: "pass"
      runnable_evaluation_path: "pass"
    comparison: {}
    decision: "selected" # selected | backup | rejected | needs_user_confirmation
    rationale: ""
    evidence: []

selected_benchmark:
  name: ""
  version: ""
  source: ""
  mode: "adopt_existing"
  rationale: ""

protocol:
  datasets: []
  task_definition: ""
  eligibility_and_filtering: ""
  preprocessing_boundary: ""
  split_strategy: ""
  temporal_cutoff: ""
  horizons: []
  primary_metrics: []
  secondary_metrics: []
  metric_aggregation: ""
  uncertainty_reporting: ""
  baseline_families: []
  seeds: []
  tuning_policy: ""
  compute_budget: ""

construction_or_adaptation:
  required: false
  source_data: []
  transformations: []
  modality_or_time_alignment: ""
  deduplication: ""
  missing_data_policy: ""
  leakage_controls: []
  versioning: ""
  implementation_obligations: []
  acceptance_tests: []

fairness_invariants: []
open_questions: []
user_approval:
  required: false
  status: "not_required" # not_required | pending | approved | rejected
evidence: []
handoff:
  next_skill: "research-repo-setup"
  repository_fit_requirements: []
```

## Decision Rules

- Prefer an established benchmark only when it actually tests the intended claim.
- Prefer adaptation over construction when the scientific protocol can remain valid and the required change is bounded and auditable.
- Construct a benchmark only from traceable data and a frozen evaluation contract; do not call an arbitrary dataset plus one metric a benchmark.
- Require user approval before changing the scientific claim, data population, labels, split semantics, primary metrics, or resource class.
- Keep benchmark choice independent from repository popularity. Select repositories against the benchmark contract, not the reverse.
- Treat smoke subsets as pipeline validation only; never substitute them for the formal benchmark.

## Boundaries

Do:

- select, adapt, or specify a benchmark
- define datasets, splits, metrics, baselines, fairness invariants, leakage controls, and acceptance criteria
- create an evidence-backed benchmark contract for downstream repository selection

Do not:

- select or clone the primary experiment repository
- download or transform full datasets
- implement benchmark adapters or evaluation code
- install dependencies or create environments
- run smoke, baseline, or formal experiments
