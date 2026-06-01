from __future__ import annotations

import sys
import time
import shlex
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.agents import AgentInit, AgentResource
    from autosota_lab.code_agent import create_code_agent
    from autosota_lab.docker_runner import DockerRunner
    from autosota_lab.io import read_yaml, write_text, write_yaml
    from autosota_lab.local_runner import LocalRunner
    from autosota_lab.models import PaperConfig
    from autosota_lab.prompts import environment_planning_prompt, readiness_check_prompt, resource_discovery_prompt
    from autosota_lab.state import config_path, create_run_paths
else:
    from .agents import AgentInit, AgentResource
    from .code_agent import create_code_agent
    from .docker_runner import DockerRunner
    from .io import read_yaml, write_text, write_yaml
    from .local_runner import LocalRunner
    from .models import PaperConfig
    from .prompts import environment_planning_prompt, readiness_check_prompt, resource_discovery_prompt
    from .state import config_path, create_run_paths


class Preparer:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        repo_path: Path | None = None,
        execution_backend: str | None = None,
        docker_image: str | None = None,
        conda_env: str | None = None,
        paper_pdf_path: str | None = None,
        resource_root: str | None = None,
        code_agent: str = "claude",
        code_agent_command: str | None = None,
        code_agent_command_template: str | None = None,
        execute_setup: bool = False,
        execute_validation: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.config = PaperConfig.model_validate(read_yaml(config_path(self.workspace, paper_name)))
        if repo_path:
            self.config.repo_path = repo_path.expanduser().resolve()
        if execution_backend:
            self.config.execution_backend = execution_backend
        if docker_image:
            self.config.docker_image = docker_image
        if conda_env is not None:
            self.config.conda_env = conda_env
        if paper_pdf_path is not None:
            self.config.paper_pdf_path = paper_pdf_path
        if resource_root is not None:
            self.config.resource_root = resource_root
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template
        self.execute_setup = execute_setup
        self.execute_validation = execute_validation or execute_setup
        self.dry_run = dry_run

    def run(self, timeout_seconds: int | None = None, setup_timeout_seconds: int | None = None) -> Path:
        paths = create_run_paths(self.workspace, self.paper_name)
        write_yaml(paths.logs_dir / "effective_config.yaml", self.config)

        runner = self._create_runner(paths.run_dir)
        self._announce("prepare_start", f"run_dir={paths.run_dir}")
        self._announce(
            "execution_environment",
            f"backend={self.config.execution_backend}, repo={runner.repo_workdir}, output={runner.output_dir}",
        )
        code_agent = create_code_agent(
            runner,
            agent=self.code_agent,
            command=self.code_agent_command,
            command_template=self.code_agent_command_template,
        )
        resource_agent = AgentResource(code_agent)
        init_agent = AgentInit(code_agent)

        self._announce("resource_discovery", "Scanning repository for datasets, models, checkpoints, and path assumptions.")
        manifest = resource_agent.discover(
            resource_discovery_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.memory_dir / "resource_manifest.json",
            paths.logs_dir / f"{self.code_agent}_resource_discovery.log",
            timeout_seconds=timeout_seconds,
            dry_run=self.dry_run,
        )
        self._announce("resource_discovery", f"Finished with {len(manifest.resources)} resource(s).")

        self._announce("environment_planning", "Inferring dependency setup and cheap validation commands.")
        environment_plan = init_agent.plan_environment(
            environment_planning_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.memory_dir / "environment_plan.json",
            paths.logs_dir / f"{self.code_agent}_environment_planning.log",
            timeout_seconds=timeout_seconds,
            dry_run=self.dry_run,
        )
        self._announce("environment_planning", f"Finished with {len(environment_plan.install_commands)} install command(s).")

        if self.execute_setup:
            setup_commands = self.config.setup_commands or environment_plan.install_commands
            self._announce("environment_setup", f"Executing {len(setup_commands)} setup command(s).")
            setup_result = self._execute_commands(
                runner=runner,
                commands=setup_commands,
                script_rel="logs/setup_commands.sh",
                log_path=paths.logs_dir / "setup_commands.log",
                timeout_seconds=setup_timeout_seconds,
            )
            self._announce("environment_setup", f"Finished with exit={setup_result.returncode}.")

        if self.execute_validation and environment_plan.validation_commands:
            self._announce("environment_validation", f"Executing {len(environment_plan.validation_commands)} validation command(s).")
            validation_result = self._execute_commands(
                runner=runner,
                commands=environment_plan.validation_commands,
                script_rel="logs/validation_commands.sh",
                log_path=paths.logs_dir / "validation_commands.log",
                timeout_seconds=timeout_seconds,
            )
            self._announce("environment_validation", f"Finished with exit={validation_result.returncode}.")

        self._announce("readiness_check", "Summarizing whether the repository is ready for baseline evaluation.")
        report = init_agent.check_readiness(
            readiness_check_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.memory_dir / "prepare_report.json",
            paths.logs_dir / f"{self.code_agent}_readiness_check.log",
            resource_manifest=manifest,
            environment_plan=environment_plan,
            eval_command=self.config.eval_command,
            timeout_seconds=timeout_seconds,
            dry_run=self.dry_run,
        )
        self._announce("readiness_check", f"Finished with status={report.readiness_status}.")
        self._announce("prepare_complete", f"run_dir={paths.run_dir}")
        return paths.run_dir

    def _create_runner(self, run_dir: Path):
        if self.config.execution_backend == "docker":
            return DockerRunner(
                image=self.config.docker_image,
                repo_path=self.config.repo_path,
                run_dir=run_dir,
                env=self.config.env_vars,
            )
        return LocalRunner(
            repo_path=self.config.repo_path,
            run_dir=run_dir,
            env=self.config.env_vars,
            conda_env=self.config.conda_env,
            conda_executable=self.config.conda_executable,
            venv_path=self.config.venv_path,
        )

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota:prepare] {timestamp} | {stage} | {message}", flush=True)

    def _execute_commands(
        self,
        runner,
        commands: list[str],
        script_rel: str,
        log_path: Path,
        timeout_seconds: int | None = None,
    ):
        script_path = runner.run_dir / script_rel
        script = self._shell_script(commands)
        write_text(script_path, script)
        command = f"bash {shlex.quote(runner.prompt_path(script_rel))}"
        preview = runner.preview(command)
        if self.dry_run:
            write_text(log_path, f"$ {preview}\n\nDRY RUN\n\n{script}")
            return type("DryRunResult", (), {"returncode": 0})()
        proc = runner.run(command, timeout_seconds=timeout_seconds, stream_output=True)
        stderr_text = "\nSTDERR:\n" + proc.stderr if proc.stderr else ""
        write_text(log_path, f"$ {preview}\n\nSCRIPT:\n{script}\n\nSTDOUT:\n{proc.stdout}{stderr_text}")
        return proc

    def _shell_script(self, commands: list[str]) -> str:
        lines = [
            "#!/usr/bin/env bash",
            "set -eo pipefail",
            'if command -v conda >/dev/null 2>&1; then eval "$(conda shell.bash hook)"; fi',
        ]
        for command in commands:
            lines.append("")
            lines.append(f"echo '+ {command}'")
            lines.append(command)
        return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Prepare resources and environment plans for a paper repository.")
    parser.add_argument("paper_name", help="Paper name under <workspace>/.autosota/papers/.")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Directory for AutoSOTA state and run outputs. Defaults to the current working directory.",
    )
    parser.add_argument("--repo", type=Path, help="Override repo_path from the paper config.")
    parser.add_argument(
        "--execution-backend",
        choices=["local", "docker"],
        help="Where to run Code Agent commands. Defaults to the paper config, usually local.",
    )
    parser.add_argument("--docker-image", help="Override docker_image from the paper config.")
    parser.add_argument("--conda-env", help="Run local commands with `conda run -n <env>`.")
    parser.add_argument("--paper-pdf", default=None, help="Optional local paper PDF path for context.")
    parser.add_argument("--resource-root", default=None, help="Optional root directory for datasets/models/checkpoints.")
    parser.add_argument("--code-agent", choices=["claude", "codex"], default="claude")
    parser.add_argument("--code-agent-command", help="Code Agent executable or command prefix.")
    parser.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    parser.add_argument("--timeout-seconds", type=int, help="Per-stage Code Agent timeout.")
    parser.add_argument("--setup-timeout-seconds", type=int, help="Timeout for setup command execution.")
    parser.add_argument("--execute-setup", action="store_true", help="Execute setup commands after environment planning.")
    parser.add_argument(
        "--execute-validation",
        action="store_true",
        help="Execute validation commands after environment planning. Implied by --execute-setup.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and preview commands only.")
    args = parser.parse_args(argv)

    run_dir = Preparer(
        workspace=args.workspace,
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
        dry_run=args.dry_run,
    ).run(timeout_seconds=args.timeout_seconds, setup_timeout_seconds=args.setup_timeout_seconds)
    print(f"[prepare] run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
