---
name: research-experiment-init
description: Orchestrate the full Agent + Skill workflow from a natural-language research need to a runnable local baseline initialization. Use when Codex is asked to find suitable open-source experiment repositories, choose or assemble a benchmark base, prepare the repository, resources, environment, and baseline for a research goal rather than being given one exact paper repository. This skill routes to research-scope-planning, experiment-repo-selection, experiment-workspace-assembly, repo-onboard, repo-resource-prepare, repo-environment-setup, repo-baseline-run, and agent-fix-error-recovery as needed; it does not replace those skills or implement a separate Python pipeline.
---

# Research Experiment Init

Use this skill as the natural-language entrypoint for a full research-demand-to-baseline workflow.

The agent acts as the coordinator. Do not implement a separate Python or TypeScript pipeline for this logic. Invoke the existing Codex skills interactively and use their artifacts to decide whether each stage is complete.

## Natural User Inputs

Trigger this skill for requests such as:

- "I want to study whether method X improves task Y. Find a repo and run a baseline."
- "Help me find a suitable open-source benchmark and initialize a local experiment."
- "I have a research idea; choose the right repository and prepare it for experiments."
- "Find a reproducible baseline for this research direction."

If the user gives one specific paper, arXiv URL, DOI, PDF, or explicit repository target, prefer the shorter paper/repo workflow instead of the open-ended research-demand workflow.

## Terminal Output

Keep terminal-facing progress concise. Report only:

- current stage started or completed
- artifact path created or reused
- user decision needed
- blocker and recovery stage
- final baseline readiness summary

Put detailed commands, evidence, candidate tables, logs, and diffs in the stage report files produced by the delegated skills.

## Agent Contract

Role: `AgentCoordinator`

Inputs:

- natural-language research need
- optional constraints such as compute budget, dataset policy, preferred framework, runtime, or avoidance of large downloads
- optional task run directory or workspace preference

Primary outputs are produced by delegated skills:

- `research_scope.yaml`
- `experiment_base_plan.yaml`
- `workspace_manifest.yaml`
- repository-local `config.yaml`
- `resource_manifest.yaml`
- `environment_plan.yaml`
- `baseline_metrics.yaml`

Handoff:

- After `repo-baseline-run` succeeds or records a meaningful local baseline, report readiness for the next optimization stage.
- If any stage fails, invoke `agent-fix-error-recovery` according to the risk gates.

## Workflow

1. Classify the request.
   - If the request is an open-ended research need, continue with the full workflow.
   - If the request names one exact paper and asks for its code, route to `paper-repo-discovery`.
   - If the request names an existing local repository, route directly to `repo-onboard`.
   - Ask only when the route is genuinely ambiguous.

2. Establish a run directory.
   - Prefer a user-provided artifact path.
   - Otherwise create or reuse a clear run directory under the active laboratory workspace, using a short slug from the research need.
   - Record artifacts there unless a delegated skill has a repository-local artifact requirement.

3. Run research scoping.
   - Invoke `research-scope-planning`.
   - Continue only when `research_scope.yaml` exists and identifies task type, benchmark space, constraints, success criteria, and open questions.
   - If key search-space choices are unresolved, ask the user before repository selection.

4. Run repository selection.
   - Invoke `experiment-repo-selection` with the research scope.
   - Continue only when `experiment_base_plan.yaml` exists.
   - Ask the user before proceeding when selection status is `needs_user_confirmation`, candidates are similarly strong, the selected repo is unofficial or medium/low confidence, or the plan requires a composed workspace.

5. Assemble workspace.
   - Invoke `experiment-workspace-assembly` after selection is ready or approved.
   - Continue only when `workspace_manifest.yaml` records a ready primary runnable repository path.
   - If only partial assembly is possible, proceed to `repo-onboard` only when the primary repository is ready and missing references are non-blocking.

6. Onboard primary repository.
   - Invoke `repo-onboard` on the primary runnable repository.
   - Continue only when repository-local `config.yaml` exists.
   - Treat documented baseline/reference discovery as owned by `repo-onboard`.

7. Prepare resources.
   - Invoke `repo-resource-prepare`.
   - Before any resource download, ensure the user chooses whether to reuse the current environment or create a repository-specific environment.
   - Continue only when `resource_manifest.yaml` and `resource_acquisition_report.md` exist or the skill explicitly records that no external resources are required.

8. Set up environment.
   - Invoke `repo-environment-setup`.
   - Install and validate dependencies only inside the environment selected or created by `repo-resource-prepare`.
   - Continue only when `environment_plan.yaml` and `environment_setup_report.md` indicate the environment is ready enough for baseline execution.

9. Run baseline.
   - Invoke `repo-baseline-run`.
   - Run baseline or eval only inside the selected environment.
   - Compare metrics against references discovered by `repo-onboard` when available.
   - Finish with `baseline_metrics.yaml` and `baseline_run_report.md`.

10. Recover from errors.
   - Invoke `agent-fix-error-recovery` automatically after resource, environment, or baseline failures.
   - Allow common low-risk checks and fixes.
   - Ask before large downloads, dependency major-version changes, experiment-protocol changes, source logic edits, deleting files, or any destructive action.
   - After a successful fix, return to the failed stage and continue.

## Readiness Checks

Before moving to the next stage, verify the relevant artifact exists and has a status that permits handoff:

```text
research_scope.yaml          -> experiment-repo-selection
experiment_base_plan.yaml    -> experiment-workspace-assembly
workspace_manifest.yaml      -> repo-onboard
config.yaml                  -> repo-resource-prepare
resource_manifest.yaml       -> repo-environment-setup
environment_plan.yaml        -> repo-baseline-run
baseline_metrics.yaml        -> final readiness summary
```

Do not treat conversational confidence as completion when the expected artifact is missing.

## User Approval Gates

Ask the user before:

- choosing among ambiguous repository candidates
- cloning unofficial or medium/low-confidence repositories
- assembling a composed workspace
- performing large downloads
- creating a new virtual environment when the user has not chosen one
- changing dependency major versions or CUDA/framework stacks
- modifying experiment logic, benchmark protocol, metrics, or dataset splits
- deleting or overwriting files

Do not ask the user just to proceed from one ordinary completed stage to the next.

## Boundaries

Do:

- route natural-language research needs through the correct skill sequence
- keep stage-specific work inside the delegated skill
- use artifacts as handoff contracts
- minimize user-facing prompt requirements
- preserve concise terminal output and detailed report files

Do not:

- duplicate repository search, onboarding, resource, environment, or baseline instructions that belong to delegated skills
- implement the workflow as a Python or TypeScript pipeline
- skip approval gates because this is an orchestrator
- install dependencies, download resources, or run baselines outside the delegated skill that owns that stage
