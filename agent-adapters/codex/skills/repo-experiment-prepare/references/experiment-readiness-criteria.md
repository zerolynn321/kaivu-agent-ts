# Experiment Readiness Criteria

## Contents

1. Readiness modes
2. Starting-state and traceability checks
3. Gap classification
4. Modification and integration standard
5. Experiment design standard
6. Validation standard
7. Final readiness gates
8. Formal-run documentation
9. Human-readable final report

## 1. Readiness modes

### Optimization

Use for a specific paper or explicitly selected repository.

Generic structural readiness requires:

- a reproducible baseline command and recorded result;
- identifiable training, evaluation, model, data, configuration, checkpoint, and output interfaces;
- parameterized experiment configuration rather than one-off source edits;
- an original-baseline mode that remains available after modifications;
- bounded validation commands and isolated output paths.

Method-specific readiness additionally requires:

- an explicit optimization goal or hypothesis;
- target files, symbols, and extension points;
- intended behavioral change and unchanged protocol invariants;
- baseline, proposed method, controls, and ablations;
- implementation and dry-run evidence.

Do not invent a method-specific objective. When only generic readiness can be assessed, record the missing goal as a user decision.

### Requirement validation

Use for an open-ended research need.

Require a complete mapping:

```text
research requirement
-> benchmark clause
-> repository or component
-> file, symbol, or interface
-> experiment branch
-> command and expected artifact
-> dry-run evidence
```

A repository is not ready merely because its original baseline runs. Every required new modality, method, integration, evaluator, control, and acceptance criterion must be implemented or explicitly blocked.

## 2. Starting-state and traceability checks

Record:

- primary workspace path and component paths;
- remotes, branches, commits, and dirty paths when already available, for provenance only;
- dirty and untracked paths before edits;
- protected or user-owned files;
- selected environment and resource manifests;
- baseline command, configuration, metrics, logs, and output artifacts;
- authoritative research, benchmark, and repository-selection artifacts;
- source and license for every external component.

Before editing, inspect the real files and symbols named by documentation or prior reports. Replace stale planned locations with verified current locations.

## 3. Gap classification

Use these categories:

| Gap | Meaning |
| --- | --- |
| `configuration_gap` | Required behavior exists but cannot be selected reproducibly |
| `data_adapter_gap` | Required data or modality cannot enter the model/evaluator correctly |
| `evaluation_gap` | Metrics, aggregation, outputs, or evaluator integration are incomplete |
| `method_implementation_gap` | The proposed method or optimization behavior is not implemented |
| `cross_repo_integration_gap` | Components exist separately but have no verified interface |
| `workspace_completeness_gap` | The connected workflow still depends on missing or undocumented source outside the current workspace |
| `protocol_decision_gap` | A scientific rule is missing or ambiguous |
| `resource_or_environment_gap` | Required runtime dependency or resource remains unavailable |

For each gap, record:

- requirement and evidence that exposed it;
- current and target behavior;
- files, symbols, schemas, and commands involved;
- benchmark invariants that must not change;
- implementation steps and rollback path;
- approval state;
- focused validation and regression checks.

## 4. Modification and integration standard

Prefer, in order:

1. existing extension points and configuration;
2. adapters or wrappers;
3. isolated modules with explicit interfaces;
4. bounded edits to existing implementation;
5. source copying or deep multi-repository merge only when necessary.

For cross-repository integration:

- record source URL, exact commit, license, role, and copied or imported paths;
- define input/output schema, shapes, dtypes, devices, lifecycle, and error behavior;
- isolate component-specific dependencies when possible;
- avoid duplicated training loops, evaluators, or data pipelines;
- preserve a primary runnable root and a single formal experiment entrypoint;
- test the interface with a tiny deterministic fixture.

A directory containing multiple repositories is not an integrated codebase. Neither is a single Git repository that merely colocates their files.

Content-level integration requires all of the following:

- one documented architecture with a primary package/root and an explicit role for every component;
- one root-level formal entrypoint that executes the complete scientific workflow;
- explicit programmatic interfaces between components, including schemas, variable ordering, split and normalization boundaries, artifact formats, validation, and error behavior;
- automatic upstream-to-downstream artifact flow with provenance, without manual file copying, path editing, or directory switching;
- one root control plane for configuration, environment setup, benchmark selection, seeds, metrics, outputs, checkpointing, resume, launch, and summarization;
- one frozen benchmark and evaluation contract shared by baseline, proposed method, controls, and ablations;
- root-level access to the preserved baseline and all formal branches;
- focused interface tests plus a bounded end-to-end run through the real component boundary;
- no undocumented runtime dependence on the original component checkouts.

