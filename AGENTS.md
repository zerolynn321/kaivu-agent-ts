# Literature Agent Instructions

This project contains local agent adapters for the literature review and literature wiki system.

Agent-specific packages live under `agent-adapters/<agent>/`. Do not assume every agent uses Codex-style `SKILL.md` directories.

- `agent-adapters/codex/skills`: Codex-compatible skills using `SKILL.md` and `agents/openai.yaml`.
- `agent-adapters/claude-code`: reserved for Claude Code-compatible packaging.
- `agent-adapters/openclaw`: reserved for OpenClaw-compatible packaging.
- `agent-adapters/harness`: reserved for Harness-compatible packaging.

Install one agent package at a time. For Codex, install the skill directories under `agent-adapters/codex/skills` as a set so literature review, digest, ingest, batch, wiki search, wiki query, and lint behavior stay consistent.

## Terminal Output Style

When reporting progress in the Codex terminal, show only key stage progress and final results. Do not paste detailed command transcripts, command strings, full command lists, stdout/stderr blocks, file content snippets, or file content diffs unless the user explicitly asks for them. Summarize what changed at the artifact level, such as file paths created, status fields updated, resources available, environment ready, or blockers found.

For the paper-repo workflow, keep terminal messages in this shape:

- stage started or completed
- key decision or user approval needed
- artifact path created or updated
- final status and next step

Write detailed commands, logs, evidence snippets, and diffs only into the stage report files. If the Codex UI itself displays tool calls such as `Ran ...` or `Edited ...`, do not repeat those details in model-authored progress or final messages.

For the final paper-repo workflow summary, report only:

- cloned repository name and local path
- why that repository was selected
- resources downloaded, copied, or reused and where they were staged
- dependencies installed and the target environment
- baseline result and reference comparison
- method, adapter, evaluator, or cross-repository changes made after baseline
- formal experiment matrix and per-branch dry-run status
- whether the codebase is ready for formal experiments and which readiness mode applies
- the consolidated human-readable `experiment_readiness_report.md` path
- the exact guarded formal-run command, repository README path, output location, and summarizer command

## General Research Skills

- `problem-frame`: clarify broad or ambiguous requests before literature review, paper wiki work, hypothesis generation, experiment planning, or research-oriented implementation.
- `literature-review`: frame research questions, generate and validate literature search queries, search external literature sources, and return ranked candidate papers.
- `literature-search`: run external literature search with `rag_arxiv_retrieve` and return candidate papers.
- `research-experiment-init`: natural-language entrypoint for open-ended research-demand experiment initialization; act as AgentCoordinator to route through combined research repository setup, external benchmark decision support, repository onboarding, resource preparation, environment setup, baseline run, experiment preparation, and error recovery using the delegated skills and their artifacts.
- `research-repo-setup`: for an open-ended research need, combine AgentResearchFrame, AgentSelector, and AgentResource responsibilities in one skill: structure the research question and benchmark requirements; consult `benchmark-selection`; compare repositories against the resulting benchmark contract; select a credible `single-repo`, `primary-repo-with-references`, or `composed-workspace` experiment base; clone or reuse approved repositories; verify remote, branch, commit, roles, and one primary runnable path; and write the scope, selection, and workspace artifact sets before handing off to `repo-onboard`.
- `benchmark-selection`: external benchmark decision index used by `research-repo-setup`; determine whether to adopt an established benchmark, adapt one under explicit scientific invariants, or construct a new benchmark specification; define datasets, provenance, task protocol, splits, leakage controls, metrics, baselines, resources, fairness invariants, and acceptance tests; and write `benchmark_plan.yaml` plus `benchmark_selection_report.md` without selecting repositories or executing experiments.
- `paper-repo-discovery`: given a specific paper title, URL, DOI, arXiv/OpenReview page, PDF, or local paper file, find the official or most credible public code repository, verify evidence, ask for confirmation when ambiguous, clone the selected repository locally, and write a resolution report.
- `repo-onboard`: after a paper repository has been cloned or selected, act as AgentOnboard to reuse an existing root `config.yaml` or scan the repository and create one locally before resource, environment, or baseline stages; this stage owns documented baseline/reference discovery.
- `repo-resource-prepare`: after repository onboarding, act as AgentInit to ask whether to reuse the current environment or create a new repository-specific environment before resource download, then identify required datasets, models, checkpoints, caches, and path assumptions; stage all required resources under the run directory; bind repository paths when needed; and write resource manifest and acquisition reports before dependency installation. Do not proceed from old `config.yaml` environment metadata alone.
- `repo-environment-setup`: after resource preparation, act as AgentInit to verify setup commands target the environment selected or created by `repo-resource-prepare`, then infer, install, and validate runtime dependencies only inside that environment; ask before environment-changing dependency actions; and invoke AgentFix automatically on setup or validation failure.
- `repo-baseline-run`: after resource and environment setup are ready, act as AgentInit to interactively run the configured baseline/eval command inside the prepared environment as the final initialization readiness check, parse metrics, compare against references recorded by `repo-onboard`, write baseline reports, and invoke AgentFix automatically on execution or metric failures.
- `repo-experiment-prepare`: after baseline validation, act as AgentExperimentPrepare in `optimization` mode for a specific paper/repository or `requirement_validation` mode for an open-ended research need; make the actual repository ready for formal experiments by inspecting real source interfaces, implementing missing methods/adapters/evaluators/cross-repository integration while preserving the original baseline, freezing the experiment protocol and matrix, dry-running every branch, generating batch scripts without launching them, documenting the exact formal command in the primary repository README, and producing a consolidated human-readable `experiment_readiness_report.md` that connects requirements, code locations, changes, validation evidence, and formal execution instructions.
- `agent-fix-error-recovery`: automatically use this when resource download, environment setup, validation, baseline, or experiment execution fails; act as AgentFix to diagnose the error, execute common low-risk fixes, ask only before risky actions, verify the result, and write a fix report.
- `repo-env-troubleshooting`: reference this from AgentInit or AgentFix when new virtual environments, dependency installs, mirrors, CUDA/framework compatibility, NumPy ABI, or environment validation produce common failures; it is advisory and does not own installation.
- `agent-fix-knowledge-base`: reference this from AgentFix for repeated or difficult errors and compact reusable lessons; promote new shared cases only when the user explicitly asks.

