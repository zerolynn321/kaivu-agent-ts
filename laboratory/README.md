# AutoSOTA Laboratory

This is a small Python-first prototype of the AutoSOTA pipeline.

It implements the high-level flow:

```text
onboard
  -> create paper config from a local repository

optimize
  -> Deep Research via OpenRouter
  -> build master_prompt.md
  -> run Claude Code in Docker for baseline, analysis, ideas, and experiments
  -> record scores.jsonl
  -> plot optimization_curve.png
```

The code is intentionally modular so the rough agent names can evolve into real
implementations:

- `AgentMonitor`: deep research and code analysis summaries
- `AgentIdeator`: structured idea generation
- `AgentScheduler`: idea selection
- `AgentSupervisor`: experiment recording and rollback decisions
- `AgentFix`: debugging guidance when an evaluation fails

## Install

```bash
cd laboratory
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Onboard

Auto onboard should be the default for a cloned paper repository. It asks the
Code Agent to infer the evaluation command, primary metric, conda environment,
setup commands, and protected paths from the repository itself:

```bash
autosota-lab onboard my-paper \
  --auto \
  --repo /absolute/path/to/paper/repo \
  --resource-root /absolute/path/to/laboratory/resources \
  --code-agent codex
```

Only pass `--eval-command` and metric overrides when debugging or pinning a
known command for a regression run. Those values should not be required for a
true first-pass zeroline flow.

```bash
autosota-lab onboard my-paper \
  --repo /absolute/path/to/paper/repo \
  --eval-command "python eval.py" \
  --primary-metric accuracy \
  --metric-direction higher
```

This writes:

```text
runs/my-paper/config.yaml
```

## Zeroline

`zeroline` runs auto onboard followed by resource discovery/acquisition,
environment planning, optional setup/validation, baseline execution, and a
readiness report. For a real first-pass run, do not provide repository-specific
evaluation knowledge:

```bash
autosota-lab zeroline my-paper \
  --repo /absolute/path/to/paper/repo \
  --repo-copy-root /absolute/path/to/laboratory/paper_repos_work \
  --resource-root /absolute/path/to/laboratory/resources \
  --code-agent codex \
  --environment-profile rtx5090-cu128 \
  --timeout-seconds 900 \
  --baseline-timeout-seconds 1800 \
  --refresh-resources \
  --use-acquired-resources \
  --skip-setup \
  --skip-validation \
  --fix-plan-only
```

`--refresh-resources` forces the resource copy/download step to rebuild the
local acquired copy under `resource_root`. `--use-acquired-resources` backs up
existing repository resource files/directories under
`.autosota_resource_backups/` and replaces the original paths with symlinks to
the acquired copies, so later evaluation commands read from `resource_root`.
Use `--repo-copy-root` when the source paper repository is read-only or owned by
another user; AutoSOTA will operate on the writable copy instead of the source.
Use `--environment-profile rtx5090-cu128` on RTX 5090 hosts to apply the
previously validated setup: Python 3.10, CUDA 12.8 PyTorch, and numpy/pillow
pins compatible with faiss and AutoGluon.

## Baseline

Use `baseline` for checkpoint recovery after onboarding, resource binding, and
environment setup are already done. It does not call a Code Agent and only runs
the configured evaluation command, captures stdout/stderr, parses metrics, and
writes `results/baseline_metrics.json`.

```bash
autosota-lab baseline my-paper \
  --repo /absolute/path/to/laboratory/paper_repos_work/paper-repo \
  --conda-env tsrag5090 \
  --baseline-timeout-seconds 1800
```

## Optimize

```bash
export OPENROUTER_API_KEY=sk-or-v1-...

autosota-lab optimize my-paper \
  --max-iterations 3 \
  --docker-image node:22-bookworm \
  --claude-command claude
```

By default the Docker command mounts the target repository read-write and mounts
the run directory at `/autosota_run`. The prototype does not install Claude Code
inside the image for you; use an image that already has `claude` available, or
override `--claude-command`.

## Outputs

```text
runs/<paper>/
  config.yaml
  latest -> run_YYYYMMDD_HHMMSS
  run_YYYYMMDD_HHMMSS/
    logs/
      master_prompt.md
      claude_phase0.log
      claude_phase1.log
      claude_phase3_iter_001.log 
    memory/
      research_report.md
      code_analysis.md
      idea_library.md
    results/
      scores.jsonl
      optimization_curve.png
```

