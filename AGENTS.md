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

## General Research Skills

- `problem-frame`: clarify broad or ambiguous requests before literature review, paper wiki work, hypothesis generation, experiment planning, or research-oriented implementation.
- `literature-review`: frame research questions, generate and validate literature search queries, search external literature sources, and return ranked candidate papers.
- `literature-search`: run external literature search with `rag_arxiv_retrieve` and return candidate papers.
- `paper-repo-discovery`: given a specific paper title, URL, DOI, arXiv/OpenReview page, PDF, or local paper file, find the official or most credible public code repository, verify evidence, ask for confirmation when ambiguous, clone the selected repository locally, and write a resolution report.
- `repo-onboard`: after a paper repository has been cloned or selected, act as AgentOnboard to reuse an existing root `config.yaml` or scan the repository and create one locally before resource, environment, or baseline stages.
- `repo-resource-prepare`: after repository onboarding, act as AgentInit to ask whether to reuse the current environment or create a new repository-specific environment before resource download, then identify required datasets, models, checkpoints, caches, and path assumptions; stage all required resources under the run directory; bind repository paths when needed; and write resource manifest and acquisition reports before dependency installation. Do not proceed from old `config.yaml` environment metadata alone.
- `repo-environment-setup`: after resource preparation, act as AgentInit to verify setup commands target the environment selected or created by `repo-resource-prepare`, then infer, install, and validate runtime dependencies only inside that environment; ask before environment-changing dependency actions; and invoke AgentFix automatically on setup or validation failure.
- `agent-fix-error-recovery`: automatically use this when resource download, environment setup, validation, baseline, or experiment execution fails; act as AgentFix to diagnose the error, execute common low-risk fixes, ask only before risky actions, verify the result, and write a fix report.

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

Keep paper-to-code repository discovery and cloning in `paper-repo-discovery`.

Keep cloned-repository onboarding and local `config.yaml` creation in `repo-onboard`.

Keep the explicit environment choice before downloads, required runtime resource discovery, download/copy, staging, and repo path binding in `repo-resource-prepare`.

Keep repository-specific virtual environment targeting, runtime dependency planning/installation, CUDA/PyTorch/TensorFlow compatibility, and cheap validation checks in `repo-environment-setup`.

Keep failure diagnosis, safe repair decisions, user approval gates, and fix reports in `agent-fix-error-recovery`.

Invoke `agent-fix-error-recovery` automatically after a failed paper-repo workflow command. Do not ask the user whether to diagnose or run low-risk checks; ask only before applying medium/high-risk fixes, large downloads, dependency/environment changes, protocol-affecting edits, or destructive operations.

Keep per-paper source understanding in `paper-digest`.

Keep single-paper wiki planning in `paper-ingest`.

Keep multi-paper transaction control in the batch agent.
