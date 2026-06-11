from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from autosota_lab.agents import AgentResource
    from autosota_lab.code_agent import create_code_agent
    from autosota_lab.io import write_text
    from autosota_lab.local_runner import LocalRunner
    from autosota_lab.models import RepoCandidate, RepoResolutionPlan
    from autosota_lab.prompts import repo_resolution_prompt
    from autosota_lab.state import create_run_paths
else:
    from .agents import AgentResource
    from .code_agent import create_code_agent
    from .io import write_text
    from .local_runner import LocalRunner
    from .models import RepoCandidate, RepoResolutionPlan
    from .prompts import repo_resolution_prompt
    from .state import create_run_paths


class RepoResolver:
    def __init__(
        self,
        workspace: Path,
        paper_name: str,
        search_roots: list[Path] | None = None,
        repo_root: Path | None = None,
        paper_title: str = "",
        research_requirement: str = "",
        clone_url: str = "",
        code_agent: str = "codex",
        code_agent_command: str | None = None,
        code_agent_command_template: str | None = None,
        max_depth: int = 3,
        no_clone: bool = False,
        refresh_clone: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.paper_name = paper_name
        self.search_roots = [path.expanduser().resolve() for path in search_roots or []]
        self.repo_root = repo_root.expanduser().resolve() if repo_root else None
        self.paper_title = paper_title
        self.research_requirement = research_requirement
        self.clone_url = clone_url
        self.code_agent = code_agent
        self.code_agent_command = code_agent_command
        self.code_agent_command_template = code_agent_command_template
        self.max_depth = max(1, max_depth)
        self.no_clone = no_clone
        self.refresh_clone = refresh_clone
        self.dry_run = dry_run

    def run(self, timeout_seconds: int | None = None, clone_timeout_seconds: int | None = None) -> RepoResolutionPlan:
        paths = create_run_paths(self.workspace, self.paper_name)
        self._announce("repo_resolution_start", f"run_dir={paths.run_dir}")
        local_candidates = self._scan_local_candidates()
        write_text(
            paths.memory_dir / "repo_local_candidates.json",
            RepoResolutionPlan(candidates=local_candidates).model_dump_json(indent=2),
        )

        runner_root = self._runner_root(local_candidates)
        runner = LocalRunner(repo_path=runner_root, run_dir=paths.run_dir)
        code_agent = create_code_agent(
            runner,
            agent=self.code_agent,
            command=self.code_agent_command,
            command_template=self.code_agent_command_template,
        )
        agent = AgentResource(code_agent)
        prompt = repo_resolution_prompt(
                paper_name=self.paper_name,
                search_roots=[str(path) for path in self.search_roots],
                local_candidates=[candidate.model_dump(mode="json") for candidate in local_candidates],
                paper_title=self.paper_title,
                research_requirement=self.research_requirement,
            clone_url=self.clone_url,
            repo_root=str(self.repo_root or ""),
        )
        output_path = paths.memory_dir / "repo_resolution_plan.json"
        log_path = paths.logs_dir / f"{self.code_agent}_repo_resolution.log"
        if hasattr(agent, "resolve_repo"):
            plan = agent.resolve_repo(
                prompt,
                output_path,
                log_path,
                timeout_seconds=timeout_seconds,
                dry_run=self.dry_run,
            )
        else:
            plan = self._resolve_repo_direct(code_agent, prompt, output_path, log_path, timeout_seconds)
        if not plan.candidates and local_candidates:
            plan.candidates = local_candidates
        if plan.action == "clone" and plan.selected_clone_url and not self.no_clone:
            clone_path = self._clone_repo(plan.selected_clone_url, clone_timeout_seconds)
            plan.selected_repo_path = str(clone_path)
            plan.evidence.append(f"Cloned selected repository to {clone_path}.")
            write_text(paths.memory_dir / "repo_resolution_plan.json", plan.model_dump_json(indent=2))
        self._announce("repo_resolution_complete", f"action={plan.action}, repo={plan.selected_repo_path or '(none)'}")
        return plan

    def _scan_local_candidates(self) -> list[RepoCandidate]:
        candidates: list[RepoCandidate] = []
        for root in self.search_roots:
            if not root.exists() or not root.is_dir():
                continue
            for path in self._candidate_dirs(root):
                evidence = self._candidate_evidence(path)
                if not evidence:
                    continue
                candidates.append(
                    RepoCandidate(
                        name=path.name,
                        local_path=str(path),
                        source="local",
                        confidence=self._local_confidence(path, evidence),
                        evidence=evidence,
                    )
                )
        candidates.sort(key=self._candidate_sort_key)
        return candidates

    def _candidate_dirs(self, root: Path) -> list[Path]:
        dirs: list[Path] = []
        blocked = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", "env"}
        stack = [(root, 0)]
        while stack:
            path, depth = stack.pop()
            dirs.append(path)
            if depth >= self.max_depth:
                continue
            try:
                children = sorted((child for child in path.iterdir() if child.is_dir()), key=lambda item: item.name)
            except OSError:
                continue
            for child in reversed(children):
                if child.name in blocked or child.name.startswith(".autosota"):
                    continue
                stack.append((child, depth + 1))
        return dirs

    def _candidate_evidence(self, path: Path) -> list[str]:
        evidence: list[str] = []
        if (path / ".git").exists():
            evidence.append(".git directory present")
        for name in ("README.md", "readme.md", "requirements.txt", "environment.yml", "pyproject.toml", "setup.py"):
            if (path / name).exists():
                evidence.append(f"{name} present")
        for name in ("script", "scripts", "eval.py", "main.py", "train.py", "test.py"):
            if (path / name).exists():
                evidence.append(f"{name} present")
        lowered = f"{path.name} {self.paper_name} {self.paper_title}".lower()
        if self.paper_name.lower() in lowered or (self.paper_title and self.paper_title.lower() in lowered):
            evidence.append("directory/name text matches paper identifier")
        remote = self._git_remote(path)
        if remote:
            evidence.append(f"git remote: {remote}")
        return evidence

    def _local_confidence(self, path: Path, evidence: list[str]) -> str:
        score = len(evidence)
        if any("name text matches" in item for item in evidence):
            score += 2
        if (path / ".git").exists():
            score += 1
        if score >= 5:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    def _candidate_sort_key(self, candidate: RepoCandidate) -> tuple[int, str]:
        confidence_rank = {"high": 0, "medium": 1, "low": 2}
        return (confidence_rank.get(candidate.confidence, 3), candidate.local_path)

    def _git_remote(self, path: Path) -> str:
        try:
            proc = subprocess.run(
                ["git", "-C", str(path), "remote", "get-url", "origin"],
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
        except Exception:
            return ""
        return proc.stdout.strip() if proc.returncode == 0 else ""

    def _runner_root(self, candidates: list[RepoCandidate]) -> Path:
        for candidate in candidates:
            if candidate.local_path:
                return Path(candidate.local_path)
        if self.search_roots:
            return self.search_roots[0]
        return self.workspace

    def _clone_repo(self, clone_url: str, timeout_seconds: int | None = None) -> Path:
        if self.repo_root is None:
            raise ValueError("--repo-root is required when cloning a repository")
        destination = self.repo_root / self._repo_name_from_url(clone_url)
        destination = destination.resolve()
        self.repo_root.mkdir(parents=True, exist_ok=True)
        try:
            destination.relative_to(self.repo_root.resolve())
        except ValueError as exc:
            raise ValueError(f"Refusing to clone outside repo root: {destination}") from exc
        if destination.exists() and self.refresh_clone:
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        if destination.exists():
            return destination
        if self.dry_run:
            return destination
        subprocess.run(["git", "clone", clone_url, str(destination)], check=True, timeout=timeout_seconds)
        return destination

    def _repo_name_from_url(self, clone_url: str) -> str:
        name = clone_url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name or self.paper_name

    def _announce(self, stage: str, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[autosota:repo] {timestamp} | {stage} | {message}", flush=True)

    def _resolve_repo_direct(self, code_agent, prompt: str, output_path: Path, log_path: Path, timeout_seconds: int | None) -> RepoResolutionPlan:
        try:
            plan = code_agent.complete_structured(
                phase="agent_resource_repo_resolution",
                prompt=prompt,
                schema=RepoResolutionPlan,
                log_path=log_path,
                timeout_seconds=timeout_seconds,
                dry_run=self.dry_run,
            )
        except Exception as exc:
            plan = RepoResolutionPlan(
                action="failed",
                warnings=["RepoResolver fallback did not produce a valid structured repo resolution plan."],
                notes=f"Fallback repo resolution plan generated because Code Agent failed: {exc}",
            )
        write_text(output_path, plan.model_dump_json(indent=2))
        return plan
