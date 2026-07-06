---
name: repo-experiment-fix
description: Inspect the repositories selected by experiment-repo-search and make the minimum source-level changes, adapters, benchmark wiring, or cross-repository integrations needed to produce one coherent repository for the requested optimization experiment before onboarding. Use when the selected repository base may already fit exactly, may need a bounded modification, or may require multiple repositories to be connected. Preserve the original-method baseline path, record no_change_required when appropriate, and output one final repository path for repo-onboard. This skill does not install dependencies, acquire runtime resources, or run the final baseline.
---

# Repo Experiment Fix

Use this skill between repository search and onboarding. Turn the selected source base into one coherent repository that satisfies the research requirement and retains a minimum original-method reproduction path.

This is intended experiment adaptation, not runtime error recovery. Use `agent-fix-error-recovery` only for unexpected command or tooling failures.

## Project Definition

The final repository is complete for this project when:

- it contains the original method needed as the optimization baseline;
- it contains the adapters or integrations required by the research need;
- one representative dataset or official pretrained evaluation route can later produce the original-method result;
- later optimization can be implemented and compared on the same path;
- unnecessary full-paper datasets, retraining, tables, and ablations are not required.

If the selected repository already satisfies these conditions, do not modify it. Record `no_change_required`.

## Artifact Location

Use the inherited `artifact_root`.

- plans: `repo_experiment_fix_plan.yaml`
- manifests: `repo_experiment_fix.yaml`, updated `workspace_manifest.yaml`
- reports: `repo_experiment_fix_report.md`
- evidence and logs: static checks, interface checks, and command output

Keep source, adapters, runtime configs, and repository-native files in the final repository.

## Agent Contract

Role: `AgentRepoFix`

Inputs:

- `research_requirement.yaml`
- `experiment_repo_plan.yaml`
- `workspace_manifest.yaml`
- all selected local repository paths
- optional protected paths and user decisions

Required outputs:

- `<artifact_root>/plans/repo_experiment_fix_plan.yaml`
- `<artifact_root>/manifests/repo_experiment_fix.yaml`
- `<artifact_root>/reports/repo_experiment_fix_report.md`
- an updated `<artifact_root>/manifests/workspace_manifest.yaml`
- exactly one `final_repo_path` for `repo-onboard`

Handoff:

- Continue only when status is `ready_for_onboard`.
- Hand `final_repo_path`, minimum reproduction intent, source changes, component roles, and unresolved runtime assumptions to `repo-onboard`.

## Workflow

1. Inspect the selected source base.
   - Read the requirement, minimum reproduction contract, repository plan, and workspace manifest.
   - Inspect actual code, configs, entrypoints, loaders, evaluators, extension points, and component interfaces.
   - Preserve existing user changes and record Git identity when available.

2. Determine whether changes are required.
   - Use `no_change_required` when one repository already exposes the original-method result and the extension path needed by the requirement.
   - Use `modified` for bounded changes inside one repository.
   - Use `integrated` when multiple repositories or components must be connected.
   - Do not modify code merely to normalize style, modernize dependencies, or add optional infrastructure.

3. Write the fix plan before material edits.
   - Map each requirement to repository role, file, symbol, expected behavior, and validation evidence.
   - Record the original baseline path that must remain available.
   - Record proposed files, adapters, interface contracts, provenance, protected invariants, and approval needs.

4. Resolve approval gates.
   - Treat the user's research requirement as approval for small, reversible changes directly required to satisfy it.
   - Ask before changing the scientific target, labels, split meaning, primary metric, model objective, major architecture, license boundary, or resource class.
   - Ask before destructive changes, replacing user files, or copying code with unclear provenance.

5. Apply the minimum required changes.
   - Prefer configuration, adapters, wrappers, and explicit interfaces over invasive rewrites.
   - Preserve an explicit original-method baseline mode.
   - Keep the selected representative benchmark path and evaluation meaning unchanged.
   - For data adaptation, preserve provenance and prevent future-information or target leakage.
   - Record every source or protocol change and why it is necessary.

6. Integrate multiple repositories when required.
   - Select one final primary root.
   - Define each component's role and explicit input/output contract.
   - Connect the actual data and artifact flow; colocating repositories is not integration.
   - Provide one root-level path that later stages can onboard.
   - Avoid requiring the user to manually copy intermediate files between repositories.
   - Preserve source URL, commit, and license information for incorporated components.

7. Perform bounded source-level verification.
   - Run static inspection, syntax/compile checks, import-free checks, config validation, or focused tests that do not require unprepared dependencies or runtime resources.
   - Do not install packages or download data in this stage.
   - Defer environment-dependent validation to the later four stages.
   - If an unexpected tool or command failure occurs, invoke `agent-fix-error-recovery`; keep intended implementation work in this skill.

8. Write the final handoff.
   - Set one `final_repo_path`.
   - Record status, change mode, changed files, component roles, original baseline path, expected minimum reproduction command family, resource hints, dependency hints, and remaining runtime assumptions.
   - Update `workspace_manifest.yaml` so later skills use the final repository rather than an unintegrated source repository.

## Manifest Shape

```yaml
status: "ready_for_onboard" # ready_for_onboard | needs_user_decision | blocked
change_mode: "no_change_required" # no_change_required | modified | integrated
research_requirement_path: ""
experiment_repo_plan_path: ""
final_repo_path: ""
original_method:
  preserved: true
  baseline_entrypoint: ""
  representative_dataset_or_input: ""
  primary_metric_or_output: ""
requirement_mapping:
  - requirement: ""
    repository_role: ""
    files_and_symbols: []
    implemented_behavior: ""
component_roles: []
changed_files: []
added_files: []
protocol_invariants: []
resource_hints: []
dependency_hints: []
verification:
  static_checks: []
  status: "passed"
runtime_validation_deferred_to:
  - "repo-onboard"
  - "repo-resource-prepare"
  - "repo-environment-setup"
  - "repo-baseline-run"
next_skill: "repo-onboard"
```

## Decision Rules

- No source modification is a valid and preferred result when the repository already fits.
- Make only changes necessary to satisfy the requirement and expose a usable optimization base.
- Preserve the original method as the baseline comparator.
- Do not require the optimized method itself to outperform the baseline in this stage.
- Do not call a directory containing multiple untouched repositories an integrated experiment repository.
- Runtime readiness is established later by a passing baseline, not by static confidence here.

## Boundaries

Do:

- inspect and modify selected repositories
- create bounded adapters and evaluators
- integrate required components into one final repository
- preserve the original-method baseline
- output one final repository path

Do not:

- install dependencies or create environments
- acquire datasets, checkpoints, or pretrained model caches
- run the final baseline or long training
- reproduce every paper experiment
- make unrelated refactors or destructive Git changes
