# Agent Instructions

This project contains local agent adapters for literature workflows and interactive research-repository initialization.

Agent-specific packages live under `agent-adapters/<agent>/`.

- `agent-adapters/codex/skills`: Codex skills using `SKILL.md` and `agents/openai.yaml`.
- `agent-adapters/claude-code`: reserved for Claude Code packaging.
- `agent-adapters/openclaw`: reserved for OpenClaw packaging.
- `agent-adapters/harness`: reserved for Harness packaging.

Install the Codex skill directories as a set so routing and artifact contracts stay consistent.

## Terminal Output

Show only:

- stage started or completed;
- major repository or minimum-reproduction decision;
- user approval needed;
- artifact path;
- blocker and AgentFix status;
- final baseline result and `ready_for_optimization` state.

Do not repeat full commands, diffs, stdout/stderr, or long logs unless requested. Put details in stage artifacts.

For the final repository-initialization summary, report:

- final repository name and path;
- why it was selected or how it was integrated;
- the representative dataset/input and checkpoint/result route;
- resources and environment;
- baseline metric or meaningful output and reference comparison;
- `ready_for_optimization`;
- key artifact paths.

## Project Definition

The repository workflow prepares a **minimum reproducible optimization base**.

Here, **minimum** means the smallest scope that still reproduces the core experiment and its scientifically meaningful result. It does not mean minimizing compute, runtime, downloads, epochs, data, or evaluation effort independently. Establish core-experiment validity first; only then remove peripheral datasets, seeds, sweeps, ablations, or comparisons that are unnecessary for that validity.

Completion does not mean reproducing every experiment in the original paper. Completion means:

- one coherent repository contains the original method;
- one representative dataset, bundled input, official checkpoint, or released result is sufficient;
- the configured baseline/evaluation produces a meaningful original-method result;
- the result is preserved as the comparator for later optimization;
- `repo-baseline-run` records `status: passed` and `ready_for_optimization: true`.

Do not require all datasets, horizons, seeds, paper tables, figures, comparisons, or ablations. Do not retrain when an official pretrained model or released result provides a valid baseline.

Within this project, a passed minimum-reproduction baseline means the repository is ready to begin formal optimization experiments. Do not add a separate post-baseline formal-readiness stage.

## Research Repository Skills

- `research-experiment-init`: common natural-language coordinator for open-ended research needs, specific papers, and existing repositories.
- `experiment-repo-search`: structure an open-ended requirement, consult the benchmark auxiliary, find and compare repositories, clone or reuse the selected source base, and write search/workspace artifacts.
- `benchmark-selection`: auxiliary decision index used inside `experiment-repo-search`; choose one representative dataset/input, checkpoint/result route, metric/output, and minimum protocol without becoming an additional top-level stage.
- `repo-experiment-fix`: before onboarding, make only the source changes, adapters, benchmark wiring, or cross-repository integrations required by the research need; preserve the original baseline; record `no_change_required` when the selected repository already fits; output one final repository path.
- `paper-repo-discovery`: when a specific paper is given without its repository, find and clone the official or most credible repository and hand it to `repo-onboard`.
- `repo-onboard`: inspect the final repository, select one meaningful original-method reproduction path, prefer pretrained/released-result evaluation over unnecessary retraining, discover reference evidence, and write the Agent-owned `config.yaml`.
- `repo-resource-prepare`: ask for the environment strategy, then stage only resources required by the selected minimum reproduction.
- `repo-environment-setup`: create the smallest environment that can run the selected minimum reproduction, using only the environment approved during resource preparation.
- `repo-baseline-run`: execute the selected meaningful original-method result as the final initialization gate; a passed result sets `ready_for_optimization: true`.
- `agent-fix-error-recovery`: diagnose unexpected resource, environment, command, and baseline failures; planned source adaptation or integration belongs to `repo-experiment-fix`.
- `repo-env-troubleshooting`: advisory reference for environment, resolver, mirror, CUDA/framework, and NumPy ABI failures.
- `agent-fix-knowledge-base`: advisory reusable error lessons; do not use prior lessons to bypass approval gates.

## Roles

- `AgentCoordinator`: `research-experiment-init`
- `AgentRepoSearch`: `experiment-repo-search`
- `BenchmarkIndex`: `benchmark-selection` as an auxiliary advisor
- `AgentRepoFix`: `repo-experiment-fix`
- `AgentResource`: `paper-repo-discovery`
- `AgentOnboard`: `repo-onboard`
- `AgentInit`: `repo-resource-prepare`, `repo-environment-setup`, `repo-baseline-run`
- `AgentFix`: `agent-fix-error-recovery`

