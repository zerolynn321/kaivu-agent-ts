---
name: experiment-workspace-assembly
description: Materialize a selected experiment base into a local workspace after experiment-repo-selection has produced an experiment_base_plan.yaml. Use when Codex must clone or reuse the selected primary repository, optionally clone reference or benchmark repositories, create a composed workspace directory when approved, verify remotes and repository roles, and write workspace_manifest.yaml plus an assembly report before handing the primary runnable repository to repo-onboard. This skill does not install dependencies, download datasets/checkpoints beyond repository clone, run baselines, or modify experiment logic.
---

# Experiment Workspace Assembly

Use this skill to turn an approved experiment base plan into local repository paths that the existing repo initialization skills can consume.

The agent performs workspace assembly directly. Do not implement a separate Python or TypeScript pipeline for this logic.

## Terminal Output

Keep terminal-facing progress concise. Report only stage status, clone/reuse decisions, artifact paths, blockers, and next step. Put detailed remotes, evidence, command notes, and file layout in `workspace_assembly_report.md`.

## Agent Contract

Role: `AgentResource`

Inputs:

- `experiment_base_plan.yaml`
- optional `repo_selection_report.md`
- optional user-approved target root for repository clones
- optional existing local repository paths

Required outputs:

- `workspace_manifest.yaml`
- `workspace_assembly_report.md`

Handoff:

- Hand the primary runnable repository path to `repo-onboard`.
- Reference repositories are context for onboarding and later reports; they are not automatically treated as runnable targets.

## Workflow

1. Read and validate the experiment base plan.
   - Confirm `selection_status` is `ready`, or that the user has approved a `needs_user_confirmation` plan.
   - Confirm base shape: `single-repo`, `primary-repo-with-references`, or `composed-workspace`.
   - Stop and ask before assembling an unapproved composed workspace or cloning a medium/low-confidence selected repository.

2. Choose local layout.
   - Prefer a task run directory when one exists.
   - Otherwise use a clear repository root such as `laboratory/paper_repos` or a user-approved project-local root.
   - Use stable, readable folder names derived from repository names.
   - Never overwrite or delete an existing directory.

3. Clone or reuse repositories.
   - For each required repository, check whether the target path exists.
   - If the path exists and its remote matches the selected URL, reuse it.
   - If the path exists with a different remote or is not a git repository, ask the user before proceeding.
   - Clone only repositories included in the selected assembly plan.
   - After clone or reuse, verify remote URL, branch, recent commit, and key README or citation evidence when available.

4. Assemble workspace shape.
   - For `single-repo`, mark the primary repository as the runnable root.
   - For `primary-repo-with-references`, clone or record reference repositories under a sibling or `references/` directory and mark them non-runnable by default.
   - For `composed-workspace`, create a top-level workspace directory only after user approval and record exact roles for each child repository.
   - Do not copy source files between repositories or merge code unless the user explicitly approves a later integration task.

5. Write artifacts.
   - Create `workspace_manifest.yaml`.
   - Create `workspace_assembly_report.md`.
   - Include selected plan path, local paths, repository roles, clone/reuse status, remote verification, unresolved risks, and next handoff.

## `workspace_manifest.yaml` Shape

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

- Mark `assembly_status: ready` only when the primary runnable repository path exists and its remote matches the selected plan.
- Mark `partial` when reference repositories are missing but the primary repository is ready and references are not required for onboarding.
- Mark `blocked` when the primary repository cannot be safely cloned or reused.
- Do not let reference repositories obscure the handoff path; `repo-onboard` receives one primary runnable repository.

## Boundaries

Do:

- clone or reuse selected repositories
- create a local workspace layout
- verify git remotes and roles
- write workspace assembly artifacts
- hand off the primary repo to `repo-onboard`

Do not:

- install dependencies or create virtual environments
- download datasets, checkpoints, or pretrained models outside normal git clone contents
- run baseline or evaluation commands
- copy, merge, or modify experiment source code
- overwrite existing directories or silently switch repository selections
