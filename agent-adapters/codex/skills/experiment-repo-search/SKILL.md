---
name: experiment-repo-search
description: Turn an open-ended natural-language research requirement into a structured minimum controlled experiment contract, consult benchmark-selection as an auxiliary decision index, find and compare credible repositories, select the repository base that best satisfies the research need and can answer the question on one representative benchmark, clone or reuse selected repositories in an isolated workspace, and hand the local workspace to repo-experiment-fix. Use after research-experiment-init for requirement-driven repository discovery, including cases where Codex must decide between single-repo modification, primary-repo-with-support, or composed-workspace integration. Comparative questions need the minimum necessary branches, but not every open-ended requirement is a comparison. This skill does not install dependencies, acquire non-Git runtime resources, modify source code, or run the baseline.
---

# Experiment Repo Search

Use this skill as the repository-discovery stage for an open-ended research requirement. Structure the requirement, choose a minimal credible reproduction target, select the repository base, and materialize the selected Git repositories.

Do not implement a separate Python or TypeScript orchestration pipeline. Perform search and decisions interactively and preserve evidence in artifacts.

## Project Definition

This project does not require complete paper reproduction. The target is a **minimum reproducible optimization base**.

For an open-ended research requirement, the baseline target is not merely "the chosen method runs." It is at least one smallest controlled experiment that can answer the user's question before later optimization. Use one representative benchmark when enough. Include control, treatment, ablation, or reference branches only when the question is comparative or the claim cannot otherwise be answered.

Do not optimize only for lowest engineering risk. First satisfy the user's research intent and test intent, then choose the smallest credible implementation among the plans that satisfy it. If the user is explicitly testing repository integration or asks Codex to decide whether integration is needed, evaluate real external component repositories before falling back to a self-written lightweight substitute.

The selected contract must ensure:

- the original method is present and identifiable;
- one representative public dataset, bundled example, saved result, or official pretrained checkpoint path is sufficient;
- the selected path produces the meaningful metric or output needed for the minimum controlled experiment;
- the result, or comparison result when branches are required, can serve as the unchanged baseline contract for later optimization;
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
   - Record any evaluation intent in the request, such as testing repository search, repository integration, source adaptation, benchmark construction, or error recovery.
   - Treat an explicit integration-test intent as a requirement to fairly evaluate multi-repository options, not as a requirement to force integration when a single repository genuinely fits better.
   - Ask only when ambiguity changes scientific meaning, repository class, data access, or resource class.

2. Define the minimum controlled experiment contract.
   - Identify the research question type: single-method reproduction, on/off effect, method/control comparison, component ablation, or model-family comparison.
   - Identify the original-method behavior that must be observable before optimization.
   - For comparative requirements, identify the smallest control, treatment, ablation, or reference branch set needed to answer the question.
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
   - When the requirement naturally decomposes into producer and consumer components, search for both roles before choosing a base shape.
   - For integration-oriented tests, include at least one credible external component repository as a candidate when such repositories exist, even if a simpler local reimplementation seems possible.

4. Compare candidates against the requirement.
   - Prioritize requirement fit, minimum-reproduction evidence, and optimization suitability over popularity.
   - Prioritize user-stated test intent over engineering convenience when they conflict.
   - Check whether the repository can produce the minimum controlled experiment without unnecessary full-paper training.
   - For comparative requirements, reject candidates that only run one branch unless a bounded adapter or switch can create the missing control without changing scientific meaning.
   - Check whether the code exposes the model, retrieval, graph, data, evaluator, or other extension point needed by the future optimization.
   - If rejecting a component repository in favor of a self-written fallback, record a concrete reason such as incompatible interface, unusable license, missing runnable code, excessive resource cost, unavailable dependency, or mismatch with the scientific target.
   - Record rejected candidates and concrete reasons.

5. Choose the best-fitting repository base.
   - Use `single-repo` when one repository already satisfies the research need, minimum controlled experiment, and user-stated test intent.
   - Use `primary-repo-with-support` when one runnable repository needs reference, data, evaluator, or small adapter support.
   - Use `composed-workspace` when multiple repositories or components are required to faithfully satisfy the research need, or when the user's integration-test intent would be bypassed by a self-written substitute despite a credible external component being available.
   - Do not force repository composition when one repository genuinely satisfies both the research question and the user's test intent.
   - Do not avoid repository composition merely because a small fallback script would be lower risk.
   - Ask before an unofficial or low-confidence primary repository, unclear licensing, large downloads, private services, or materially different candidate choices.

6. Clone or reuse selected repositories.
   - Use the run directory or user-provided workspace root.
   - Never overwrite an existing path.
   - If reusing an existing local repository, create an isolated copy for this run before any later modification or onboarding, unless the user explicitly asks to operate in place.
   - Reuse an existing repository as a source only when its remote matches the selected source.
   - Tell the user the original local path, isolated copy path, and that the original repository will not be modified.
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
test_intent:
  search_required: true
  integration_evaluation_required: false
  source_adaptation_expected: false
minimum_reproduction:
  original_method_behavior: ""
  baseline_kind: "single_method" # single_method | controlled_comparison
  representative_dataset_or_input: ""
  primary_metric_or_output: ""
  acceptable_route: "pretrained_eval" # pretrained_eval | released_result_eval | documented_training | bundled_example
  required_branches: []
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
base_shape_decision:
  chosen_shape: "single-repo"
  alternatives_considered:
    - shape: "composed-workspace"
      reason_rejected: ""
  self_written_fallback_used: false
  fallback_justification: ""
minimum_reproduction_contract:
  baseline_kind: "single_method" # single_method | controlled_comparison
  dataset_or_input: ""
  branches:
    - name: ""
      role: "treatment" # treatment | control | reference
      command_evidence: ""
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
- A minimum reproduction for a paper/repository route must exercise the original method and produce a meaningful result suitable as an optimization baseline.
- A minimum baseline for an open-ended requirement must be the smallest controlled experiment that answers the user's research question.
- Comparative requirements must include the control, treatment, ablation, or reference branch needed to answer the user's question.
- One representative dataset is enough when it provides a valid original-method result.
- Prefer released checkpoints and evaluation-only paths over unnecessary expensive retraining.
- Prefer the smallest credible repository base only after it satisfies the research question and user-stated test intent.
- For integration-oriented tests, do not replace a credible component repository with a self-written lightweight fallback unless the component is demonstrably unsuitable and the reason is recorded.
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
