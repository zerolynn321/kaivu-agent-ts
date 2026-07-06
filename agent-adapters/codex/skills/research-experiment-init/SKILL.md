---
name: research-experiment-init
description: Common natural-language entrypoint for preparing a research repository for later optimization experiments. Use when Codex receives an open-ended research requirement, a specific paper, or an existing repository and must route the request through the correct Agent + Skill stages. For open-ended requirements, run experiment-repo-search, repo-experiment-fix, repo-onboard, repo-resource-prepare, repo-environment-setup, and repo-baseline-run. For a specific paper with an already identified repository or an existing local repository, skip search and source adaptation and enter the final four stages directly. A passing minimum-reproduction baseline is the final ready-for-optimization state; do not add a separate formal-experiment preparation stage.
---

# Research Experiment Init

Use this skill as the common coordinator for all research-repository initialization requests.

Execute delegated skills interactively. Do not implement a separate Python or TypeScript pipeline.

## Project Completion Semantics

The goal is not complete paper reproduction. The goal is a **minimum reproducible repository for subsequent optimization**.

A workflow is complete when:

- one coherent repository contains the original method;
- one representative dataset, bundled input, released result, or official pretrained checkpoint path is prepared;
- the selected baseline/evaluation command produces a meaningful original-method result;
- that result can be retained as the comparator for later optimization;
- `repo-baseline-run` records `status: passed` and `ready_for_optimization: true`.

Do not require:

- every dataset or benchmark used by the paper;
- every horizon, seed, comparison, table, figure, or ablation;
- full retraining when an official pretrained model or released result provides a valid baseline;
- an additional readiness stage after baseline.

Within this project, a passed minimum-reproduction baseline means the repository can formally enter optimization experiments.

## Artifact Layout

Set `artifact_root` to `<run_dir>/experiment_artifacts/` unless the user provides another location.

```text
experiment_artifacts/
  plans/
  manifests/
  reports/
  evidence/
  logs/
```

Keep source code, runtime configs, dependency files, resources, and result directories in their normal project locations.

## Terminal Output

Report only:

- stage start or completion;
- major repository or minimum-reproduction decision;
- required user approval;
- artifact path;
- blocker and AgentFix status;
- final baseline result and `ready_for_optimization` state.

Put detailed commands, candidate evidence, logs, and diffs in stage reports.

## Agent Contract

Role: `AgentCoordinator`

Inputs:

- open-ended research requirement, specific paper, or repository path/URL
- optional compute, framework, data, license, download, or environment constraints
- optional run directory

Outputs are owned by delegated skills. The final required outputs are:

- `<artifact_root>/manifests/config.yaml`
- `<artifact_root>/manifests/resource_manifest.yaml`
- `<artifact_root>/plans/environment_plan.yaml`
- `<artifact_root>/manifests/baseline_metrics.yaml`
- `<artifact_root>/reports/baseline_run_report.md`

Open-ended workflows additionally require:

- `<artifact_root>/plans/research_requirement.yaml`
- `<artifact_root>/plans/benchmark_plan.yaml`, produced inside `experiment-repo-search` through the auxiliary `benchmark-selection` skill
- `<artifact_root>/plans/experiment_repo_plan.yaml`
- `<artifact_root>/manifests/workspace_manifest.yaml`
- `<artifact_root>/manifests/repo_experiment_fix.yaml`

## Routing

### Open-ended research requirement

```text
research-experiment-init
  -> experiment-repo-search
  -> repo-experiment-fix
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

Use this route when the user describes a research goal and expects the Agent to determine repositories, benchmark evidence, or required integration.

### Specific paper and repository already identified

```text
research-experiment-init
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

Use this route when the user supplies the exact paper and its repository, or supplies an existing local repository and asks to initialize it. Do not search again and do not modify the method before onboarding unless the user explicitly asks.

### Specific paper without an identified repository

```text
research-experiment-init
  -> paper-repo-discovery
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

Use `paper-repo-discovery` only to resolve and clone the paper repository, then enter the same four-stage tail.

## Workflow

1. Classify the request.
   - Preserve the user's wording.
   - Choose one route above.
   - Ask only when the route is genuinely ambiguous.

2. Establish the run directory and `artifact_root`.
   - Reuse existing artifacts when they belong to the same repository and requirement.
   - Pass absolute repository, run, and artifact paths to every skill.

3. For an open-ended requirement, search repositories.
   - Invoke `experiment-repo-search`.
   - Allow it to consult `benchmark-selection` internally without adding another user-facing stage.
   - Continue only when `experiment_repo_plan.yaml` and `workspace_manifest.yaml` record `search_status: ready`.

4. For an open-ended requirement, fix or integrate the repository base.
   - Invoke `repo-experiment-fix`.
   - Accept `no_change_required`, `modified`, or `integrated`.
   - Continue only when `repo_experiment_fix.yaml` records `status: ready_for_onboard` and one `final_repo_path`.

5. Onboard the final repository.
   - Invoke `repo-onboard`.
   - Require a minimum-reproduction command that exercises the original method on one representative input and produces a meaningful metric or output.
   - Continue only when `config.yaml` records `onboard_status: ready`.

6. Prepare only required resources.
   - Invoke `repo-resource-prepare`.
   - Preserve the environment-choice gate.
   - Acquire only resources required by the selected minimum-reproduction command.
   - Prefer official pretrained checkpoints, released predictions/results, bundled datasets, and reusable local resources over unnecessary retraining or broad downloads.

7. Prepare the minimum environment.
   - Invoke `repo-environment-setup`.
   - Install only into the environment chosen during resource preparation.
   - Continue only when environment validation is ready for the selected baseline.

8. Run the minimum-reproduction baseline.
   - Invoke `repo-baseline-run`.
   - Require a meaningful original-method result, not only an import or empty command success.
   - Compare with a documented reference when available; absence of a comparable reference does not block a valid local baseline.
   - Finish when `baseline_metrics.yaml` records `status: passed` and `ready_for_optimization: true`.

9. Recover from failures.
   - Invoke `agent-fix-error-recovery` automatically for unexpected resource, environment, command, or baseline failures.
   - Return intended source adaptation or integration gaps to `repo-experiment-fix`.
   - Ask only before risky, expensive, destructive, or scientifically meaningful changes.

## Readiness Chain

```text
plans/research_requirement.yaml         -> experiment-repo-search
plans/experiment_repo_plan.yaml         -> repo-experiment-fix
manifests/repo_experiment_fix.yaml      -> repo-onboard
manifests/config.yaml                   -> repo-resource-prepare
manifests/resource_manifest.yaml        -> repo-environment-setup
plans/environment_plan.yaml             -> repo-baseline-run
manifests/baseline_metrics.yaml         -> ready_for_optimization
```

For direct paper/repository routes, the chain starts at `config.yaml`.

## Approval Gates

Ask before:

- ambiguous or unofficial repository selection;
- unclear license or provenance;
- large or credentialed downloads;
- creating or replacing environments;
- major framework, CUDA, or dependency changes;
- scientific target, split, label, metric, or model-objective changes;
- destructive operations or overwriting user files.

Do not ask merely to continue between ordinary completed stages.

## Boundaries

Do:

- use this skill as the common natural-language entrypoint
- follow the exact route appropriate to the input
- use artifacts as stage contracts
- optimize for the smallest credible original-method reproduction
- end at a passing baseline that is ready for later optimization

Do not:

- require complete paper reproduction
- add another post-baseline readiness stage
- rerun training when an official checkpoint or released result is sufficient
- duplicate work owned by delegated skills
- implement orchestration as a standalone program
