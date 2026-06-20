# Environment Troubleshooting Cases

Use this file only when the main `repo-env-troubleshooting` guidance is not enough.

## absl help false failure

Some absl applications print complete help text and exit nonzero. If imports pass and the help output is valid, treat the failure as a validation-command issue. Replace the check with a narrow import or entrypoint load check and record the reason in the setup report.

## Slow package installs

Prefer command-scoped mirrors first. For pip, use a fast mirror only when it serves compatible packages and does not change requested versions. For conda, ask before changing global `.condarc`; prefer command-scoped channels or environment-local configuration.

## Existing environment name

An existing environment may be reused only when the user selected that exact environment for the current repository. Otherwise ask for a repository-specific name or path.
