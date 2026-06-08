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

