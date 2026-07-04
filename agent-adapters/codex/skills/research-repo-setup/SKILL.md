---
name: research-repo-setup
description: Turn an open-ended natural-language research need into a structured experiment scope, use benchmark-selection as an external decision index, select the best credible experiment repository or repository combination against that benchmark contract, and materialize the approved primary runnable repository in a local workspace. Use when Codex must identify the research question, task type, method families, constraints, exclusions, and success criteria; obtain an evidence-backed benchmark plan; compare candidate repositories for officialness, benchmark fit, runnable evidence, resource cost, and suitability as the primary experiment base; then clone or reuse the selection, verify git remote, branch, and commit, record reference repositories, and hand one explicit runnable repository path to repo-onboard. This skill does not install dependencies, download datasets or checkpoints, run baselines, or modify experiment logic.
---

# Research Repo Setup

Use this skill as the single pre-onboarding stage for an open-ended research need. Perform research scoping, repository selection, and local workspace assembly in sequence, preserving an artifact checkpoint for each phase.

Execute the workflow interactively through Codex tool calls. Do not implement a separate Python or TypeScript pipeline.

## Terminal Output

Report only phase status, major decisions or approvals, artifact paths, the primary runnable repository path, blockers, and the next step. Put search evidence, candidate comparisons, git commands, and detailed decisions in the reports.

## Agent Contract

Roles:

- `AgentResearchFrame`: structure the research need.
- `AgentSelector`: compare candidates and select the experiment base.
- `AgentResource`: materialize and verify the local workspace.

Inputs:

- natural-language research need, hypothesis, topic, method idea, or desired comparison
- optional compute, runtime, data, license, framework, privacy, and download constraints
- optional paper, repository, benchmark, dataset, local path, or workspace root

Required outputs:

- `research_scope.yaml`
- `research_scope_report.md`
- `benchmark_plan.yaml` from `benchmark-selection`
- `benchmark_selection_report.md` from `benchmark-selection`
- `experiment_base_plan.yaml`
- `repo_selection_report.md`
- `workspace_manifest.yaml`
- `workspace_assembly_report.md`

Handoff:

- Hand exactly one primary runnable repository path from `workspace_manifest.yaml` to `repo-onboard`.
- Keep reference, benchmark, dataset, and component repositories as recorded context unless the approved plan requires local clones.

## Workflow

### Phase 1: Structure the research need

1. Normalize the request.
   - Record the original request and a concrete research question.
   - Identify task type, domain, input/output form, target evidence, and must-have versus preferred requirements.
   - Ask only when ambiguity would materially change the benchmark or repository search space.

2. Identify the experiment scope.
   - Record candidate method families, benchmark requirements, possible benchmark families, and success criteria.
   - Record compute and runtime limits, data and license policies, framework preferences, large-model or training restrictions, exclusions, and unresolved questions.
   - Do not finalize datasets, splits, metrics, or benchmark protocols inside this skill.

3. Write the scope checkpoint.
   - Write `research_scope.yaml` and `research_scope_report.md`.
   - Continue only when `benchmark-selection` can evaluate candidates without guessing the task or intended evidence.

4. Consult the benchmark index.
   - Invoke `benchmark-selection` with the research scope and constraints.
   - Require `benchmark_plan.yaml` and `benchmark_selection_report.md`.
   - Continue only when benchmark status is `ready`, or the user has approved and resolved a `needs_user_confirmation` decision.
   - Use the selected benchmark contract, protocol, fairness invariants, resource limits, and repository fit requirements as authoritative inputs to repository comparison.

### Phase 2: Select the experiment repository

5. Find candidates.
   - Search official paper links, author or lab pages, benchmark pages, GitHub organizations, package documentation, and credible benchmark libraries.
   - Classify candidates as `primary_repo`, `reference_repo`, `benchmark_tooling`, `dataset_tooling`, or `component_repo`.
   - Penalize stale mirrors, unrelated forks, missing paper or benchmark evidence, private-data dependencies, and closed-service requirements unless requested.

6. Compare candidates.
   - Evaluate officialness, task match, fit against `benchmark_plan.yaml`, documented evaluation commands, checkpoints or reproducible baselines, maintenance, license, dependency risk, framework/CUDA risk, expected downloads, training cost, and modification complexity.
   - Decide whether each candidate is suitable for full reproduction, a smoke baseline, benchmark tooling, data preparation, reference evidence, or component integration.
   - Treat benchmark fit and runnable evidence as more important than popularity.
   - Do not change the benchmark contract to make a preferred repository appear compatible.

7. Select the experiment base.
   - Use `single-repo` when one repository supplies the runnable method and benchmark path.
   - Use `primary-repo-with-references` when one repository runs experiments and others provide reference or comparison context.
   - Use `composed-workspace` only when the research need requires multiple repositories and their roles and integration points are concrete.
   - Ask before selecting an unofficial or medium/low-confidence primary repository, a surprising license or resource cost, similarly strong candidates, or a composed workspace.

