# Benchmark Decision Criteria

## Contents

1. Benchmark contract
2. Existing benchmark hard gates
3. Candidate comparison rubric
4. Adopt, adapt, or construct
5. Benchmark construction standard
6. Protocol and fairness standard
7. Readiness and rejection rules

## 1. Benchmark contract

Define these fields before evaluating candidates:

- research claim the experiment is intended to support
- task unit and unit of analysis
- observable inputs at the decision or prediction time
- target, label, outcome, or expected output
- domain, population, geography, entities, and time range
- prediction horizon, context window, or intervention point when applicable
- comparison target and minimum useful evidence
- data, license, privacy, compute, runtime, and service constraints
- exclusions and known invalid shortcuts

Do not choose a dataset first and retrofit the research question around it.

## 2. Existing benchmark hard gates

A candidate must pass every applicable gate:

1. **Task and protocol fit**
   - The input, target, task unit, evaluation timing, and intended use match the research contract.
   - A superficially similar domain is not enough.

2. **Lawful and practical access**
   - The dataset, labels, and required metadata are available under compatible terms.
   - Authentication, private agreements, geographic restrictions, and expected size are explicit.

3. **Traceable provenance**
   - Original source, version, collection process, label construction, and known corrections are identifiable.
   - Derived data can be traced to the upstream source and transformation.

4. **Split and leakage safety**
   - Train, validation, and test units are separated according to the claim.
   - Temporal tasks use cutoffs that prevent future information, including future text, revised records, global normalization, and post-outcome features.
   - Entity, user, patient, location, document, or near-duplicate leakage is controlled when relevant.

5. **Metric validity**
   - Primary metrics reflect the scientific objective and are computable from released outputs.
   - Aggregation does not conceal important subgroup, horizon, class, or scale behavior.

6. **Runnable evaluation path**
   - A sufficiently precise evaluation protocol or implementation exists to reproduce scoring.
   - Hidden evaluation services are acceptable only when the user permits them and reproducible local alternatives are unnecessary.

Reject or block any candidate that fails a hard gate unless a documented adaptation can repair it without changing the intended claim.

## 3. Candidate comparison rubric

Score each dimension from 0 to 3 after hard gates pass:

- `0`: absent or contradicted
- `1`: weak, unclear, or high risk
- `2`: adequate with bounded caveats
- `3`: strong and directly evidenced

Dimensions:

| Dimension | What to assess |
| --- | --- |
| Research fit | Directness of support for the intended claim |
| Task fidelity | Input, target, unit, horizon, and protocol alignment |
| Data quality | Coverage, representativeness, missingness, label quality, and provenance |
| Split integrity | Leakage protection and realistic generalization boundary |
| Metric quality | Validity, robustness, aggregation, and uncertainty reporting |
| Baseline coverage | Naive, classical, standard learned, and task-relevant baselines |
| Evaluation tooling | Scripts, schemas, deterministic scoring, and output validation |
| Reproducibility | Versioning, documented preprocessing, fixed splits, and artifacts |
| Resource feasibility | Download, memory, compute, runtime, and external-service needs |
| Maintenance and adoption | Current availability, corrections, community use, and issue state |
| Adaptation cost | Amount and scientific risk of required local work |

Do not use the sum as an automatic decision. Report failed or weak dimensions separately, and prefer the simplest candidate that satisfies the research contract with acceptable risk.

## 4. Adopt, adapt, or construct

### Adopt existing

Choose when:

- every hard gate passes;
- the benchmark tests the intended claim directly;
- released splits and metrics are suitable;
- required resources fit the constraints;
- no local change is needed beyond ordinary configuration or documented preprocessing.

### Adapt existing

Choose when:

- the underlying data and task remain scientifically suitable;
- the mismatch is bounded and explicit;
- adaptation does not use unavailable-at-decision-time information;
- original results remain distinguishable from locally adapted results;
- the adapted protocol is versioned and its fairness invariants can be frozen.

Typical adaptations:

- local data loader or file-format conversion;
- timestamp or modality alignment;
- leakage-safe split correction;
- adding a scientifically necessary metric;
- replacing an unavailable hosted evaluator with an equivalent local evaluator;
- creating a bounded subset for smoke validation while retaining the full formal protocol.

