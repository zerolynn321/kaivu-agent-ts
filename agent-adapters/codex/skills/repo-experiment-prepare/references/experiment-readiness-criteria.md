# Experiment Readiness Criteria

## Contents

1. Readiness modes
2. Starting-state and traceability checks
3. Gap classification
4. Modification and integration standard
5. Experiment design standard
6. Validation standard
7. Final readiness gates

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

- primary repository remote, branch, commit, submodules, and component commits;
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
   - original baseline mode still resolves and runs;
   - unchanged protocol fields remain unchanged;
   - output and metric parsing remain compatible;
   - material regression is investigated rather than hidden by new thresholds.

4. **Branch dry runs**
   - every experiment-matrix branch reaches its intended code path;
   - expected outputs are created in isolated locations;
   - metrics are parseable;
   - checkpoints or intermediate artifacts are usable when required;
   - failure and resume behavior are explicit.

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
- no unresolved scientific or protocol decision remains;
- original baseline mode is preserved;
- benchmark and fairness invariants are frozen;
- experiment plan and matrix are complete;
- every branch passes a bounded dry run;
- expected outputs and metrics are verified;
- batch entrypoint is generated and syntax-checked;
- formal resource estimates and approval requirements are recorded;
- full formal experiments have not started.

Set `needs_user_decision` when a missing choice changes scientific meaning, architecture, licensing, protocol, or resource class.

Set `needs_implementation` when the goal and protocol are clear but required code, integration, tests, or experiment branches remain incomplete.

Set `blocked` when required resources, legal access, environment, repository state, or a valid experiment design cannot be established.
