---
name: agent-fix-knowledge-base
description: Consult and maintain a reusable AgentFix troubleshooting knowledge base for difficult repository setup, resource, environment, validation, baseline, and experiment failures. Use when AgentFix needs prior solved cases, external reference notes, accumulated error patterns, or a place to append concise lessons after resolving non-trivial errors, while preserving user approval gates and scientific protocol.
---

# Agent Fix Knowledge Base

Use this skill as AgentFix's reference memory. It helps AgentFix avoid re-solving the same difficult issues and gives a disciplined place to record new lessons.

This skill is advisory. It does not replace `agent-fix-error-recovery`, and it must not execute repairs directly.

## Read Order

When diagnosing a non-trivial failure, read only the references needed for the error category:

- Environment, dependency, CUDA, framework, mirror, or validation failures: read `references/error_cases.md`, then use `repo-env-troubleshooting` if available.
- Resource download, path binding, missing file, or archive failures: read `references/error_cases.md`.
- Baseline metric parsing or benchmark failures: read `references/error_cases.md`.

If the current error is simple and already covered by `agent-fix-error-recovery` safe fixes, do not load extra references.

## How To Use Prior Cases

For each relevant prior case:

- match on symptoms, package names, framework versions, resource names, command type, and stage
- treat the prior solution as a candidate, not proof
- verify against the current repository's docs and config
- prefer the smallest protocol-preserving fix
- keep all installs in the user-selected repository environment
- preserve the resource/environment gate: no resource or dependency download before the user has chosen current-env reuse or a new repository-specific environment

## External Reference Notes

When searching online or reading external docs during a fix, store only compact reference notes in the report or knowledge entry:

- source URL or document name
- applicable error pattern
- relevant version constraints
- recommended fix
- confidence and caveats

Do not copy long external text into reports or the knowledge file.

## Accumulating New Lessons

After resolving a non-trivial issue, append a concise case note to the active run's fix report. If the user explicitly asks to promote it into the shared skill knowledge base, append it to `references/error_cases.md`.

Use this shape:

```markdown
## Case: short title
- Stage:
- Symptoms:
- Root cause:
- Fix:
- Verification:
- Scope:
- Risk:
- Source:
```

Only promote cases that are reusable and evidence-backed. Do not promote one-off hacks, unverified guesses, or changes that alter experimental protocol.

## Safety

Never use a prior case to justify:

- changing datasets, labels, splits, metrics, or evaluation logic without approval
- installing into the wrong environment
- skipping the required environment-choice gate
- downloading large or license-gated resources without approval
- changing package/framework versions only for convenience
- hiding a benchmark failure by changing success criteria
