---
name: experiment-repo-search
description: Turn an open-ended natural-language research requirement into a structured minimum-reproduction contract, consult benchmark-selection as an auxiliary decision index, find and compare credible repositories, select the smallest repository base that can reproduce the original method on one representative dataset or official pretrained evaluation path, clone or reuse the selected repositories, and hand the local workspace to repo-experiment-fix. Use after research-experiment-init for requirement-driven repository discovery. This skill does not install dependencies, acquire non-Git runtime resources, modify source code, or run the baseline.
---

# Experiment Repo Search

Use this skill as the repository-discovery stage for an open-ended research requirement. Structure the requirement, choose a minimal credible reproduction target, select the repository base, and materialize the selected Git repositories.

Do not implement a separate Python or TypeScript orchestration pipeline. Perform search and decisions interactively and preserve evidence in artifacts.

## Project Definition

This project does not require complete paper reproduction. The target is a **minimum reproducible optimization base**:

- the original method is present and identifiable;
- one representative public dataset, bundled example, saved result, or official pretrained checkpoint path is sufficient;
- the selected path produces the method's meaningful output or metric;
- the result can serve as the unchanged baseline for later optimization;
- all datasets, all paper tables, all seeds, full retraining, and appendix experiments are unnecessary unless the user explicitly requests them.

Prefer official pretrained evaluation or released results over expensive retraining when they provide a valid original-method baseline.

## Artifact Location

Use the coordinator-provided `artifact_root`, or default to `<run_dir>/experiment_artifacts/`.

- plans: `research_requirement.yaml`, `experiment_repo_plan.yaml`
- auxiliary benchmark plan: `benchmark_plan.yaml`
- manifests: `workspace_manifest.yaml`
- reports: `experiment_repo_search_report.md`
- evidence and logs: supporting search and Git evidence

Do not scatter workflow artifacts across repository roots.

## Agent Contract

Role: `AgentRepoSearch`

Inputs:

- natural-language research requirement
- optional paper, repository, dataset, benchmark, framework, compute, license, or download constraints
- optional run directory or workspace root

Required outputs:

- `<artifact_root>/plans/research_requirement.yaml`
- `<artifact_root>/plans/benchmark_plan.yaml` from `benchmark-selection`
- `<artifact_root>/reports/benchmark_selection_report.md` from `benchmark-selection`
- `<artifact_root>/plans/experiment_repo_plan.yaml`
- `<artifact_root>/manifests/workspace_manifest.yaml`
- `<artifact_root>/reports/experiment_repo_search_report.md`

Handoff:

- Hand all selected local repository paths and one proposed primary root to `repo-experiment-fix`.
- Do not hand directly to `repo-onboard`; `repo-experiment-fix` must explicitly confirm either `modified`, `integrated`, or `no_change_required`.

## Workflow

1. Structure the requirement.
   - Preserve the original request.
   - Record the research question, task, input/output, intended optimization, must-have requirements, exclusions, and resource limits.
   - Ask only when ambiguity changes scientific meaning, repository class, data access, or resource class.

2. Define the minimum reproduction contract.
   - Identify the original-method behavior that must be observable before optimization.
   - Select the smallest scientifically meaningful evidence unit: normally one representative dataset and one primary metric or output.
   - Accept an official pretrained checkpoint, released prediction/result file, evaluation-only route, or short documented training route.
   - Do not require full retraining when an official pretrained route establishes the baseline.
   - Do not require every dataset, horizon, seed, comparison, table, or ablation from a paper.
   - Reject a trivial import check or unrelated toy demo that does not exercise the original method.
   - Invoke `benchmark-selection` as an auxiliary decision after the requirement is structured.
   - Require `benchmark_plan.yaml` to identify the representative dataset/input, route, metric/output, protocol boundary, and repository-fit requirements.
   - Treat the benchmark plan as evidence for repository comparison, not as an extra top-level workflow stage.

3. Search candidate repositories and benchmark resources.
   - Search official paper/project pages, author or lab pages, GitHub organizations, benchmark pages, package documentation, and credible maintained implementations.
   - Classify each candidate as `primary_repo`, `component_repo`, `reference_repo`, `dataset_repo`, or `benchmark_tooling`.
   - Verify officialness, paper/task identity, license, runnable evidence, available checkpoints/results, representative dataset support, dependencies, hardware cost, and modification/integration cost.

