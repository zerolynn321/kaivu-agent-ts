---
name: research-scope-planning
description: Frame an open-ended research need into a concrete experiment search scope before repository selection. Use when Codex is given a research goal, method idea, application area, comparison target, or benchmark-seeking request rather than one specific paper, and must identify the task type, constraints, candidate method families, benchmark families, datasets, metrics, success criteria, exclusions, and unresolved questions before searching for experiment repositories. This skill does not clone repositories, install dependencies, download datasets, or run baselines.
---

# Research Scope Planning

Use this skill to turn a broad research demand into a scoped experiment search plan that later skills can use to select a repository and benchmark.

The agent does the planning interactively. Do not implement a separate Python or TypeScript pipeline for this logic.

## Terminal Output

Keep terminal-facing progress concise. Report only stage status, key assumptions, user decisions needed, artifact paths, and next step. Put detailed evidence, search notes, and alternatives in `research_scope_report.md`.

## Agent Contract

Role: `AgentResearchFrame`

Inputs:

- user research need, hypothesis, topic, method idea, or desired comparison
- optional constraints such as GPU, runtime, domain, data availability, license, privacy, deadline, or preferred framework
- optional prior paper, repository, benchmark, or result references

Required outputs:

- `research_scope.yaml`
- `research_scope_report.md`

Handoff:

- After scope artifacts exist, hand off to `experiment-repo-selection`.
- Do not proceed into repository cloning, resource download, environment setup, or baseline execution.

## Workflow

1. Normalize the research demand.
   - Restate the core research question in one or two concrete sentences.
   - Identify task type, domain, input/output form, target evaluation behavior, and what would count as useful experimental evidence.
   - Distinguish must-have requirements from preferences.
   - Ask the user only when the ambiguity changes the repository or benchmark search space materially.

2. Identify constraints and exclusions.
   - Record compute budget, allowed runtime, local hardware, external API/token restrictions, dataset privacy, preferred languages/frameworks, and whether large pretrained models or full training are allowed.
   - Record exclusions such as no private datasets, no huge downloads, no closed-source services, no fragile multi-repo assembly, or no long training.

3. Discover method and benchmark space.
   - Use live lookup when the current state of papers, repositories, benchmark pages, or leaderboards matters.
   - Search for representative papers, surveys, benchmark suites, datasets, standard metrics, and common baselines.
   - Prefer primary sources, official benchmark pages, official code repositories, Papers with Code, arXiv/OpenReview pages, author pages, and well-maintained benchmark libraries.
   - Record enough evidence for the repo selection stage to audit why a method family or benchmark was included.

4. Propose the experiment search scope.
   - List candidate method families and why each is relevant.
   - List candidate benchmark families, datasets, metrics, and common baselines.
   - Mark each candidate as `recommended`, `possible`, or `out_of_scope`.
   - Call out likely risks: unavailable data, missing official code, expensive training, incompatible frameworks, unclear metrics, or benchmark mismatch.

5. Write artifacts.
   - Create `research_scope.yaml` in the task run directory when one exists; otherwise create it in a clear local work directory.
   - Create `research_scope_report.md` next to it.
   - Include unresolved questions that later stages must resolve before clone or assembly.

## `research_scope.yaml` Shape

```yaml
research_need:
  original_request: ""
  normalized_question: ""
  task_type: ""
  domain: ""
  expected_evidence: ""

constraints:
  compute: ""
  runtime: ""
  data_policy: ""
  framework_preferences: []
  license_constraints: []
  exclusions: []

method_families:
  - name: ""
    status: "recommended" # recommended | possible | out_of_scope
    rationale: ""
    representative_papers: []
    expected_repo_patterns: []

benchmark_space:
  datasets: []
  metrics: []
  protocols: []
  common_baselines: []
  leaderboards_or_sources: []

selection_criteria:
  must_have: []
  nice_to_have: []
  risk_flags: []

open_questions: []
evidence: []
next_skill: "experiment-repo-selection"
```

## Decision Rules

- Mark the scope as ready only when repository selection can proceed without guessing the task, benchmark family, or success criteria.
- Prefer a narrower, executable scope over a broad survey when the user wants an experiment base.
- Keep benchmark candidates tied to the research question; do not list popular datasets just because they are common in the field.
- If the research need is actually one specific paper, hand off to `paper-repo-discovery` instead of using this skill.

## Boundaries

Do:

- clarify research goal, benchmark space, and selection criteria
- use web lookup for current paper, benchmark, and repository ecosystem facts
- create audit-friendly scope artifacts
- prepare the next stage to compare repositories

Do not:

- clone repositories
- choose the final repository
- assemble multi-repo workspaces
- download datasets or checkpoints
- install dependencies or create environments
- run baselines or modify experiment code