## Paper Literature Skills

Use `paper-wiki` first for routing and operation-boundary questions.

Use these skills before modifying or operating the paper ingest pipeline:

- `paper-wiki`: route digest, ingest, batch, query, lint, and save-like wiki operations.
- `literature-review`: find external paper candidates before digest or ingest.
- `literature-search`: retrieve external paper candidates with `rag_arxiv_retrieve`.
- `paper-digest`: create or revise structured `PaperDigest` records from scientific papers.
- `paper-ingest`: plan and materialize one structured `PaperDigest` into literature wiki pages.
- `paper-ingest-batch`: orchestrate multi-paper digest, ingest, cross-reference, commit, and batch summary.
- `paper-wiki-search`: retrieve relevant literature wiki pages before query, ingest planning, or cross-reference.
- `paper-wiki-query`: answer questions using retrieved literature wiki pages with citations.
- `paper-wiki-lint`: health-check wiki graph, evidence, stale claims, and missing cross-references.

Use `paper-ingest-batch` as the orchestration pattern when multiple papers are processed together. Batch ingest owns deduplication, failures, cross-reference pass, commit, log/index/hot updates, and batch summary.

## Boundary

Use `research-experiment-init` as the natural-language entrypoint when the user asks to turn a research need into a suitable open-source experiment repository, benchmark choice, local runnable baseline, or full initialization workflow.

Use `research-repo-setup` when the user gives a research need, topic, desired comparison, or benchmark-seeking request instead of one specific paper.

Keep workflow classification, stage sequencing, artifact readiness checks, and cross-stage approval gates in `research-experiment-init`.

Keep broad research-demand scoping, method-family discovery, candidate repository comparison, experiment-base selection, local clone/reuse, workspace layout, Git identity verification, and primary runnable repository handoff in `research-repo-setup`. Preserve `research_scope.yaml`, `experiment_base_plan.yaml`, and `workspace_manifest.yaml` as internal phase checkpoints.

Keep benchmark candidate discovery, existing-benchmark evaluation, adopt/adapt/construct decisions, dataset and protocol definition, split and leakage rules, metrics, baselines, fairness invariants, and benchmark acceptance criteria in `benchmark-selection`. Treat it as an external index consulted by `research-repo-setup`, not as a new top-level pipeline stage.

Keep paper-to-code repository discovery and cloning in `paper-repo-discovery`.

Keep cloned-repository onboarding and local `config.yaml` creation in `repo-onboard`.

Keep documented baseline/reference discovery in `repo-onboard`.

Keep the explicit environment choice before downloads, required runtime resource discovery, download/copy, staging, and repo path binding in `repo-resource-prepare`.

Keep repository-specific virtual environment targeting, runtime dependency planning/installation, CUDA/PyTorch/TensorFlow compatibility, and cheap validation checks in `repo-environment-setup`.

Keep common virtual environment and environment setup troubleshooting guidance in `repo-env-troubleshooting`.

Keep baseline execution, metric parsing, comparison against onboard-recorded references, and baseline reports in `repo-baseline-run`.

Treat `repo-resource-prepare`, `repo-environment-setup`, and `repo-baseline-run` as the three AgentInit skills. Do not introduce a separate AgentBaseline role unless the user explicitly changes this architecture.

Keep post-baseline source inspection, requirement-to-code traceability, planned method and integration changes, post-change baseline regression, formal experiment planning, per-branch dry runs, batch script generation, README formal-run instructions, the consolidated human-readable final report, direct codebase verification, and the `ready_for_formal_run` gate in `repo-experiment-prepare`. Treat it as AgentExperimentPrepare, not as part of AgentInit or AgentFix. The primary deliverables are the working experiment codebase and its readable `experiment_readiness_report.md`; machine-readable artifacts only record evidence and must not replace direct inspection of code, commands, and outputs.

For open-ended research-demand workflows, use this order:

```text
research-experiment-init
  -> research-repo-setup
       <-> benchmark-selection
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
  -> repo-experiment-prepare
```

For one specific paper, keep the shorter existing order:

```text
paper-repo-discovery
  -> repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
  -> repo-experiment-prepare
```

For a user-specified existing repository, skip discovery and repository selection but keep the same preparation tail:

```text
repo-onboard
  -> repo-resource-prepare
  -> repo-environment-setup
  -> repo-baseline-run
  -> repo-experiment-prepare
```

Keep unexpected failure diagnosis, safe repair decisions, user approval gates, and fix reports in `agent-fix-error-recovery`. Keep intended method development and experiment design in `repo-experiment-prepare`.

Keep reusable AgentFix error lessons and reference notes in `agent-fix-knowledge-base`; do not use prior lessons to bypass user approval or environment-choice gates.

Invoke `agent-fix-error-recovery` automatically after a failed paper-repo workflow command. Do not ask the user whether to diagnose or run low-risk checks; ask only before applying medium/high-risk fixes, large downloads, dependency/environment changes, protocol-affecting edits, or destructive operations.

Keep per-paper source understanding in `paper-digest`.

Keep single-paper wiki planning in `paper-ingest`.

Keep multi-paper transaction control in the batch agent.
