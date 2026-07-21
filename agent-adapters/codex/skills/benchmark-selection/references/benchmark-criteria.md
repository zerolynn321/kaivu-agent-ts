# Minimum Benchmark Criteria

## Hard Gates

A selected benchmark unit must pass every applicable gate:

1. **Research fit**
   - The input, target, task, and intended optimization match the requirement.

2. **Original-method evidence**
   - The route executes or evaluates the original method and produces a meaningful metric or output.
   - Import checks and unrelated demos do not pass.

3. **Core-claim alignment**
   - The benchmark records a traceable chain from the research requirement or paper's main empirical claim to the claim-bearing method behavior, representative task/data, evaluator, primary metric, and documented reference result when available.
   - Each element is supported by the paper, official repository instructions, benchmark documentation, or released-result metadata.
   - An official example is not sufficient merely because it is official; it must exercise the path and metric that support the relevant claim.
   - For a dataset-level empirical claim, one prediction or arbitrary-folder inference cannot replace benchmark evaluation. Require a representative paper dataset or justified subset, the paper-aligned evaluator, and the primary aggregate metric.

4. **Core-method execution**
   - Determine whether the contribution is a procedure that creates or changes a scientific artifact.
   - If it is, require one faithful execution of the claim-bearing stages that produces a new evaluable artifact. Evaluation of an author-provided artifact alone is `evaluation_only`.
   - If scaled execution is necessary, preserve the mechanism and record changed budget parameters and scientific impact.

5. **Representative input**
   - At least one public, bundled, or otherwise approved dataset/input is available.
   - One representative dataset is sufficient.

6. **Traceable provenance**
   - Dataset, checkpoint, released result, and evaluator sources are identifiable.

7. **Protocol and leakage safety**
   - Split, temporal boundary, preprocessing, and available-at-decision-time information are compatible with the intended claim.

8. **Comparable output**
   - The result can be preserved as the baseline comparator for later optimization on the same protocol.

9. **Controlled comparison for comparative requirements**
   - If the user asks whether a factor improves performance, the benchmark must define the minimum treatment/control or reference branches needed to answer that question.
   - The branches must share the same dataset/input, split, primary metric, resource budget, and available-information boundary unless a difference is explicitly part of the claim.
   - Do not require control/treatment branches for non-comparative questions when one controlled experiment can directly answer the requirement.

10. **Resource feasibility**
   - Required downloads, environment, memory, runtime, and hardware fit the user constraints or have explicit approval.

11. **Protocol fidelity**
   - Use the paper's epochs/steps, data scale, model configuration, evaluation episodes, evaluator, and primary metric for the selected core experiment when feasible.
   - Reduce breadth first: fewer datasets, seeds, secondary methods, ablations, or sweep points usually preserve the selected experiment better than shortening its convergence- or performance-bearing protocol.
   - Any shortened core protocol records a concrete material constraint, cost evidence, changed parameters, expected scientific impact, and the closest full-paper command.

## Smoke-Test Boundary

Treat the following as engineering validation, not a final scientific baseline, unless the core claim explicitly concerns that behavior:

- environment construction, reset, stepping, rendering, imports, or CLI help;
- random or untrained actions;
- observing any finite or nonzero reward without task completion evidence;
- one forward pass without the paper-aligned task metric;
- a toy or generic demo disconnected from the source paper's representative evaluation.
- single-image, single-sample, or arbitrary-folder inference when the paper reports dataset-level metrics.

Require the smallest feasible claim-bearing route. When the paper reports an aggregate outcome, raw intermediate outputs are not a faithful substitute.

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
- one original-method route or other smallest controlled experiment that answers the requirement;
- the smallest controlled comparison only for comparative open-ended requirements;
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

Do not classify a reduced-epoch or reduced-data run as paper-result reproduction merely because it matches a deterministic golden value created for that shortened configuration. It may be a valid local regression or optimization baseline, but paper-level alignment requires evidence that the shortened protocol preserves the reported result or conclusion.

## Readiness

Set `status: ready` when:

- one route passes every hard gate;
- the claim-to-task-to-method-to-metric evidence chain is explicit and is not `smoke_only`;
- the required input and output are explicit;
- adaptation obligations are bounded;
- repository search can evaluate implementation fit;
- no unresolved choice changes the scientific target or resource class.

Set `needs_user_confirmation` for materially different valid targets, licenses, private access, or resource classes.

Set `blocked` when no lawful, leakage-safe, meaningful, and feasible original-method result can be defined.
