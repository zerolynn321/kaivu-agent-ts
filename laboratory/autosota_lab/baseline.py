from __future__ import annotations

import argparse
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.io import read_yaml, write_text, write_yaml
    from autosota_lab.local_runner import LocalRunner
    from autosota_lab.models import BaselineRunSummary, PaperConfig
    from autosota_lab.state import config_path, create_run_paths
else:
    from .io import read_yaml, write_text, write_yaml
    from .local_runner import LocalRunner
    from .models import BaselineRunSummary, PaperConfig
    from .state import config_path, create_run_paths


class BaselineRunner:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        repo_path: Path | None = None,
        conda_env: str | None = None,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.config = PaperConfig.model_validate(read_yaml(config_path(self.workspace, paper_name)))
        if repo_path:
            self.config.repo_path = repo_path.expanduser().resolve()
        if conda_env is not None:
            self.config.conda_env = conda_env
        self.dry_run = dry_run

    def run(self, timeout_seconds: int | None = None) -> Path:
        paths = create_run_paths(self.workspace, self.paper_name)
        write_yaml(paths.logs_dir / "effective_config.yaml", self.config)
        runner = LocalRunner(
            repo_path=self.config.repo_path,
            run_dir=paths.run_dir,
            env=self.config.env_vars,
            conda_executable=self.config.conda_executable,
            venv_path=self.config.venv_path,
        )
        self._announce("baseline_start", f"repo={runner.repo_workdir}, conda_env={self.config.conda_env or '(none)'}")
        summary = self._execute_baseline(runner, paths, timeout_seconds=timeout_seconds or self.config.eval_timeout_seconds)
        self._announce("baseline_complete", f"status={summary.status}, exit={summary.returncode}, primary={summary.primary_metric}")
        return paths.run_dir

    def _execute_baseline(self, runner: LocalRunner, paths, timeout_seconds: int | None = None) -> BaselineRunSummary:
        started_at = datetime.now(timezone.utc).isoformat()
        commands = [*self.config.pre_eval_commands, self.config.eval_command]
        log_path = paths.logs_dir / "baseline_eval.log"
        script_rel = "logs/baseline_eval.sh"
        script_path = runner.run_dir / script_rel
        script = self._shell_script(
            commands,
            conda_env=self.config.conda_env,
            env_vars={
                "AUTOSOTA_RUN_DIR": runner.output_dir,
                "AUTOSOTA_OUTPUT_DIR": runner.output_dir,
                "AUTOSOTA_RESULTS_DIR": str(paths.results_dir),
                "OUTPUT_DIR": runner.output_dir,
                "RESULTS_DIR": str(paths.results_dir),
            },
        )
        write_text(script_path, script)
        command = f"bash {shlex.quote(runner.prompt_path(script_rel))}"
        preview = runner.preview(command)
        if self.dry_run:
            result = type("DryRunResult", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            write_text(log_path, f"$ {preview}\n\nDRY RUN\n\n{script}")
        else:
            result = runner.run(command, timeout_seconds=timeout_seconds, stream_output=True)
            stderr_text = "\nSTDERR:\n" + result.stderr if result.stderr else ""
            write_text(log_path, f"$ {preview}\n\nSCRIPT:\n{script}\n\nSTDOUT:\n{result.stdout}{stderr_text}")

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

        summary = BaselineRunSummary(
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
        write_text(paths.results_dir / "baseline_metrics.json", summary.model_dump_json(indent=2))
        return summary

    def _shell_script(self, commands: list[str], conda_env: str = "", env_vars: dict[str, str] | None = None) -> str:
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
            lines.append(command)
        return "\n".join(lines) + "\n"

    def _parse_metrics(self, text: str) -> dict[str, float]:
        metrics: dict[str, float] = {}
        patterns = [
            re.compile(
                r"(?im)^\s*([A-Za-z][A-Za-z0-9_./-]{0,40})\s*[:=]\s*"
                r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
            ),
            re.compile(
                r"(?im)\b(mse|mae|rmse|smape)(?:_mean)?\b\s*[:=]\s*"
                r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
            ),
        ]
        for pattern in patterns:
            for match in pattern.finditer(text):
                key = match.group(1).strip().lower().replace("-", "_")
                if key.endswith("_mean"):
                    key = key[: -len("_mean")]
                try:
                    metrics[key] = float(match.group(2))
                except ValueError:
                    continue
        return metrics

    def _primary_metric_value(self, metrics: dict[str, float]) -> float | None:
        primary = self.config.primary_metric.lower().replace("-", "_")
        candidates = [primary, f"{primary}_mean"]
        for candidate in candidates:
            if candidate in metrics:
                return metrics[candidate]
        for key, value in metrics.items():
            normalized = key.lower().replace("-", "_")
            if normalized == primary or normalized == f"{primary}_mean":
                return value
        return None

    def _announce(self, stage: str, message: str) -> None:
        print(f"\n[autosota:baseline] {stage} | {message}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run only the configured baseline command and capture metrics.")
    parser.add_argument("paper_name")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--repo", type=Path, help="Override repo_path from the paper config.")
    parser.add_argument("--conda-env", help="Override the conda environment used for baseline execution.")
    parser.add_argument("--baseline-timeout-seconds", type=int, help="Timeout for baseline execution.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    run_dir = BaselineRunner(
        workspace=args.workspace,
        paper_name=args.paper_name,
        repo_path=args.repo,
        conda_env=args.conda_env,
        dry_run=args.dry_run,
    ).run(timeout_seconds=args.baseline_timeout_seconds)
    print(f"[baseline] run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
