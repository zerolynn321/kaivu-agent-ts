from __future__ import annotations

import sys
import time
import shlex
import re
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.agents import AgentFix, AgentInit, AgentResource
    from autosota_lab.code_agent import create_code_agent
    from autosota_lab.docker_runner import DockerRunner
    from autosota_lab.io import read_yaml, write_text, write_yaml
    from autosota_lab.local_runner import LocalRunner
    from autosota_lab.models import BaselineRunSummary, CommandExecutionSummary, EnvironmentFixPlan, FixAttemptSummary, FixRunSummary, PaperConfig, PrepareExecutionStatus, ResourceAcquisitionItem, ResourceAcquisitionReport, ResourceManifest, ResourceStatus
    from autosota_lab.prompts import environment_planning_prompt, readiness_check_prompt, resource_discovery_prompt
    from autosota_lab.state import config_path, create_run_paths
else:
    from .agents import AgentFix, AgentInit, AgentResource
    from .code_agent import create_code_agent
    from .docker_runner import DockerRunner
    from .io import read_yaml, write_text, write_yaml
    from .local_runner import LocalRunner
    from .models import BaselineRunSummary, CommandExecutionSummary, EnvironmentFixPlan, FixAttemptSummary, FixRunSummary, PaperConfig, PrepareExecutionStatus, ResourceAcquisitionItem, ResourceAcquisitionReport, ResourceManifest, ResourceStatus
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
        execute_baseline: bool = False,
        acquire_resources: bool = True,
        auto_fix: bool = False,
        max_fix_attempts: int = 1,
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
        self.execute_baseline = execute_baseline
        self.acquire_resources = acquire_resources
        self.auto_fix = auto_fix
        self.max_fix_attempts = max(0, max_fix_attempts)
        self.dry_run = dry_run

    def run(
        self,
        timeout_seconds: int | None = None,
        setup_timeout_seconds: int | None = None,
        fix_timeout_seconds: int | None = None,
        baseline_timeout_seconds: int | None = None,
    ) -> Path:
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
        fix_agent = AgentFix(code_agent)
        execution_status = PrepareExecutionStatus()

        self._announce("resource_discovery", "Scanning repository for datasets, models, checkpoints, and path assumptions.")
        manifest = resource_agent.discover(
            resource_discovery_prompt(self.config, runner.repo_workdir, runner.output_dir),
            paths.memory_dir / "resource_manifest.json",
            paths.logs_dir / f"{self.code_agent}_resource_discovery.log",
            timeout_seconds=timeout_seconds,
            dry_run=self.dry_run,
        )
        self._announce("resource_discovery", f"Finished with {len(manifest.resources)} resource(s).")

        if self.acquire_resources and self.config.resource_root:
            self._announce("resource_acquisition", f"Copying discovered local resources into {self.config.resource_root}.")
            acquisition_report = self._acquire_resources(manifest, paths)
            write_text(paths.memory_dir / "resource_acquisition_report.json", acquisition_report.model_dump_json(indent=2))
            write_text(paths.memory_dir / "resource_manifest.json", manifest.model_dump_json(indent=2))
            acquired = [item for item in acquisition_report.items if item.status == ResourceStatus.available]
            failed = [item for item in acquisition_report.items if item.status == ResourceStatus.failed]
            self._announce("resource_acquisition", f"Finished with available={len(acquired)}, failed={len(failed)}.")
        elif self.acquire_resources:
            self._announce("resource_acquisition", "Skipped because resource_root is not configured.")

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
            setup_result = self._execute_with_agent_fix(
                runner=runner,
                fix_agent=fix_agent,
                paths=paths,
                stage="setup",
                commands=setup_commands,
                script_rel="logs/setup_commands.sh",
                log_path=paths.logs_dir / "setup_commands.log",
                timeout_seconds=setup_timeout_seconds,
                fix_timeout_seconds=fix_timeout_seconds or timeout_seconds,
                idempotent=True,
            )
            execution_status.setup = self._command_summary("setup", setup_commands, setup_result, paths.logs_dir / "setup_commands.log")
            self._announce("environment_setup", f"Finished with exit={setup_result.returncode}.")

        if self.execute_validation and environment_plan.validation_commands:
            validation_conda_env = self.config.conda_env or self._infer_conda_env(
                self.config.setup_commands or environment_plan.install_commands
            )
            self._announce("environment_validation", f"Executing {len(environment_plan.validation_commands)} validation command(s).")
            validation_result = self._execute_with_agent_fix(
                runner=runner,
                fix_agent=fix_agent,
                paths=paths,
                stage="validation",
                commands=environment_plan.validation_commands,
                script_rel="logs/validation_commands.sh",
                log_path=paths.logs_dir / "validation_commands.log",
                timeout_seconds=timeout_seconds,
                fix_timeout_seconds=fix_timeout_seconds or timeout_seconds,
                conda_env=validation_conda_env,
            )
            execution_status.validation = self._command_summary(
                "validation",
                environment_plan.validation_commands,
                validation_result,
                paths.logs_dir / "validation_commands.log",
            )
            self._announce("environment_validation", f"Finished with exit={validation_result.returncode}.")

        if self.execute_baseline:
            self._announce("baseline_check", "Executing the configured baseline command and capturing current-run metrics.")
            execution_status.baseline = self._execute_baseline(
                runner=runner,
                fix_agent=fix_agent,
                paths=paths,
                timeout_seconds=baseline_timeout_seconds or self.config.eval_timeout_seconds,
                fix_timeout_seconds=fix_timeout_seconds or timeout_seconds,
            )
            self._announce(
                "baseline_check",
                f"Finished with status={execution_status.baseline.status}, exit={execution_status.baseline.returncode}.",
            )

        execution_status.readiness_status = self._execution_readiness(execution_status)
        execution_status.notes = self._execution_notes(execution_status)
        write_text(paths.memory_dir / "setup_status.json", execution_status.model_dump_json(indent=2))

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
        if execution_status.readiness_status == "blocked" and report.readiness_status != "blocked":
            report.readiness_status = "blocked"
            report.next_steps = [
                "Review memory/setup_status.json and command logs before running optimize.",
                *report.next_steps,
            ]
            report.notes = f"{report.notes}\nExecution status forced readiness to blocked.".strip()
            write_text(paths.memory_dir / "prepare_report.json", report.model_dump_json(indent=2))
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
            conda_executable=self.config.conda_executable,
            venv_path=self.config.venv_path,
        )

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota:prepare] {timestamp} | {stage} | {message}", flush=True)

    def _acquire_resources(self, manifest: ResourceManifest, paths) -> ResourceAcquisitionReport:
        resource_root = Path(self.config.resource_root).expanduser()
        store_root = resource_root / self.config.paper_name
        report = ResourceAcquisitionReport(resource_root=str(store_root))
        if self.dry_run:
            report.notes = "Dry run: resource acquisition was planned but not executed."
            for resource in manifest.resources:
                report.items.append(
                    ResourceAcquisitionItem(
                        name=resource.name,
                        type=resource.type,
                        source=resource.source_url or resource.local_path,
                        repo_path=resource.local_path,
                        action="skipped",
                        status=ResourceStatus.discovered,
                        notes="dry run",
                    )
                )
            return report

        store_root.mkdir(parents=True, exist_ok=True)
        for resource in manifest.resources:
            item = self._acquire_one_resource(resource, store_root)
            report.items.append(item)
        return report

    def _acquire_one_resource(self, resource, store_root: Path) -> ResourceAcquisitionItem:
        repo_resource_path = self._repo_resource_path(resource.local_path)
        acquired_path = store_root / self._resource_destination_rel(resource)
        item = ResourceAcquisitionItem(
            name=resource.name,
            type=resource.type,
            source=resource.source_url or str(repo_resource_path),
            repo_path=str(repo_resource_path) if repo_resource_path is not None else resource.local_path,
            acquired_path=str(acquired_path),
        )
        try:
            source_path = self._resource_source_path(resource, repo_resource_path)
            if acquired_path.exists():
                item.action = "reused"
                item.status = ResourceStatus.available
                item.notes = "Existing acquired resource reused."
            elif source_path is not None and source_path.exists():
                self._copy_resource(source_path, acquired_path)
                item.action = "copied"
                item.status = ResourceStatus.available
                item.notes = f"Copied from {source_path}."
            elif resource.source_url:
                self._download_resource(resource.source_url, acquired_path)
                item.action = "downloaded"
                item.status = ResourceStatus.available
                item.notes = f"Downloaded from {resource.source_url}."
            else:
                item.action = "skipped"
                item.status = ResourceStatus.missing
                item.notes = "No existing local path or source_url was available."

            if item.status == ResourceStatus.available:
                resource.acquired_path = str(acquired_path)
                resource.status = ResourceStatus.available
                resource.notes = self._append_note(resource.notes, item.notes)
                link_note = self._bind_repo_resource(repo_resource_path, acquired_path)
                if link_note:
                    item.action = "linked" if item.action == "reused" else item.action
                    item.notes = self._append_note(item.notes, link_note)
                    resource.notes = self._append_note(resource.notes, link_note)
        except Exception as exc:
            item.action = "failed"
            item.status = ResourceStatus.failed
            item.notes = str(exc)
            resource.status = ResourceStatus.failed
            resource.notes = self._append_note(resource.notes, f"Acquisition failed: {exc}")
        return item

    def _repo_resource_path(self, local_path: str) -> Path | None:
        if not local_path:
            return None
        path = Path(local_path).expanduser()
        if path.is_absolute():
            return path
        return self.config.repo_path / path

    def _resource_source_path(self, resource, repo_resource_path: Path | None) -> Path | None:
        if repo_resource_path is None:
            return None
        if repo_resource_path.exists():
            return repo_resource_path.resolve()
        if repo_resource_path.is_symlink():
            return repo_resource_path.resolve()
        return None

    def _resource_destination_rel(self, resource) -> Path:
        raw = resource.local_path or resource.name or resource.type.value
        path = Path(raw)
        if path.is_absolute():
            parts = [part for part in path.parts if part not in (path.anchor, "/", "\\")]
            path = Path(*parts) if parts else Path(self._safe_resource_name(resource.name or resource.type.value))
        safe_parts = [self._safe_resource_name(part) for part in path.parts if part not in ("", ".", "..")]
        if not safe_parts:
            safe_parts = [self._safe_resource_name(resource.name or resource.type.value)]
        return Path(*safe_parts)

    def _safe_resource_name(self, value: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
        return safe.strip("._") or "resource"

    def _copy_resource(self, source_path: Path, acquired_path: Path) -> None:
        acquired_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.is_dir():
            shutil.copytree(source_path, acquired_path, symlinks=False)
        else:
            shutil.copy2(source_path, acquired_path)

    def _download_resource(self, source_url: str, acquired_path: Path) -> None:
        acquired_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(source_url, acquired_path)

    def _bind_repo_resource(self, repo_resource_path: Path | None, acquired_path: Path) -> str:
        if repo_resource_path is None:
            return ""
        if repo_resource_path.is_symlink():
            repo_resource_path.unlink()
            repo_resource_path.symlink_to(acquired_path, target_is_directory=acquired_path.is_dir())
            return f"Replaced repository symlink with acquired resource link: {repo_resource_path} -> {acquired_path}."
        if not repo_resource_path.exists():
            repo_resource_path.parent.mkdir(parents=True, exist_ok=True)
            repo_resource_path.symlink_to(acquired_path, target_is_directory=acquired_path.is_dir())
            return f"Created repository resource link: {repo_resource_path} -> {acquired_path}."
        return "Repository path already exists as a regular file/directory; acquired copy recorded but repo path was not replaced."

    def _append_note(self, current: str, note: str) -> str:
        if not current:
            return note
        if not note:
            return current
        return f"{current}\n{note}"

    def _execute_commands(
        self,
        runner,
        commands: list[str],
        script_rel: str,
        log_path: Path,
        timeout_seconds: int | None = None,
        conda_env: str = "",
        env_vars: dict[str, str] | None = None,
        idempotent: bool = False,
    ):
        script_path = runner.run_dir / script_rel
        script = self._shell_script(commands, conda_env=conda_env, env_vars=env_vars or {}, idempotent=idempotent)
        write_text(script_path, script)
        command = f"bash {shlex.quote(runner.prompt_path(script_rel))}"
        preview = runner.preview(command)
        if self.dry_run:
            write_text(log_path, f"$ {preview}\n\nDRY RUN\n\n{script}")
            return type("DryRunResult", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        proc = runner.run(command, timeout_seconds=timeout_seconds, stream_output=True)
        stderr_text = "\nSTDERR:\n" + proc.stderr if proc.stderr else ""
        write_text(log_path, f"$ {preview}\n\nSCRIPT:\n{script}\n\nSTDOUT:\n{proc.stdout}{stderr_text}")
        return proc

    def _execute_with_agent_fix(
        self,
        runner,
        fix_agent: AgentFix,
        paths,
        stage: str,
        commands: list[str],
        script_rel: str,
        log_path: Path,
        timeout_seconds: int | None = None,
        fix_timeout_seconds: int | None = None,
        conda_env: str = "",
        env_vars: dict[str, str] | None = None,
        idempotent: bool = False,
    ):
        summary = FixRunSummary(stage=stage, max_attempts=self.max_fix_attempts)
        result = self._execute_commands(
            runner=runner,
            commands=commands,
            script_rel=script_rel,
            log_path=log_path,
            timeout_seconds=timeout_seconds,
            conda_env=conda_env,
            env_vars=env_vars,
            idempotent=idempotent,
        )
        if result.returncode == 0:
            summary.resolved = True
            summary.stopped_reason = "initial command succeeded"
            write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
            self._attach_fix_summary(result, summary)
            return result
        if not self.auto_fix or self.max_fix_attempts <= 0:
            summary.stopped_reason = "agent fix disabled" if not self.auto_fix else "max fix attempts is zero"
            write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
            self._attach_fix_summary(result, summary)
            return result

        previous_fix_plans: list[EnvironmentFixPlan] = []
        previous_attempts: list[FixAttemptSummary] = []
        last_result = result
        for attempt in range(1, self.max_fix_attempts + 1):
            self._announce("agent_fix", f"stage={stage}, attempt={attempt}")
            plan_path = paths.memory_dir / f"environment_fix_plan_{stage}_attempt_{attempt:03d}.json"
            fix_plan = fix_agent.plan_environment_fix(
                config=self.config,
                repo_dir=runner.repo_workdir,
                output_dir=runner.output_dir,
                failed_stage=stage,
                failed_commands=commands,
                stdout=last_result.stdout,
                stderr=last_result.stderr,
                output_path=plan_path,
                log_path=paths.logs_dir / f"{self.code_agent}_agent_fix_{stage}_attempt_{attempt:03d}.log",
                timeout_seconds=fix_timeout_seconds,
                dry_run=self.dry_run,
                previous_fix_plans=previous_fix_plans,
                previous_attempts=previous_attempts,
            )
            previous_fix_plans.append(fix_plan)
            unsafe_reason = self._unsafe_fix_reason(fix_plan.fix_commands)
            attempt_summary = FixAttemptSummary(
                attempt=attempt,
                failed_stage=stage,
                failure_returncode=int(last_result.returncode),
                plan_path=str(plan_path),
                fix_commands=fix_plan.fix_commands,
                rejected_reason=unsafe_reason,
            )
            if not fix_plan.safe_to_execute or not fix_plan.fix_commands or unsafe_reason:
                self._announce("agent_fix", f"stage={stage}, attempt={attempt} did not produce safe commands.")
                attempt_summary.rejected_reason = unsafe_reason or (
                    "safe_to_execute=false" if not fix_plan.safe_to_execute else "no fix commands"
                )
                attempt_summary.notes = fix_plan.notes or fix_plan.diagnosis
                previous_attempts.append(attempt_summary)
                summary.attempts = previous_attempts
                summary.stopped_reason = attempt_summary.rejected_reason
                write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
                self._attach_fix_summary(last_result, summary)
                if unsafe_reason:
                    write_text(
                        paths.logs_dir / f"fix_{stage}_attempt_{attempt:03d}_rejected.log",
                        f"Rejected AgentFix commands: {unsafe_reason}\n\n{fix_plan.model_dump_json(indent=2)}",
                    )
                break

            fix_result = self._execute_commands(
                runner=runner,
                commands=fix_plan.fix_commands,
                script_rel=f"logs/fix_{stage}_attempt_{attempt:03d}.sh",
                log_path=paths.logs_dir / f"fix_{stage}_attempt_{attempt:03d}.log",
                timeout_seconds=fix_timeout_seconds,
                conda_env=conda_env,
                env_vars={**(env_vars or {}), **fix_plan.env_vars},
                idempotent=True,
            )
            attempt_summary.fix_returncode = int(fix_result.returncode)
            if fix_result.returncode != 0:
                attempt_summary.notes = "fix commands failed; next attempt will receive this failure output"
                previous_attempts.append(attempt_summary)
                summary.attempts = previous_attempts
                write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
                self._attach_fix_summary(fix_result, summary)
                last_result = fix_result
                continue

            retry_commands = fix_plan.validation_commands if stage == "validation" and fix_plan.validation_commands else commands
            last_result = self._execute_commands(
                runner=runner,
                commands=retry_commands,
                script_rel=f"logs/{stage}_retry_attempt_{attempt:03d}.sh",
                log_path=paths.logs_dir / f"{stage}_retry_attempt_{attempt:03d}.log",
                timeout_seconds=timeout_seconds,
                conda_env=conda_env,
                env_vars={**(env_vars or {}), **fix_plan.env_vars},
                idempotent=False,
            )
            attempt_summary.retry_commands = retry_commands
            attempt_summary.retry_returncode = int(last_result.returncode)
            if last_result.returncode == 0:
                attempt_summary.notes = "retry succeeded"
                previous_attempts.append(attempt_summary)
                summary.attempts = previous_attempts
                summary.resolved = True
                summary.stopped_reason = f"resolved after attempt {attempt}"
                write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
                self._attach_fix_summary(last_result, summary)
                return last_result
            attempt_summary.notes = "retry failed; next attempt will receive retry output"
            previous_attempts.append(attempt_summary)
            summary.attempts = previous_attempts
            write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
        if not summary.stopped_reason:
            summary.stopped_reason = f"reached max_fix_attempts={self.max_fix_attempts}"
        summary.resolved = False
        summary.attempts = previous_attempts
        write_text(paths.memory_dir / f"agent_fix_summary_{stage}.json", summary.model_dump_json(indent=2))
        self._attach_fix_summary(last_result, summary)
        return last_result

    def _attach_fix_summary(self, result, summary: FixRunSummary) -> None:
        try:
            result.autosota_fix_summary = summary
        except Exception:
            pass

    def _shell_script(
        self,
        commands: list[str],
        conda_env: str = "",
        env_vars: dict[str, str] | None = None,
        idempotent: bool = False,
    ) -> str:
        lines = [
            "#!/usr/bin/env bash",
            "set -eo pipefail",
            'if command -v conda >/dev/null 2>&1; then eval "$(conda shell.bash hook)"; fi',
        ]
        for key, value in (env_vars or {}).items():
            lines.append(f"export {shlex.quote(key)}={shlex.quote(value)}")
        if conda_env:
            lines.extend(["", f"conda activate {shlex.quote(conda_env)}"])
        for command in commands:
            lines.append("")
            lines.append(f"echo '+ {command}'")
            lines.append(self._idempotent_command(command) if idempotent else command)
        return "\n".join(lines) + "\n"

    def _idempotent_command(self, command: str) -> str:
        conda_create = re.search(r"\bconda\s+create\b.*(?:-n|--name)\s+([A-Za-z0-9_.-]+)", command)
        if conda_create:
            env_name = conda_create.group(1)
            quoted_env = shlex.quote(env_name)
            return (
                f"if conda env list | awk '{{print $1}}' | grep -qx {quoted_env}; then "
                f"echo 'autosota: conda env {env_name} already exists; skipping create'; "
                f"else {command}; fi"
            )
        return command

    def _unsafe_fix_reason(self, commands: list[str]) -> str:
        banned_patterns = [
            r"\bgit\s+(reset|checkout|clean|commit|tag)\b",
            r"\brm\s+-[^\n;]*[rf]",
            r"\bdel\s+",
            r"\brmdir\s+",
            r"\bformat\s+",
            r"\bmkfs\b",
        ]
        protected_terms = [
            "eval.py",
            "evaluation",
            "metric",
            "metrics",
            "test.csv",
            "train.csv",
            "label",
            "labels",
        ]
        for command in commands:
            lowered = command.lower()
            for pattern in banned_patterns:
                if re.search(pattern, lowered):
                    return f"banned command pattern {pattern!r} in {command!r}"
            if re.search(r"\b(sed|perl|python|python3)\b.*\b(-i|write_text|open\()", lowered):
                for term in protected_terms:
                    if term in lowered:
                        return f"possible protected file edit involving {term!r} in {command!r}"
        return ""

    def _infer_conda_env(self, commands: list[str]) -> str:
        for command in commands:
            match = re.search(r"\bconda\s+activate\s+([A-Za-z0-9_.-]+)", command)
            if match:
                return match.group(1)
        for command in commands:
            match = re.search(r"\bconda\s+create\b.*(?:-n|--name)\s+([A-Za-z0-9_.-]+)", command)
            if match:
                return match.group(1)
        return ""

    def _execute_baseline(
        self,
        runner,
        fix_agent: AgentFix,
        paths,
        timeout_seconds: int | None = None,
        fix_timeout_seconds: int | None = None,
    ) -> BaselineRunSummary:
        started_at = datetime.now(timezone.utc).isoformat()
        commands = [
            *self.config.pre_eval_commands,
            self.config.eval_command,
        ]
        log_path = paths.logs_dir / "baseline_eval.log"
        result = self._execute_with_agent_fix(
            runner=runner,
            fix_agent=fix_agent,
            paths=paths,
            stage="baseline",
            commands=commands,
            script_rel="logs/baseline_eval.sh",
            log_path=log_path,
            timeout_seconds=timeout_seconds,
            fix_timeout_seconds=fix_timeout_seconds,
            conda_env=self.config.conda_env,
            env_vars={
                "AUTOSOTA_RUN_DIR": runner.output_dir,
                "AUTOSOTA_OUTPUT_DIR": runner.output_dir,
                "AUTOSOTA_RESULTS_DIR": str(paths.results_dir),
                "OUTPUT_DIR": runner.output_dir,
                "RESULTS_DIR": str(paths.results_dir),
            },
        )
        finished_at = datetime.now(timezone.utc).isoformat()
        metrics = self._parse_metrics(result.stdout + "\n" + result.stderr)
        primary_metric = self._primary_metric_value(metrics)
        status = "success" if result.returncode == 0 and primary_metric is not None else "failed"
        notes = "Baseline command completed successfully and primary metric was captured."
        if result.returncode == 0 and primary_metric is None:
            notes = "Baseline command completed, but no primary metric was captured."
        elif result.returncode != 0 and primary_metric is not None:
            status = "metrics_captured"
            notes = "Baseline command exited non-zero, but current-run metrics were captured from stdout/stderr."
        elif result.returncode != 0:
            notes = "Baseline command failed and no primary metric was captured."
        write_text(
            paths.results_dir / "baseline_metrics.json",
            BaselineRunSummary(
                command=self.config.eval_command,
                pre_eval_commands=self.config.pre_eval_commands,
                returncode=int(result.returncode),
                status=status,
                metrics=metrics,
                primary_metric=primary_metric,
                log_path=str(log_path),
                started_at=started_at,
                finished_at=finished_at,
                notes=notes,
            ).model_dump_json(indent=2),
        )
        return BaselineRunSummary(
            command=self.config.eval_command,
            pre_eval_commands=self.config.pre_eval_commands,
            returncode=int(result.returncode),
            status=status,
            metrics=metrics,
            primary_metric=primary_metric,
            log_path=str(log_path),
            started_at=started_at,
            finished_at=finished_at,
            notes=notes,
        )

    def _parse_metrics(self, text: str) -> dict[str, float]:
        metrics: dict[str, float] = {}
        pattern = re.compile(
            r"(?im)^\s*([A-Za-z][A-Za-z0-9_./-]{0,40})\s*[:=]\s*"
            r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
        )
        for match in pattern.finditer(text):
            key = match.group(1).strip().lower().replace("-", "_")
            try:
                metrics[key] = float(match.group(2))
            except ValueError:
                continue
        return metrics

    def _primary_metric_value(self, metrics: dict[str, float]) -> float | None:
        primary = self.config.primary_metric.lower().replace("-", "_")
        if primary in metrics:
            return metrics[primary]
        for key, value in metrics.items():
            if key.lower().replace("-", "_") == primary:
                return value
        return None

    def _command_summary(self, stage: str, commands: list[str], result, log_path: Path) -> CommandExecutionSummary:
        fix_summary: FixRunSummary | None = getattr(result, "autosota_fix_summary", None)
        fix_attempts = len(fix_summary.attempts) if fix_summary is not None else 0
        if int(result.returncode) == 0:
            notes = "ok"
        elif fix_summary is not None and fix_attempts:
            notes = f"failed after AgentFix attempts; stopped_reason={fix_summary.stopped_reason}"
        else:
            notes = "failed; inspect command logs"
        return CommandExecutionSummary(
            stage=stage,
            commands=commands,
            returncode=int(result.returncode),
            log_path=str(log_path),
            attempted_fix=fix_attempts > 0,
            fix_attempts=fix_attempts,
            notes=notes,
        )

    def _execution_readiness(self, status: PrepareExecutionStatus) -> str:
        executed = [item for item in (status.setup, status.validation) if item is not None]
        if status.baseline is not None and status.baseline.status == "failed":
            return "blocked"
        if not executed and status.baseline is None:
            return "partial"
        if any(item.returncode != 0 for item in executed):
            return "blocked"
        if self.execute_validation and status.validation is None:
            return "partial"
        return "ready"

    def _execution_notes(self, status: PrepareExecutionStatus) -> list[str]:
        notes: list[str] = []
        if status.setup is None and self.execute_setup:
            notes.append("Setup was requested but no setup commands were available.")
        if status.validation is None and self.execute_validation:
            notes.append("Validation was requested but no validation commands were available.")
        for item in (status.setup, status.validation):
            if item is not None and item.returncode != 0:
                notes.append(f"{item.stage} failed with exit={item.returncode}; see {item.log_path}.")
        if status.baseline is not None:
            if status.baseline.status == "success":
                notes.append(f"Baseline completed with {self.config.primary_metric}={status.baseline.primary_metric}.")
            elif status.baseline.status == "metrics_captured":
                notes.append(
                    f"Baseline exited non-zero, but {self.config.primary_metric}={status.baseline.primary_metric} was captured from the current run."
                )
            else:
                notes.append(f"Baseline failed with exit={status.baseline.returncode}; see {status.baseline.log_path}.")
        if not notes:
            notes.append("Executed prepare commands completed successfully." if status.readiness_status == "ready" else "Prepare commands were not executed.")
        return notes


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
    parser.add_argument("--skip-resource-acquisition", action="store_true", help="Skip copying discovered resources into resource_root.")
    parser.add_argument("--code-agent", choices=["claude", "codex"], default="claude")
    parser.add_argument("--code-agent-command", help="Code Agent executable or command prefix.")
    parser.add_argument(
        "--code-agent-command-template",
        help="Shell template with {command} and {prompt}; defaults are backend-specific.",
    )
    parser.add_argument("--timeout-seconds", type=int, help="Per-stage Code Agent timeout.")
    parser.add_argument("--setup-timeout-seconds", type=int, help="Timeout for setup command execution.")
    parser.add_argument("--fix-timeout-seconds", type=int, help="Timeout for each AgentFix planning or command execution attempt.")
    parser.add_argument("--baseline-timeout-seconds", type=int, help="Timeout for the optional baseline check.")
    parser.add_argument("--execute-setup", action="store_true", help="Execute setup commands after environment planning.")
    parser.add_argument(
        "--execute-validation",
        action="store_true",
        help="Execute validation commands after environment planning. Implied by --execute-setup.",
    )
    parser.add_argument("--execute-baseline", action="store_true", help="Run the configured eval command once and capture current-run baseline metrics.")
    parser.add_argument(
        "--auto-fix",
        "--auto-fix-setup",
        dest="auto_fix",
        action="store_true",
        help="Let AgentFix propose and execute safe repair commands after failed setup, validation, or baseline stages.",
    )
    parser.add_argument("--max-fix-attempts", type=int, default=1, help="Maximum AgentFix attempts per failed execution stage.")
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
        execute_baseline=args.execute_baseline,
        acquire_resources=not args.skip_resource_acquisition,
        auto_fix=args.auto_fix,
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


if __name__ == "__main__":
    raise SystemExit(main())