Source colocation, successful imports, a shell wrapper around unrelated CLIs, or separately runnable components are not sufficient evidence. Judge integration from the connected scientific workflow and its observed dataflow first.

For local workspace completeness:

- keep every required source component and integration layer under the selected server workspace, unless it is a documented installed dependency;
- allow external datasets, checkpoints, services, and environment packages when the manifest records them and the current machine can resolve them;
- reject undocumented runtime dependence on missing sibling source trees or manual cross-component file transfer;
- run the root entrypoint from the current workspace through the complete bounded dataflow;
- treat Git remotes, commits, tracked status, nested `.git` directories, and clean-clone reconstruction as irrelevant to readiness.

Do not run `git init`, `git add`, `git commit`, configure author identity, remove nested `.git`, or create a clean clone for this skill. Those actions belong to an explicit version-control or publication request, not experiment preparation.

Ask before:

- changing labels, population, splits, metrics, timing, target, model objective, or scientific claim;
- changing a major architecture or framework stack;
- copying code under unclear or incompatible terms;
- overwriting existing implementations or user changes;
- introducing a materially larger resource class.

## 5. Experiment design standard

Freeze:

- dataset and version;
- eligible samples and split membership;
- feature availability and preprocessing fit boundary;
- target, labels, horizons, and evaluation timing;
- primary and secondary metrics, direction, units, and aggregation;
- seeds and uncertainty procedure;
- tuning policy, early stopping, checkpoint selection, and compute budget;
- allowed external data, pretrained models, and services;
- output naming, isolation, and retention.

The experiment matrix must include:

- preserved original baseline;
- every required formal baseline;
- proposed method;
- controls that isolate alternative explanations;
- ablations for material new components;
- one formal and one dry-run command per branch;
- expected outputs and resource estimates.

Dry-run reductions may change sample count, epochs, steps, or model size only in an explicitly separate smoke configuration. They must exercise the same implementation and evaluation path and must not overwrite formal settings.

## 6. Validation standard

Apply relevant checks:

1. **Static and interface**
   - syntax, formatting, type or schema checks;
   - imports and compilation;
   - configuration resolution;
   - tensor, table, or message shapes and dtypes;
   - device and checkpoint compatibility.

2. **Focused tests**
   - deterministic tiny fixtures;
   - adapter alignment and boundary cases;
   - evaluator and metric sanity checks;
   - leakage and split assertions;
   - output and resume behavior.

3. **Baseline regression**
   - original baseline mode still resolves and runs after the source changes;
   - unchanged protocol fields remain unchanged;
   - output and metric parsing remain compatible;
   - material regression is investigated rather than hidden by new thresholds.
   - a pre-existing metrics checksum alone does not prove post-change regression;
   - save the executed command and a non-empty evidence file.

4. **Branch dry runs**
   - every experiment-matrix branch reaches its intended code path;
   - expected outputs are created in isolated locations;
   - metrics are parseable;
   - checkpoints or intermediate artifacts are usable when required;
   - failure and resume behavior are explicit.
   - save a non-empty evidence file and `dry_run_status: passed` for every matrix branch.

5. **Batch entrypoint**
   - script syntax passes;
   - environment and working directory are explicit;
   - commands correspond exactly to matrix entries;
   - failures stop or record status predictably;
   - validation does not launch the full batch.

Use `agent-fix-error-recovery` for unexpected operational failures. Return planned feature gaps, incorrect method behavior, and experiment-design changes to `repo-experiment-prepare`.

## 7. Final readiness gates

Set `ready_for_formal_run` only when all are true:

- baseline and repository starting state are recorded;
- all requirements have traceability entries;
- every required gap is implemented and verified;
- component responsibilities and the integrated architecture are explicit;
- one root entrypoint drives the complete required workflow;
- component interfaces and artifact contracts are implemented and validated;
- configuration, environment, benchmark, evaluation, outputs, and resume behavior are controlled coherently from the root;
- no manual inter-component handoff or conflicting scientific control plane remains;
- a bounded end-to-end run exercises the real complete dataflow;
- all source required by the current server run is present under the workspace or supplied by documented installed dependencies;
- no undocumented external source path or manual inter-component file transfer remains;
- the root entrypoint passes the bounded integration path in the current workspace and selected environment;
- no unresolved scientific or protocol decision remains;
- original baseline mode is preserved;
- benchmark and fairness invariants are frozen;
- experiment plan and matrix are complete;
- every branch passes a bounded dry run;
- expected outputs and metrics are verified;
- batch entrypoint is generated and syntax-checked;
- repository README contains the managed formal-experiment section and exact command;
- formal resource estimates and approval requirements are recorded;
- full formal experiments have not started.

