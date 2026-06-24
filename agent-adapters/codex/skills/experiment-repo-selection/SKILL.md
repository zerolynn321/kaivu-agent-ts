---
name: experiment-repo-selection
description: Find, compare, and select the best experiment repository or repository combination for a scoped research need. Use after research-scope-planning or whenever Codex has a research_scope.yaml and must search official and credible repositories, evaluate benchmark fit, runnable evidence, resource risk, maintenance, license, and integration cost, then decide whether to use a single repository, a primary repository with references, or a composed workspace. This skill asks for user confirmation when candidates are ambiguous or risky; it does not clone, install dependencies, download resources, or run baselines.
---

# Experiment Repo Selection

Use this skill to choose the experiment base for a research need before any local repository assembly.

The agent performs repository discovery and selection directly. Do not implement a separate Python or TypeScript pipeline for this logic.

## Terminal Output

Keep terminal-facing progress concise. Report only stage status, major candidate decisions, approval needs, artifact paths, and next step. Put candidate tables, URLs, evidence, and risk notes in `repo_selection_report.md`.

## Agent Contract

Role: `AgentSelector`

Inputs:

- `research_scope.yaml`
- optional `research_scope_report.md`
- optional user-provided candidate repositories, papers, benchmark names, or exclusions

Required outputs:

- `experiment_base_plan.yaml`
- `repo_selection_report.md`

Handoff:

- If a selected local workspace already exists, hand off to `repo-onboard`.
- If repositories must be cloned or assembled, hand off to `experiment-workspace-assembly`.
- If the best input is one specific paper with one official repo, hand off to `paper-repo-discovery` when that simpler path is sufficient.

## Workflow

1. Read the research scope.
   - Verify task type, benchmark expectations, must-have criteria, exclusions, and open questions.
   - If the scope is missing or too vague, ask for clarification or run `research-scope-planning` first.

2. Search candidate repositories.
   - Use live lookup for repository status, official links, recent maintenance, license, issues, releases, and benchmark coverage.
   - Search from papers, benchmark pages, leaderboards, author pages, lab pages, GitHub organizations, Papers with Code, package docs, and curated benchmark libraries.
   - Separate candidates into `primary_repo`, `reference_repo`, `benchmark_tooling`, `dataset_tooling`, and `component_repo`.
   - Penalize forks, stale mirrors, unrelated homonyms, repos without paper or benchmark evidence, and repos that require private data or closed services unless the user requested them.

3. Evaluate benchmark fit.
   - Check whether each candidate supports the target task, datasets, metrics, evaluation protocol, and baseline comparison needed by the research scope.
   - Prefer repositories with documented eval scripts, pretrained checkpoints or reproducible baseline commands, public data preparation, and reference results.
   - Record whether the repo is best for full reproduction, smoke testing, benchmark harness, dataset preparation, or component integration.

4. Evaluate runnable and integration risk.
   - Inspect public repo files when available: README, requirements, environment files, scripts, configs, docs, examples, licenses, issues, and releases.
   - Estimate dependency risk, CUDA/framework risk, expected download size, expected runtime, and modification complexity.
   - Do not clone or run the repo in this skill.

5. Select experiment base shape.
   - Use `single-repo` when one repository contains the method, benchmark, data procedure, metrics, and baseline command.
   - Use `primary-repo-with-references` when one repository should run experiments and other repositories only provide reference baselines, preprocessing ideas, or comparison evidence.
   - Use `composed-workspace` only when no single repository can satisfy the scope and the integration plan is concrete enough to audit.
   - Ask the user before selecting a medium-confidence repo, an unofficial reproduction, a composed workspace, a repo with heavy resources, or multiple similarly strong candidates.

6. Write artifacts.
   - Create `experiment_base_plan.yaml`.
   - Create `repo_selection_report.md`.
   - Include selected repository URLs, roles, selection rationale, rejected candidates, risk flags, user decisions, and handoff target.

## `experiment_base_plan.yaml` Shape

```yaml
research_scope_path: ""
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

candidates:
  - url: ""
    role: ""
    confidence: ""
    officialness: ""
    benchmark_fit: ""
    runnable_risk: ""
    decision: "selected" # selected | backup | rejected | needs_user_confirmation
    rationale: ""

benchmark_decision:
  datasets: []
  metrics: []
  protocol: ""
  baseline_targets: []

assembly_plan:
  clone_required: true
  expected_repo_root: ""
  reference_clone_required: false
  composed_workspace_required: false
  notes: ""

open_questions: []
evidence: []
next_skill: "experiment-workspace-assembly"
```

## Decision Rules

- Select a repository only when it is credible enough to justify local work and matches the scoped benchmark.
- Prefer official repositories over unofficial reproductions when both are runnable enough.
- Prefer a simpler single-repo base unless the research need truly requires composition.
- Treat benchmark fit as more important than GitHub stars.
- Ask before selecting any repo whose license, data access, download size, runtime, or integration cost could surprise the user.

## Boundaries

Do:

- search and compare repositories
- evaluate benchmark fit and runnable risk
- choose experiment base shape
- write selection artifacts for later audit
- ask for user confirmation when selection is ambiguous or risky

Do not:

- clone repositories
- edit source code
- download datasets or checkpoints
- install dependencies or create environments
- run baseline commands
- hide integration risk behind an overconfident recommendation