Do not call it adaptation when changing the target, population, scientific claim, label semantics, or evaluation objective. Treat those changes as constructing a new benchmark.

### Construct new

Choose only when:

- no existing benchmark passes the task/protocol fit gate;
- available benchmarks omit a required modality, target, population, horizon, or evaluation behavior;
- combining traceable source data can test the claim validly;
- the team can define reproducible splits, metrics, baselines, and validation checks.

## 5. Benchmark construction standard

A constructed benchmark must define:

1. **Requirement traceability**
   - Map every research requirement to data fields, protocol rules, metrics, baselines, and acceptance evidence.

2. **Source inventory**
   - Record source owner, URL or location, version or retrieval date, license, coverage, schema, size estimate, and checksums when acquired.

3. **Cohort or sample construction**
   - Define inclusion, exclusion, filtering, unit of analysis, deduplication, and label creation.
   - Quantify attrition from raw data to final samples.

4. **Alignment**
   - Define joins across time, entity, geography, modality, or identifiers.
   - State allowable information at each prediction or decision point.
   - Define lag, event window, timezone, calendar, and revision handling.

5. **Splits**
   - Freeze train, validation, and test rules before method comparison.
   - Prefer chronological splits for forecasting and future-facing tasks.
   - Use group-aware splits when samples share entities, users, documents, sites, or subjects.
   - Reserve the test set from iterative tuning.

6. **Data quality**
   - Specify missingness, corruption, outliers, duplicates, label noise, class balance, coverage gaps, and subgroup checks.
   - Define deterministic handling rules and record their impact.

7. **Metrics**
   - Select a primary metric tied to the intended claim.
   - Add secondary metrics for robustness, scale, calibration, subgroup, horizon, or operational behavior as appropriate.
   - Define direction, units, aggregation, tie handling, confidence intervals, and statistical comparisons.

8. **Baselines**
   - Include a trivial or persistence baseline where meaningful.
   - Include a classical or simple learned baseline.
   - Include a recognized task-standard baseline.
   - Keep the proposed method out of benchmark construction decisions.

9. **Protocol controls**
   - Freeze preprocessing boundaries, seeds, horizons, tuning budget, compute budget, early stopping, checkpoint selection, and allowed external data.
   - Apply the same evaluation path to baseline and proposed methods.

10. **Version and audit trail**
    - Assign a benchmark name and version.
    - Record source versions, construction configuration, split manifests, schema, checksums, and change history in machine-readable artifacts.

11. **Acceptance tests**
    - Schema and type validation.
    - Split disjointness and duplicate checks.
    - Temporal and feature-availability leakage checks.
    - Label and metric sanity checks.
    - Deterministic evaluator checks on a tiny fixture.
    - Trivial-baseline result and expected-range checks.
    - Resource estimate for the full protocol.

## 6. Protocol and fairness standard

Freeze these as fairness invariants before method comparison:

- dataset version and eligible samples;
- split membership and temporal cutoff;
- target and label semantics;
- permitted input information;
- preprocessing fit boundary;
- horizons or evaluation conditions;
- primary metrics and aggregation;
- tuning and compute budget;
- seeds or uncertainty procedure;
- baseline and proposed-method evaluation code path.

Any change to an invariant creates a new benchmark version or requires explicit user approval and a full rerun of affected comparisons.

## 7. Readiness and rejection rules

Set `status: ready` only when:

- the benchmark contract is complete;
- one decision mode is justified;
- every selected candidate passes hard gates;
- the formal protocol and fairness invariants are explicit;
- construction or adaptation obligations and acceptance tests are listed;
- repository selection can judge compatibility without inventing missing rules.

Set `needs_user_confirmation` when choices imply materially different:

- scientific claims or task definitions;
- datasets, populations, or labels;
- licenses, privacy constraints, or external services;
- resource classes or large downloads;
- primary metrics or split semantics.

Set `blocked` when:

- required data or labels are unavailable;
- lawful use cannot be established;
- leakage cannot be prevented or assessed;
- no valid metric or evaluation design exists;
- the required benchmark exceeds non-negotiable constraints.
