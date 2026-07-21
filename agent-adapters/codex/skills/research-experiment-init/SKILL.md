---
name: research-experiment-init
description: Common natural-language entrypoint for preparing a research repository for later optimization experiments. Use when Codex receives an open-ended research requirement, a specific paper, or an existing repository and must route the request through the correct Agent + Skill stages. For open-ended research requirements, run experiment-repo-search, repo-experiment-fix, repo-onboard, repo-resource-prepare, repo-environment-setup, and repo-baseline-run, and require the final baseline to be at least one smallest controlled experiment that can answer the research question. Comparative questions need the minimum necessary control/treatment or reference branches, but not every open-ended requirement is a comparison. For a specific paper with an already identified repository or an existing local repository, skip search and source adaptation and enter the final four stages directly. A passing minimum baseline is the final ready-for-optimization state; do not add a separate formal-experiment preparation stage.
---

# Research Experiment Init

Use this skill as the common coordinator for all research-repository initialization requests.

Execute delegated skills interactively. Do not implement a separate Python or TypeScript pipeline.

## Project Completion Semantics

The goal is not complete paper reproduction. The goal is a **minimum reproducible repository for subsequent optimization**. In this workflow, minimum means the smallest scope that still reproduces the core experiment and a scientifically meaningful result; it does not mean independently minimizing resources, runtime, epochs, data, or evaluation effort. Establish the core reproduction first, then remove only peripheral scope that is not needed to support it.

A workflow is complete when:

- one coherent repository contains the original method;
- one representative dataset, bundled input, released result, or official pretrained checkpoint path is prepared;
- for a specific paper or supplied repository, the selected baseline/evaluation command reproduces a paper-aligned core experiment of the original method and produces a meaningful result;
- for an open-ended research requirement, the selected baseline runs at least one smallest controlled experiment that can answer the user's research question;
- when the question is comparative, that controlled experiment includes the minimum necessary on/off, method/control, component/no-component, or primary/reference-model branches;
- the produced result or comparison can be retained as the comparator contract for later optimization;
- `repo-baseline-run` records `status: passed` and `ready_for_optimization: true`.

Do not require:

- every dataset or benchmark used by the paper;
- every horizon, seed, comparison, table, figure, or ablation;
- full retraining when an official pretrained model or released result provides a valid baseline;
- an additional readiness stage after baseline.

Within this project, a passed minimum baseline means the repository can formally enter optimization experiments.

## Baseline Semantics

Distinguish the task type before delegating:

- **Specific paper or supplied repository**: baseline means a minimum representative reproduction of the original paper/method's core experiment. Reuse official artifacts when they embody the contribution; otherwise execute the claim-bearing method. Dataset-level claims require a representative benchmark dataset or justified subset, the paper evaluator, and the primary aggregate metric.
- **Open-ended research requirement**: baseline means a minimum controlled experiment that answers the research question before optimization. It may be a single-method experiment when that is enough, or multiple branches when the claim is comparative; use only the smallest set needed for the question.

For comparative open-ended requirements, require every branch needed to answer the question under a fair protocol. For non-comparative requirements, one controlled experiment can be sufficient.

For specific papers, classify the core contribution before selecting a route. If it is a procedure that creates or changes a scientific artifact, execute the claim-bearing stages at least once and evaluate the newly produced artifact. Evaluating an author-provided artifact alone is `evaluation_only`; a runnable check without core-claim evidence is `demo_only`. Neither can establish readiness for optimizing the procedure.

Do not choose a route by minimizing resource use first. First identify what evidence is required to reproduce the core experiment; then choose the least costly route that satisfies that evidence without weakening it.

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

Default resource policy when the user has not specified stricter limits:

- A single reproduction task may acquire official or trusted resources and install dependencies up to about 6 GB of new local downloads.
- Downloads or installs within this budget are not "large" by default when they are required for the paper-aligned minimum reproduction and stay inside the selected run/environment roots.
- When the user explicitly chooses or creates a repository-specific environment for the run, that approval also authorizes installing the selected minimum-reproduction dependencies into that environment. Do not ask again for each ordinary `pip` or `conda` install.
- Do not infer environment approval from the run directory name, numbering convention, previous experiments, or an agent-proposed environment name. Creation or reuse must be explicitly chosen by the user in the current request.
- Ask before exceeding this budget, using credentialed or license-gated sources, using untrusted mirrors, changing global package-manager configuration, or installing outside the selected repository-specific environment.
- Do not replace a paper-aligned official path with a weaker fallback only because the required dependency or resource download is several GB but still within this default budget.

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
   - Preserve user-stated test intent, such as evaluating repository integration, source modification, benchmark construction, or error recovery. Pass it to downstream skills as part of the requirement rather than treating it as incidental wording.
   - Ask only when the route is genuinely ambiguous.

2. Establish the run directory and `artifact_root`.
   - Reuse existing artifacts when they belong to the same repository and requirement.
   - Pass absolute repository, run, and artifact paths to every skill.
   - When reusing a local repository or local resource for a new experiment, default to creating an isolated copy under the run/workspace root before modifications, staging, or binding. Tell the user the source path, copy path, and that the original was left untouched.

3. For an open-ended requirement, search repositories.
   - Invoke `experiment-repo-search`.
   - Allow it to consult `benchmark-selection` internally without adding another user-facing stage.
   - Require it to define the minimum controlled experiment contract, with comparison branches only when the user asks a comparative question.
   - When the user wants to test repository integration, require explicit comparison of single-repo, primary-with-support, and composed-workspace options before accepting a low-risk fallback.
   - Continue only when `experiment_repo_plan.yaml` and `workspace_manifest.yaml` record `search_status: ready`.

4. For an open-ended requirement, fix or integrate the repository base.
   - Invoke `repo-experiment-fix`.
   - Accept `no_change_required`, `modified`, or `integrated`.
   - Continue only when `repo_experiment_fix.yaml` records `status: ready_for_onboard` and one `final_repo_path`.

5. Onboard the final repository.
   - Invoke `repo-onboard`.
   - For paper/repository routes, require a command that exercises the original method on a paper-aligned core experiment. For dataset-level claims, require a representative benchmark dataset or justified subset, the paper evaluator, and the primary aggregate metric; do not substitute one input or raw prediction.
   - Record the core contribution type and whether method execution is required. Do not mark onboarding ready when a method-execution paper only evaluates an author-provided artifact.
   - For open-ended requirement routes, require the configured baseline to preserve the minimum controlled experiment, including every branch only when the requirement is comparative.
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
   - For paper/repository routes, require the configured claim-bearing method and evidence unit to be verified.
   - For open-ended requirement routes, require the smallest meaningful controlled experiment that answers the research question.
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
- downloads or dependency installs expected to exceed the default 6 GB per-task budget, or any credentialed/license-gated download;
- creating, replacing, or reusing environments unless the current user request explicitly chose that environment strategy;
- installing outside the user-selected repository-specific environment, changing global package-manager configuration, or changing major framework/CUDA/dependency versions beyond what the selected minimum reproduction requires;
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