8. Write the selection checkpoint.
   - Write `experiment_base_plan.yaml` and `repo_selection_report.md`.
   - Reference `benchmark_plan.yaml` and record any repository-side adapter or evaluator obligations it requires.
   - Continue only when `selection_status` is `ready`, or the user has approved a `needs_user_confirmation` plan.

### Phase 3: Materialize the workspace

9. Choose the local layout.
   - Prefer the task run directory or a user-provided workspace root.
   - Otherwise use an established project-local repository root.
   - Use stable repository-derived directory names and never overwrite an existing directory.

10. Clone or reuse repositories.
   - Clone or reuse the selected primary repository.
   - When a target exists, verify it is a Git repository and that its remote matches the selected URL before reuse.
   - If the existing path has a different remote or is not a Git repository, stop and ask.
   - Record reference repositories without cloning them by default. Clone them only when the approved plan requires local benchmark, component, or composed-workspace content.
   - Clone only repositories recorded in the approved selection plan.

11. Verify repository identity.
    - Record the primary repository URL, absolute local path, role, clone/reuse status, verified remote, current branch, and exact commit.
    - For each local supporting repository, record the same Git identity fields and its non-primary role.
    - For `composed-workspace`, create the top-level layout only after approval and do not copy or merge source code.

12. Write the workspace checkpoint.
    - Write `workspace_manifest.yaml` and `workspace_assembly_report.md`.
    - Mark the workspace `ready` only when the primary path exists, its remote matches the approved selection, and branch and commit are recorded.
    - Make `handoff.repo_path` the single explicit primary runnable repository path for `repo-onboard`.

## Artifact Shapes

### `research_scope.yaml`

```yaml
research_need:
  original_request: ""
  normalized_question: ""
  task_type: ""
  domain: ""
  expected_evidence: ""

constraints:
  compute: ""
  runtime: ""
  data_policy: ""
  framework_preferences: []
  license_constraints: []
  exclusions: []

method_families: []
benchmark_space:
  requirements: []
  candidate_families: []
  unresolved_choices: []

selection_criteria:
  must_have: []
  nice_to_have: []
  risk_flags: []

success_criteria: []
open_questions: []
evidence: []
benchmark_handoff:
  next_skill: "benchmark-selection"
  required_artifact: "benchmark_plan.yaml"
next_skill: "research-repo-setup"
```

### `experiment_base_plan.yaml`

```yaml
research_scope_path: ""
benchmark_plan_path: ""
selection_status: "ready" # ready | needs_user_confirmation | blocked
base_shape: "single-repo" # single-repo | primary-repo-with-references | composed-workspace

selected:
  primary_repo:
    url: ""
    role: "primary_repo"
    confidence: "high" # high | medium | low
    officialness: ""
    rationale: ""
    benchmark_fit: ""
    runnable_evidence: []
    risks: []
  reference_repos: []
  benchmark_or_dataset_repos: []
  component_repos: []

candidates: []
benchmark_decision:
  source: "benchmark-selection"
  datasets: []
  metrics: []
  protocol: ""
  baseline_targets: []
  repository_fit_requirements: []

assembly_plan:
  clone_required: true
  expected_repo_root: ""
  reference_clone_required: false
  composed_workspace_required: false
  notes: ""

open_questions: []
evidence: []
next_skill: "research-repo-setup"
```

### `workspace_manifest.yaml`

```yaml
experiment_base_plan_path: ""
assembly_status: "ready" # ready | partial | blocked
base_shape: "single-repo" # single-repo | primary-repo-with-references | composed-workspace

workspace_root: ""
primary_repo:
  url: ""
  local_path: ""
  role: "primary_repo"
  clone_status: "cloned" # cloned | reused | existing_mismatch | blocked
  remote_verified: false
  branch: ""
  commit: ""
  runnable_root: true

reference_repos: []
benchmark_or_dataset_repos: []
component_repos: []

handoff:
  next_skill: "repo-onboard"
  repo_path: ""
  notes: ""

warnings: []
evidence: []
```

## Decision Rules

- If the request names one exact paper and primarily asks for its official code, use `paper-repo-discovery`.
- If the request already names an existing local repository and does not require candidate comparison, hand it directly to `repo-onboard`.
- Prefer a narrow executable scope and a credible single primary repository over unnecessary composition.
- Use `benchmark-selection` as the source of truth for dataset, split, metric, protocol, and benchmark-construction decisions.
- Do not proceed from one phase merely on conversational confidence; verify its required artifacts and status.
- Do not let supporting repositories obscure the single primary runnable path.

## Boundaries

Do:

- structure the research requirement and benchmark scope
- invoke and consume the external benchmark decision index
- compare and select credible repositories
- clone or reuse only approved repositories
- verify remote, branch, commit, role, and primary runnable path
- preserve the three artifact checkpoints for audit and resumption

Do not:

- install dependencies or create environments
- independently finalize or silently alter benchmark datasets, splits, metrics, or protocol
- download datasets, checkpoints, or pretrained models outside normal Git clone contents
- run baseline, evaluation, or training commands
- modify, merge, or adapt experiment source code
- overwrite existing directories or silently switch the selected repository