4. Compare candidates against the requirement.
   - Prioritize requirement fit, minimum-reproduction evidence, and optimization suitability over popularity.
   - Check whether the original method can produce a meaningful result without unnecessary full-paper training.
   - Check whether the code exposes the model, retrieval, graph, data, evaluator, or other extension point needed by the future optimization.
   - Record rejected candidates and concrete reasons.

5. Choose the smallest adequate repository base.
   - Use `single-repo` when one repository already satisfies the requirement.
   - Use `primary-repo-with-support` when one runnable repository needs reference, data, evaluator, or small adapter support.
   - Use `composed-workspace` only when multiple repositories or components are genuinely required.
   - Do not force repository composition when one repository plus a bounded adapter is sufficient.
   - Ask before an unofficial or low-confidence primary repository, unclear licensing, large downloads, private services, or materially different candidate choices.

6. Clone or reuse selected repositories.
   - Use the run directory or user-provided workspace root.
   - Never overwrite an existing path.
   - Reuse an existing repository only when its remote matches the selected source.
   - Verify and record URL, absolute path, remote, branch, commit, role, and clone/reuse status.
   - Clone only repositories needed by the selected plan.

7. Write and verify artifacts.
   - Record the structured requirement, minimum reproduction contract, candidate comparison, selected roles, expected modification/integration work, and local workspace.
   - Set `search_status: ready` only when the selected local source base is sufficient for `repo-experiment-fix` to inspect and adapt without guessing the research goal.

## Artifact Shapes

### `research_requirement.yaml`

```yaml
original_request: ""
normalized_question: ""
task_type: ""
domain: ""
optimization_goal: ""
must_have: []
preferred: []
exclusions: []
resource_constraints: {}
minimum_reproduction:
  original_method_behavior: ""
  representative_dataset_or_input: ""
  primary_metric_or_output: ""
  acceptable_route: "pretrained_eval" # pretrained_eval | released_result_eval | documented_training | bundled_example
  reference_target: ""
  unnecessary_scope: []
open_questions: []
```

### `experiment_repo_plan.yaml`

```yaml
search_status: "ready" # ready | needs_user_confirmation | blocked
base_shape: "single-repo" # single-repo | primary-repo-with-support | composed-workspace
research_requirement_path: ""
benchmark_plan_path: ""
selected:
  primary_repo:
    url: ""
    role: "primary_repo"
    confidence: "high"
    officialness: ""
    requirement_fit: ""
    minimum_reproduction_evidence: []
    optimization_extension_points: []
    risks: []
  support_repos: []
candidates: []
minimum_reproduction_contract:
  dataset_or_input: ""
  command_evidence: ""
  metric_or_output: ""
  reference_source: ""
  pretrained_or_released_assets: []
expected_repo_fix:
  required: false
  reasons: []
  proposed_changes_or_integrations: []
evidence: []
next_skill: "repo-experiment-fix"
```

### `workspace_manifest.yaml`

```yaml
search_status: "ready"
workspace_root: ""
base_shape: "single-repo"
primary_repo:
  url: ""
  local_path: ""
  remote_verified: false
  branch: ""
  commit: ""
  role: "primary_repo"
support_repos: []
handoff:
  next_skill: "repo-experiment-fix"
  proposed_primary_path: ""
warnings: []
```

## Decision Rules

- A repository is not suitable merely because its README uses similar keywords.
- Use `benchmark-selection` as the auxiliary source of truth for the representative dataset/input and minimum evaluation protocol.
- A minimum reproduction must exercise the original method and produce a meaningful result suitable as an optimization baseline.
- One representative dataset is enough when it provides a valid original-method result.
- Prefer released checkpoints and evaluation-only paths over unnecessary expensive retraining.
- Prefer the smallest credible repository base and lowest-risk adaptation.
- Preserve uncertainty and ask only for decisions that materially affect the experiment.

## Boundaries

Do:

- structure the research requirement
- define the minimum reproduction contract
- invoke and consume the auxiliary benchmark decision
- search and compare repositories and benchmark resources
- clone or reuse selected Git repositories
- preserve provenance and hand all local paths to `repo-experiment-fix`

Do not:

- install dependencies or create environments
- download datasets, checkpoints, or model caches outside normal Git clone contents
- modify or integrate source code
- run baseline, evaluation, or training
- require complete paper reproduction when a valid minimum result is sufficient
