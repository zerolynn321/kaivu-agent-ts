from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.models import MetricDirection
    from autosota_lab.onboard import onboard
    from autosota_lab.optimize import Optimizer
else:
    from .models import MetricDirection
    from .onboard import onboard
    from .optimize import Optimizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autosota-lab")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Directory for AutoSOTA state and run outputs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    onboard_p = sub.add_parser("onboard", help="Create a paper config for a local repository.")
    onboard_p.add_argument("paper_name")
    onboard_p.add_argument("--repo", type=Path, required=True)
    onboard_p.add_argument("--paper-title", default="")
    onboard_p.add_argument("--eval-command", required=True)
    onboard_p.add_argument("--primary-metric", required=True)
    onboard_p.add_argument("--metric-direction", choices=[m.value for m in MetricDirection], default="higher")
    onboard_p.add_argument("--baseline-metric", type=float)
    onboard_p.add_argument("--docker-image", default="node:22-bookworm")
    onboard_p.add_argument("--max-iterations", type=int, default=5)
    onboard_p.add_argument("--max-ideas", type=int, default=8)

    opt_p = sub.add_parser("optimize", help="Run the prototype optimization pipeline.")
    opt_p.add_argument("paper_name")
    opt_p.add_argument("--repo", type=Path, help="Override repo_path from the paper config.")
    opt_p.add_argument(
        "--execution-backend",
        choices=["local", "docker"],
        help="Where to run Code Agent commands. Defaults to the paper config, usually local.",
    )
    opt_p.add_argument("--docker-image")
    opt_p.add_argument("--conda-env", help="Run local commands with `conda run -n <env>`.")
    opt_p.add_argument("--code-agent", choices=["claude", "codex"], default="claude")
    opt_p.add_argument("--code-agent-command")
    opt_p.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    opt_p.add_argument(
        "--research-model",
        default="openai/o4-mini-deep-research",
        help="Deep research model. This is separate from the Code Agent used for code changes.",
    )
    opt_p.add_argument(
        "--skip-onboard",
        action="store_true",
        help="Accepted for compatibility; optimize uses an existing paper config.",
    )
    opt_p.add_argument("--skip-research", action="store_true")
    opt_p.add_argument("--max-iterations", "--max-iter", dest="max_iterations", type=int)
    opt_p.add_argument("--max-ideas", type=int)
    opt_p.add_argument("--max-debug", dest="max_debug_attempts", type=int)
    opt_p.add_argument("--max-debug-min", dest="max_debug_minutes", type=int)
    opt_p.add_argument("--max-total-minutes", type=int)
    opt_p.add_argument("--dry-run", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = args.workspace.resolve()

    if args.cmd == "onboard":
        config = onboard(
            workspace=workspace,
            paper_name=args.paper_name,
            repo_path=args.repo,
            eval_command=args.eval_command,
            primary_metric=args.primary_metric,
            metric_direction=MetricDirection(args.metric_direction),
            paper_title=args.paper_title,
            docker_image=args.docker_image,
            baseline_metric=args.baseline_metric,
            max_iterations=args.max_iterations,
            max_ideas=args.max_ideas,
        )
        print(f"[onboard] wrote {workspace / '.autosota' / 'papers' / args.paper_name / 'config.yaml'}")
        print(config.model_dump_json(indent=2))
        return 0

    if args.cmd == "optimize":
        run_dir = Optimizer(
            workspace=workspace,
            paper_name=args.paper_name,
            repo_path=args.repo,
            execution_backend=args.execution_backend,
            docker_image=args.docker_image,
            conda_env=args.conda_env,
            code_agent=args.code_agent,
            code_agent_command=args.code_agent_command,
            code_agent_command_template=args.code_agent_command_template,
            research_model=args.research_model,
            skip_research=args.skip_research,
            dry_run=args.dry_run,
        ).run(
            max_iterations=args.max_iterations,
            max_ideas=args.max_ideas,
            max_debug_attempts=args.max_debug_attempts,
            max_debug_minutes=args.max_debug_minutes,
            max_total_minutes=args.max_total_minutes,
        )
        print(f"[optimize] run dir: {run_dir}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
