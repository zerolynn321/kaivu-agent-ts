from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.models import MetricDirection
    from autosota_lab.onboard import AutoOnboarder, onboard
    from autosota_lab.optimize import Optimizer
    from autosota_lab.pipeline import ZerolinePipeline
    from autosota_lab.prepare import Preparer
else:
    from .models import MetricDirection
    from .onboard import AutoOnboarder, onboard
    from .optimize import Optimizer
    from .pipeline import ZerolinePipeline
    from .prepare import Preparer


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
    onboard_p.add_argument("--auto", action="store_true", help="Ask a Code Agent to infer eval command, metric, and setup hints.")
    onboard_p.add_argument("--paper-title", default="")
    onboard_p.add_argument("--paper-pdf", default="")
    onboard_p.add_argument("--resource-root", default="")
    onboard_p.add_argument("--eval-command")
    onboard_p.add_argument("--primary-metric")
    onboard_p.add_argument("--metric-direction", choices=[m.value for m in MetricDirection])
    onboard_p.add_argument("--baseline-metric", type=float)
    onboard_p.add_argument("--docker-image", default="node:22-bookworm")
    onboard_p.add_argument("--max-iterations", type=int, default=5)
    onboard_p.add_argument("--max-ideas", type=int, default=8)
    onboard_p.add_argument("--code-agent", choices=["claude", "codex"], default="codex")
    onboard_p.add_argument("--code-agent-command")
    onboard_p.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    onboard_p.add_argument("--timeout-seconds", type=int, help="Code Agent timeout for --auto onboard.")
    onboard_p.add_argument("--dry-run", action="store_true")
    onboard_p.add_argument(
        "--setup-command",
        action="append",
        default=[],
        help="Optional setup command to record in config. Can be passed multiple times.",
    )
    onboard_p.add_argument(
        "--pre-eval-command",
        action="append",
        default=[],
        help="Optional command to run before evaluation. Can be passed multiple times.",
    )

    prep_p = sub.add_parser("prepare", help="Discover resources and plan environment setup for a paper repo.")
    prep_p.add_argument("paper_name")
    prep_p.add_argument("--repo", type=Path, help="Override repo_path from the paper config.")
    prep_p.add_argument(
        "--execution-backend",
        choices=["local", "docker"],
        help="Where to run Code Agent commands. Defaults to the paper config, usually local.",
    )
    prep_p.add_argument("--docker-image")
    prep_p.add_argument("--conda-env", help="Run local commands with `conda run -n <env>`.")
    prep_p.add_argument("--paper-pdf", default=None, help="Optional local paper PDF path for context.")
    prep_p.add_argument("--resource-root", default=None, help="Optional root directory for datasets/models/checkpoints.")
    prep_p.add_argument("--skip-resource-acquisition", action="store_true", help="Skip copying discovered resources into resource_root.")
    prep_p.add_argument("--code-agent", choices=["claude", "codex"], default="claude")
    prep_p.add_argument("--code-agent-command")
    prep_p.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    prep_p.add_argument("--timeout-seconds", type=int, help="Per-stage Code Agent timeout.")
    prep_p.add_argument("--setup-timeout-seconds", type=int, help="Timeout for setup command execution.")
    prep_p.add_argument("--fix-timeout-seconds", type=int, help="Timeout for each AgentFix planning or command execution attempt.")
    prep_p.add_argument("--baseline-timeout-seconds", type=int, help="Timeout for the optional baseline check.")
    prep_p.add_argument("--execute-setup", action="store_true", help="Execute setup commands after environment planning.")
    prep_p.add_argument(
        "--execute-validation",
        action="store_true",
        help="Execute validation commands after environment planning. Implied by --execute-setup.",
    )
    prep_p.add_argument("--execute-baseline", action="store_true", help="Run the configured eval command once and capture current-run baseline metrics.")
    prep_p.add_argument(
        "--auto-fix",
        "--auto-fix-setup",
        dest="auto_fix",
        action="store_true",
        help="Let AgentFix propose and execute safe repair commands after failed setup, validation, or baseline stages.",
    )
    prep_p.add_argument("--fix-plan-only", action="store_true", help="Ask AgentFix for repair plans but do not execute fix commands.")
    prep_p.add_argument("--allow-risky-fix", action="store_true", help="Allow high-risk dependency repair commands such as PyTorch upgrades.")
    prep_p.add_argument("--max-fix-attempts", type=int, default=1, help="Maximum AgentFix attempts per failed execution stage.")
    prep_p.add_argument("--dry-run", action="store_true")

    zero_p = sub.add_parser("zeroline", help="Run auto onboard, resource acquisition, environment setup, validation, and baseline.")
    zero_p.add_argument("paper_name")
    zero_p.add_argument("--repo", type=Path, required=True)
    zero_p.add_argument("--paper-title", default="")
    zero_p.add_argument("--paper-pdf", default="")
    zero_p.add_argument("--resource-root", required=True, help="Root directory where discovered resources are copied/downloaded.")
    zero_p.add_argument("--eval-command", help="Optional override if auto onboard should not infer it.")
    zero_p.add_argument("--primary-metric", help="Optional override if auto onboard should not infer it.")
    zero_p.add_argument("--metric-direction", choices=[m.value for m in MetricDirection])
    zero_p.add_argument("--baseline-metric", type=float)
    zero_p.add_argument("--execution-backend", choices=["local", "docker"])
    zero_p.add_argument("--docker-image", default="node:22-bookworm")
    zero_p.add_argument("--code-agent", choices=["claude", "codex"], default="codex")
    zero_p.add_argument("--code-agent-command")
    zero_p.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    zero_p.add_argument("--timeout-seconds", type=int, help="Per-agent stage timeout.")
    zero_p.add_argument("--setup-timeout-seconds", type=int, help="Timeout for environment setup command execution.")
    zero_p.add_argument("--fix-timeout-seconds", type=int, help="Timeout for each AgentFix planning or command execution attempt.")
    zero_p.add_argument("--baseline-timeout-seconds", type=int, help="Timeout for zeroline baseline execution.")
    zero_p.add_argument("--max-iterations", type=int, default=5)
    zero_p.add_argument("--max-ideas", type=int, default=8)
    zero_p.add_argument("--setup-command", action="append", default=[], help="Optional setup command override. Can be passed multiple times.")
    zero_p.add_argument("--pre-eval-command", action="append", default=[], help="Optional pre-eval command. Can be passed multiple times.")
    zero_p.add_argument("--no-auto-fix", action="store_true", help="Disable AgentFix retries during setup, validation, and baseline.")
    zero_p.add_argument("--fix-plan-only", action="store_true", help="Ask AgentFix for repair plans but do not execute fix commands.")
    zero_p.add_argument("--allow-risky-fix", action="store_true", help="Allow high-risk dependency repair commands such as PyTorch upgrades.")
    zero_p.add_argument("--max-fix-attempts", type=int, default=2, help="Maximum AgentFix attempts per failed execution stage.")
    zero_p.add_argument("--skip-setup", action="store_true", help="Skip executing environment setup commands.")
    zero_p.add_argument("--skip-validation", action="store_true", help="Skip executing validation commands.")
    zero_p.add_argument("--skip-baseline", action="store_true", help="Skip zeroline baseline execution.")
    zero_p.add_argument("--skip-resource-acquisition", action="store_true", help="Skip copying/downloading resources into resource_root.")
    zero_p.add_argument("--dry-run", action="store_true")

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
        if args.auto:
            config = AutoOnboarder(
                workspace=workspace,
                paper_name=args.paper_name,
                repo_path=args.repo,
                paper_pdf_path=args.paper_pdf,
                resource_root=args.resource_root,
                docker_image=args.docker_image,
                code_agent=args.code_agent,
                code_agent_command=args.code_agent_command,
                code_agent_command_template=args.code_agent_command_template,
                dry_run=args.dry_run,
            ).run(
                timeout_seconds=args.timeout_seconds,
                paper_title=args.paper_title,
                eval_command=args.eval_command or "",
                primary_metric=args.primary_metric or "",
                metric_direction=MetricDirection(args.metric_direction) if args.metric_direction else None,
                baseline_metric=args.baseline_metric,
                max_iterations=args.max_iterations,
                max_ideas=args.max_ideas,
                setup_commands=args.setup_command,
                pre_eval_commands=args.pre_eval_command,
            )
            print(f"[onboard] wrote {workspace / '.autosota' / 'papers' / args.paper_name / 'config.yaml'}")
            print(config.model_dump_json(indent=2))
            return 0

        if not args.eval_command or not args.primary_metric:
            raise SystemExit("manual onboard requires --eval-command and --primary-metric; use --auto to let a Code Agent infer them")
        config = onboard(
            workspace=workspace,
            paper_name=args.paper_name,
            repo_path=args.repo,
            eval_command=args.eval_command,
            primary_metric=args.primary_metric,
            metric_direction=MetricDirection(args.metric_direction or "higher"),
            paper_title=args.paper_title,
            paper_pdf_path=args.paper_pdf,
            resource_root=args.resource_root,
            docker_image=args.docker_image,
            baseline_metric=args.baseline_metric,
            max_iterations=args.max_iterations,
            max_ideas=args.max_ideas,
            setup_commands=args.setup_command,
            pre_eval_commands=args.pre_eval_command,
        )
        print(f"[onboard] wrote {workspace / '.autosota' / 'papers' / args.paper_name / 'config.yaml'}")
        print(config.model_dump_json(indent=2))
        return 0

    if args.cmd == "prepare":
        run_dir = Preparer(
            workspace=workspace,
            paper_name=args.paper_name,
            repo_path=args.repo,
            execution_backend=args.execution_backend,
            docker_image=args.docker_image,
            conda_env=args.conda_env,
            paper_pdf_path=args.paper_pdf,
            resource_root=args.resource_root,
            code_agent=args.code_agent,
            code_agent_command=args.code_agent_command,
            code_agent_command_template=args.code_agent_command_template,
            execute_setup=args.execute_setup,
            execute_validation=args.execute_validation,
            execute_baseline=args.execute_baseline,
            acquire_resources=not args.skip_resource_acquisition,
            auto_fix=args.auto_fix,
            fix_plan_only=args.fix_plan_only,
            allow_risky_fix=args.allow_risky_fix,
            max_fix_attempts=args.max_fix_attempts,
            dry_run=args.dry_run,
        ).run(
            timeout_seconds=args.timeout_seconds,
            setup_timeout_seconds=args.setup_timeout_seconds,
            fix_timeout_seconds=args.fix_timeout_seconds,
            baseline_timeout_seconds=args.baseline_timeout_seconds,
        )
        print(f"[prepare] run dir: {run_dir}")
        return 0

    if args.cmd == "zeroline":
        run_dir = ZerolinePipeline(
            workspace=workspace,
            paper_name=args.paper_name,
            repo_path=args.repo,
            paper_pdf_path=args.paper_pdf,
            resource_root=args.resource_root,
            execution_backend=args.execution_backend,
            docker_image=args.docker_image,
            code_agent=args.code_agent,
            code_agent_command=args.code_agent_command,
            code_agent_command_template=args.code_agent_command_template,
            dry_run=args.dry_run,
        ).run(
            timeout_seconds=args.timeout_seconds,
            setup_timeout_seconds=args.setup_timeout_seconds,
            fix_timeout_seconds=args.fix_timeout_seconds,
            baseline_timeout_seconds=args.baseline_timeout_seconds,
            paper_title=args.paper_title,
            eval_command=args.eval_command or "",
            primary_metric=args.primary_metric or "",
            metric_direction=MetricDirection(args.metric_direction) if args.metric_direction else None,
            baseline_metric=args.baseline_metric,
            max_iterations=args.max_iterations,
            max_ideas=args.max_ideas,
            setup_commands=args.setup_command,
            pre_eval_commands=args.pre_eval_command,
            auto_fix=not args.no_auto_fix,
            fix_plan_only=args.fix_plan_only,
            allow_risky_fix=args.allow_risky_fix,
            max_fix_attempts=args.max_fix_attempts,
            skip_setup=args.skip_setup,
            skip_validation=args.skip_validation,
            skip_baseline=args.skip_baseline,
            skip_resource_acquisition=args.skip_resource_acquisition,
        )
        print(f"[zeroline] run dir: {run_dir}")
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