Do not introduce a separate AgentBaseline or post-baseline AgentExperimentPrepare role.

## Required Routes

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

### Specific paper and repository already identified

```text
research-experiment-init
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

### Specific paper without a repository

```text
research-experiment-init
  -> paper-repo-discovery
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

### Existing local repository

```text
research-experiment-init
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
```

If the user explicitly asks to adapt an already specified repository to a new research requirement, route it through `repo-experiment-fix` before onboarding.

## Stage Boundaries

Keep request classification, stage sequencing, artifact checks, and final readiness semantics in `research-experiment-init`.

Keep requirement structuring, minimum benchmark/reproduction definition, candidate search, repository comparison, Git clone/reuse, and workspace identity in `experiment-repo-search`.

Keep representative dataset/input selection, pretrained or released-result route selection, minimum protocol, leakage controls, and benchmark evidence in the auxiliary `benchmark-selection` skill. It does not alter the required main route.

Keep intended source modification, adapter creation, data/evaluator wiring, cross-repository integration, original-baseline preservation, and final runnable-root selection in `repo-experiment-fix`.

Keep repository inspection, minimum original-method command discovery, and documented reference discovery in `repo-onboard`.

Keep environment choice, runtime resource discovery, resource acquisition, staging, and path binding in `repo-resource-prepare`.

Keep dependency inference, installation, framework compatibility, and cheap pre-baseline validation in `repo-environment-setup`.

Keep meaningful original-method execution, metric/output validation, reference comparison, and final `ready_for_optimization` decision in `repo-baseline-run`.

Keep unexpected failure diagnosis and low-risk repair in `agent-fix-error-recovery`. If a failure exposes a missing planned feature or integration, return to `repo-experiment-fix`.

## Artifact Layout

Keep Agent-generated auxiliary files under `<run_dir>/experiment_artifacts/`:

```text
experiment_artifacts/
  plans/
  manifests/
  reports/
  evidence/
  logs/
```

Keep source, runtime configs, dependency definitions, resources, and experiment results in their normal repository/run locations.

Core artifact chain for an open-ended requirement:

```text
plans/research_requirement.yaml
  -> plans/benchmark_plan.yaml
  -> plans/experiment_repo_plan.yaml
  -> manifests/workspace_manifest.yaml
  -> manifests/repo_experiment_fix.yaml
  -> manifests/config.yaml
  -> manifests/resource_manifest.yaml
  -> plans/environment_plan.yaml
  -> manifests/baseline_metrics.yaml
```

The final manifest must record:

```yaml
status: "passed"
ready_for_optimization: true
```

## Approval Rules

Ask before:

- ambiguous or unofficial repository selection;
- unclear license or provenance;
- large or credentialed downloads;
- creating, replacing, or changing environments;
- major dependency, framework, CUDA, or system changes;
- changing the scientific target, labels, split semantics, primary metric, or model objective;
- destructive operations or overwriting user files.

Do not ask:

- merely to continue between ordinary completed stages;
- to perform read-only inspection;
- to apply small reversible changes already required by the approved research need;
- to reuse an official pretrained checkpoint instead of unnecessary retraining when the route is clearly valid and download approval is not otherwise required.

## Literature Skills

The repository also contains literature and paper-wiki skills:

- `problem-frame`
- `literature-review`
- `literature-search`
- `paper-digest`
- `paper-ingest`
- `paper-ingest-batch`
- `paper-wiki`
- `paper-wiki-search`
- `paper-wiki-query`
- `paper-wiki-lint`

Use `paper-wiki` for wiki routing. Use `paper-ingest-batch` for multi-paper ingestion. These literature skills do not replace the research repository workflow above.

## General Boundaries

- Execute skills interactively; do not implement clone, download, installation, baseline, or repair orchestration as a separate Python/TypeScript pipeline.
- Preserve user changes and avoid destructive Git operations.
- Use artifacts, not conversational confidence, as stage completion evidence.
- Treat one representative original-method result as sufficient for this project's repository initialization.
- Do not reinterpret a passed meaningful baseline as an intermediate-only state; it is the project's final ready-for-optimization gate.
