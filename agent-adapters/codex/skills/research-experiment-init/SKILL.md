---
name: research-experiment-init
description: Orchestrate the full Agent + Skill workflow from a natural-language research need to a codebase that is ready for formal requirement-validation experiments. Use when Codex is asked to find suitable open-source experiment repositories, choose or specify a benchmark, prepare the repository, resources, environment, and baseline, then implement missing methods or integrations, configure and dry-run experiment branches, and generate formal-run scripts without launching the full experiment. This skill routes to research-repo-setup, which consults benchmark-selection, then to repo-onboard, repo-resource-prepare, repo-environment-setup, repo-baseline-run, repo-experiment-prepare, and agent-fix-error-recovery as needed; it does not replace those skills or implement a separate Python pipeline.
---

# Research Experiment Init

Use this skill as the natural-language entrypoint for a full research-demand-to-experiment-ready workflow.

The agent acts as the coordinator. Do not implement a separate Python or TypeScript pipeline for this logic. Invoke the existing Codex skills interactively and use their artifacts to decide whether each stage is complete.

## Workflow Artifact Layout

At the start of the workflow, set `artifact_root` to `<run_dir>/experiment_artifacts/` and pass it to every delegated skill. Never scatter Agent-generated auxiliary files across the repository root.

Use this layout:

```text
experiment_artifacts/
  plans/       # research scope, benchmark, environment, adaptation, and experiment plans/matrices
  manifests/   # workspace/config/resource/baseline/readiness machine state
  reports/     # human-readable stage and final reports
  evidence/    # checks, metrics, fixtures, dry-run and regression evidence
  logs/        # command and recovery logs
```

Bare artifact names in this skill refer to the appropriate path under `artifact_root`. Keep source code, the primary `README.md`, formal launch and summary scripts, runtime configs under `configs/`, standard dependency files such as `environment.yml` and requirements files, and result directories in the normal codebase structure.

For an existing workspace, reuse or migrate root-level auxiliary artifacts into this layout when safe, update every reference, and avoid duplicate sources of truth. Do not move a file merely because it is YAML, JSON, Markdown, or a log; classify it by purpose. Runtime files stay with the code, while Agent plans, manifests, reports, evidence, and logs go under `artifact_root`.

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
- final experiment readiness summary

Put detailed commands, evidence, candidate tables, logs, and diffs in the stage report files produced by the delegated skills.

## Agent Contract

Role: `AgentCoordinator`

Inputs:

- natural-language research need
- optional constraints such as compute budget, dataset policy, preferred framework, runtime, or avoidance of large downloads
- optional task run directory or workspace preference

Primary outputs are produced by delegated skills:

- `research_scope.yaml`
- `benchmark_plan.yaml`
- `experiment_base_plan.yaml`
- `workspace_manifest.yaml`
- `<artifact_root>/manifests/config.yaml`
- `resource_manifest.yaml`
- `environment_plan.yaml`
- `baseline_metrics.yaml`
- `method_adaptation_plan.yaml`
- `experiment_plan.yaml`
- `experiment_matrix.yaml`
- `experiment_readiness.yaml`

Handoff:

- After `repo-baseline-run` succeeds, invoke `repo-experiment-prepare` in `requirement_validation` mode.
- Report formal experiment readiness only when `experiment_readiness.yaml` records `ready_for_formal_run`.
- If any stage fails, invoke `agent-fix-error-recovery` according to the risk gates.

## Workflow

1. Classify the request.
   - Before starting a new workflow, check whether the current repository already has `<artifact_root>/manifests/experiment_readiness.yaml` with `ready_for_formal_run` for the same recorded requirement.
   - If it does, route directly to the `repo-experiment-prepare` re-entry audit. Do not repeat repository selection, onboarding, resource preparation, environment setup, baseline execution, or experiment preparation unless the re-entry audit identifies a concrete stale or invalid gate.
   - If the request is an open-ended research need, continue with the full workflow.
   - If the request names one exact paper and asks for its code, route to `paper-repo-discovery`.
   - For the exact-paper route, require `repo-experiment-prepare` to ask for experiment scope after read-only paper/repository inspection and before modification; recommend paper reproduction by default.
   - If the request names an existing local repository, route directly to `repo-onboard`.
   - Ask only when the route is genuinely ambiguous.

2. Establish a run directory.
   - Prefer a user-provided artifact path.
   - Otherwise create or reuse a clear run directory under the active laboratory workspace, using a short slug from the research need.
   - Create or reuse `<run_dir>/experiment_artifacts/` with the standard subdirectories and pass that absolute `artifact_root` to every delegated skill.
   - Require delegated skills to resolve their generated plans, manifests, reports, evidence, and logs under `artifact_root`; a repository-local requirement does not mean the repository root.

3. Scope, select, and materialize the research repository.
   - Invoke `research-repo-setup`.
   - Require `research_scope.yaml`, externally produced `benchmark_plan.yaml`, `experiment_base_plan.yaml`, and `workspace_manifest.yaml` as phase checkpoints.
   - Ensure `research-repo-setup` invokes `benchmark-selection` before final repository comparison and treats its protocol as authoritative.
   - Ask the user when key search-space choices remain unresolved, selection status is `needs_user_confirmation`, candidates are similarly strong, the selected repo is unofficial or medium/low confidence, or the plan requires a composed workspace.
   - Continue only when `workspace_manifest.yaml` records a ready primary runnable repository path with verified remote, branch, and commit.
   - If only partial assembly is possible, proceed to `repo-onboard` only when the primary repository is ready and missing references are non-blocking.

