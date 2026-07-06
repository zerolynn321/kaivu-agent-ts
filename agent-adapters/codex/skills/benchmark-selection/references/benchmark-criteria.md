# Minimum Benchmark Criteria

## Hard Gates

A selected benchmark unit must pass every applicable gate:

1. **Research fit**
   - The input, target, task, and intended optimization match the requirement.

2. **Original-method evidence**
   - The route executes or evaluates the original method and produces a meaningful metric or output.
   - Import checks and unrelated demos do not pass.

3. **Representative input**
   - At least one public, bundled, or otherwise approved dataset/input is available.
   - One representative dataset is sufficient.

4. **Traceable provenance**
   - Dataset, checkpoint, released result, and evaluator sources are identifiable.

5. **Protocol and leakage safety**
   - Split, temporal boundary, preprocessing, and available-at-decision-time information are compatible with the intended claim.

6. **Comparable output**
   - The result can be preserved as the baseline comparator for later optimization on the same protocol.

7. **Resource feasibility**
   - Required downloads, environment, memory, runtime, and hardware fit the user constraints or have explicit approval.

## Route Preference

Prefer the first valid route:

1. official pretrained checkpoint plus documented evaluation;
2. official released prediction/result plus documented evaluator;
3. bundled representative data plus evaluation;
4. one established public dataset plus evaluation;
5. the shortest necessary documented training route.

Do not retrain solely to regenerate an official artifact that already supplies the required original-method result.

## Adaptation Rules

Allow bounded adaptation when it preserves scientific meaning:

- file-format conversion;
- local data loader;
- timestamp or modality alignment;
- leakage-safe split correction;
- equivalent local metric evaluator;
- path or configuration binding.

Treat changes to target, labels, population, metric meaning, or evaluation timing as a new benchmark decision requiring explicit justification and user approval.

## Minimum Versus Optional Scope

Required scope:

- one representative dataset/input;
- one original-method route;
- one primary metric or meaningful output;
- enough provenance and protocol detail for later comparison.

Optional scope:

- additional datasets;
- additional horizons;
- multiple seeds;
- full paper tables;
- secondary comparisons;
- appendix experiments;
- full retraining when released artifacts are sufficient.

Optional scope must not block repository initialization unless the user explicitly requests it.

## Readiness

Set `status: ready` when:

- one route passes every hard gate;
- the required input and output are explicit;
- adaptation obligations are bounded;
- repository search can evaluate implementation fit;
- no unresolved choice changes the scientific target or resource class.

Set `needs_user_confirmation` for materially different valid targets, licenses, private access, or resource classes.

Set `blocked` when no lawful, leakage-safe, meaningful, and feasible original-method result can be defined.