Before declaring readiness, directly inspect the final repository and re-check the commands and outputs represented by the artifacts. Missing code, configurations, matrix branches, pending dry runs, absent evidence, simplified readiness schemas, missing post-change baseline regression, or missing README instructions must prevent readiness. Do not accept a self-reported status field as evidence by itself.

Set `needs_user_decision` when a missing choice changes scientific meaning, architecture, licensing, protocol, or resource class.

Set `needs_implementation` when the goal and protocol are clear but required code, integration, tests, or experiment branches remain incomplete.

Set `blocked` when required resources, legal access, environment, workspace contents, or a valid experiment design cannot be established. Missing Git identity, commits, or tracked status are not blockers.

## 8. Formal-run documentation

Add or update a managed section in the primary repository README:

````markdown
<!-- kaivu-formal-experiment:start -->
## Formal Experiments

### Prerequisites
...

### Run
```bash
<exact guarded formal command>
```

### Outputs and summary
...

Formal experiments have not been started by the preparation workflow.
<!-- kaivu-formal-experiment:end -->
````

Preserve all content outside the markers. The final user-facing response must repeat the exact formal command, repository path, environment, output location, summarizer command when available, and readiness artifact paths.

## 9. Human-readable final report

Use `experiment_readiness_report.md` as the single consolidated document for a researcher or engineer who needs to understand the prepared codebase without reading terminal history or raw YAML.

Use this section order:

1. **Executive summary**
   - Original goal, readiness mode, final status, and whether formal experiments have started.
   - One short paragraph describing the prepared method and comparison.

2. **Original requirement**
   - Preserve the user's wording when available.
   - Separate explicit requirements, constraints, exclusions, and success criteria.
   - If the original wording is unavailable, mark it missing and request it; do not silently infer it from implementation.

3. **Requirement-to-code mapping**
   - Use a table with: requirement ID, requirement, repository/component, repo-relative file, function/class/symbol, implemented behavior, experiment branch, and evidence.
   - Prefer stable symbol names over line numbers. Add line numbers only as optional navigation hints because they drift after edits.

4. **Baseline and fixed protocol**
   - Describe the original baseline, recorded result, environment, dataset, split, horizons, metrics, and protocol fields preserved for fairness.
   - Clearly distinguish a preserved artifact from a baseline regression executed after code changes.

5. **Implemented changes**
   - Organize by functional purpose rather than chronological edit order.
   - For each change, explain prior behavior, new behavior, files and symbols changed, configuration or CLI controls, provenance for external code, and why the change is needed.
   - For multi-repository solutions, describe the architecture, component roles, interfaces, complete dataflow, root control plane and entrypoint, end-to-end evidence, component paths, provenance, licenses, and current-workspace execution validation.

6. **Formal experiment design**
   - Explain datasets, splits, inputs, targets, metrics, seeds, horizons, baselines, proposed branches, controls, ablations, compute budget, checkpoint rule, and output isolation.
   - Summarize the experiment matrix in a readable table and link to `experiment_matrix.yaml` for full commands.

7. **Validation evidence**
   - Summarize static checks, focused tests, post-change baseline regression, and per-branch dry runs.
   - State what each check proves and what it does not prove.
   - Link to evidence and logs without pasting full transcripts.

8. **How to run formal experiments**
   - Give prerequisites, environment activation, working directory, exact guarded launcher command, matrix size, expected output paths, resume behavior, and exact summarizer command in copyable code blocks.
   - State whether formal runs have started and flag high-cost execution when applicable.

9. **Readiness decision and limitations**
   - Explain why the status is justified.
   - List unresolved scientific questions, excluded experiments, resource risks, and what remains after formal results are produced.

10. **Artifact index**
    - Link the method plan/report, experiment plan, matrix, readiness YAML, README, launcher, summarizer, configurations, tests, and evidence directories.

Writing rules:

- Write for a technical researcher, not for the Agent that produced the files.
- Prefer concise prose and tables over raw dictionaries, command logs, or YAML dumps.
- Define project-specific abbreviations on first use.
- Clearly label observed facts, planned formal actions, and scientific conclusions.
- Never present dry-run metrics as formal results.
- Re-read the final codebase so every path, symbol, and command is current before saving the report.
