# AgentFix Error Cases

Add compact reusable cases here only when the user explicitly asks to promote a solved issue into the shared skill knowledge base.

## Case: absl help exits with code 1
- Stage: environment validation
- Symptoms: dependency imports pass, command prints valid absl help text, process exits nonzero.
- Root cause: validation command convention rather than missing dependency.
- Fix: replace broad `--help` validation with a narrower import or entrypoint validation that exercises the same imports without running baseline logic.
- Verification: import/entrypoint validation passes in the selected environment.
- Scope: absl-based Python entrypoints.
- Risk: low when the replacement validation does not change benchmark command or success criteria.
- Source: prior local CLSR-style environment setup run.

## Case: generic active environment reused accidentally
- Stage: resource preparation or environment setup
- Symptoms: setup proceeds in `base`, `autosota`, or Codex runtime env because it is currently active.
- Root cause: active shell environment was mistaken for repository-specific user approval.
- Fix: stop before resource/dependency downloads and ask the user to choose current-env reuse or a new repository-specific environment name/path.
- Verification: manifest or environment plan records the selected environment and setup commands target it.
- Scope: all paper-repo workflow stages before downloads.
- Risk: high if ignored; dependencies can pollute unrelated environments.