4. Onboard primary repository.
   - Invoke `repo-onboard` on the primary runnable repository.
   - Continue only when `<artifact_root>/manifests/config.yaml` exists.
   - Treat documented baseline/reference discovery as owned by `repo-onboard`.

5. Prepare resources.
   - Invoke `repo-resource-prepare`.
   - Before any resource download, ensure the user chooses whether to reuse the current environment or create a repository-specific environment.
   - Continue only when `resource_manifest.yaml` and `resource_acquisition_report.md` exist or the skill explicitly records that no external resources are required.

6. Set up environment.
   - Invoke `repo-environment-setup`.
   - Install and validate dependencies only inside the environment selected or created by `repo-resource-prepare`.
   - Continue only when `environment_plan.yaml` and `environment_setup_report.md` indicate the environment is ready enough for baseline execution.

7. Run baseline.
   - Invoke `repo-baseline-run`.
   - Run baseline or eval only inside the selected environment.
   - Compare metrics against references discovered by `repo-onboard` when available.
   - Finish with `baseline_metrics.yaml` and `baseline_run_report.md`.

8. Prepare the codebase for requirement-validation experiments.
   - Invoke `repo-experiment-prepare` in `requirement_validation` mode.
   - Require requirement-to-code traceability against `research_scope.yaml` and `benchmark_plan.yaml`.
   - Allow the skill to implement protocol-preserving methods, adapters, evaluators, configuration, and approved cross-repository interfaces while retaining the original baseline mode.
   - For composed workspaces, require one documented architecture, root formal entrypoint, explicit component interfaces, automatic end-to-end artifact flow, unified configuration/environment/benchmark/evaluation/output controls, all source needed by the current server run, and a bounded run through the real complete workflow. Git initialization, commits, tracked status, author identity, and clean-clone reconstruction are not readiness requirements.
   - Require `method_adaptation_plan.yaml`, `experiment_plan.yaml`, `experiment_matrix.yaml`, and `experiment_readiness.yaml`.
   - Run only bounded validation and per-branch dry runs; do not launch full formal experiments.
   - Require the primary repository README to contain the managed formal-experiment section and exact guarded launch command.
   - Accept `ready_for_formal_run` only after directly verifying the modified code, complete local-workspace integration, post-change baseline regression, every experiment branch, generated launcher, expected outputs, and README instructions; otherwise finish as `needs_user_decision`, `needs_implementation`, or `blocked`.
   - Require a consolidated, human-readable `experiment_readiness_report.md` that preserves the original requirement and maps it to actual code locations, changes, experiment branches, evidence, and formal execution instructions.
   - In the final response, link the consolidated report and tell the user exactly how to start the formal run, where outputs will go, and how to summarize results, while stating that the formal run has not started.
   - Because this is requirement-driven, let the Agent determine the scientifically necessary experiment scope from `research_scope.yaml` and `benchmark_plan.yaml`; do not add a routine user scope-selection prompt.

9. Recover from errors.
   - Invoke `agent-fix-error-recovery` automatically after resource, environment, baseline, experiment-preparation, or dry-run failures.
   - Allow common low-risk checks and fixes.
   - Ask before large downloads, dependency major-version changes, scientific-protocol changes, source logic changes beyond the approved research goal, deleting files, or any destructive action.
   - After a successful fix, return to the failed stage and continue.

## Readiness Checks

Before moving to the next stage, verify the relevant artifact exists and has a status that permits handoff:

```text
plans/research_scope.yaml             -> research-repo-setup selection phase
plans/benchmark_plan.yaml             -> research-repo-setup repository comparison
plans/experiment_base_plan.yaml       -> research-repo-setup assembly phase
manifests/workspace_manifest.yaml     -> repo-onboard
manifests/config.yaml                 -> repo-resource-prepare
manifests/resource_manifest.yaml      -> repo-environment-setup
plans/environment_plan.yaml           -> repo-baseline-run
manifests/baseline_metrics.yaml       -> repo-experiment-prepare
manifests/experiment_readiness.yaml   -> final readiness summary
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
- modifying experiment logic beyond the approved research goal
- changing benchmark protocol, metrics, labels, or dataset splits
- deleting or overwriting files

Do not ask the user just to proceed from one ordinary completed stage to the next.

## Boundaries

Do:

- route natural-language research needs through the correct skill sequence
- keep stage-specific work inside the delegated skill
- use artifacts as handoff contracts
- keep all Agent-generated auxiliary artifacts under the shared `experiment_artifacts/` tree
- minimize user-facing prompt requirements
- preserve concise terminal output and detailed report files

Do not:

- duplicate repository search, onboarding, resource, environment, or baseline instructions that belong to delegated skills
- implement the workflow as a Python or TypeScript pipeline
- skip approval gates because this is an orchestrator
- install dependencies, download resources, run baselines, or prepare experiment code outside the delegated skill that owns that stage
