from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from .io import ensure_dir
from .models import RunPaths


def paper_dir(workspace: Path, paper_name: str) -> Path:
    return workspace / ".autosota" / "papers" / paper_name


def config_path(workspace: Path, paper_name: str) -> Path:
    return paper_dir(workspace, paper_name) / "config.yaml"


def create_run_paths(workspace: Path, paper_name: str) -> RunPaths:
    base = paper_dir(workspace, paper_name)
    stamp = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    run_dir = base / stamp
    paths = RunPaths(
        workspace=workspace,
        paper_dir=base,
        run_dir=run_dir,
        logs_dir=run_dir / "logs",
        memory_dir=run_dir / "memory",
        results_dir=run_dir / "results",
    )
    for path in (paths.paper_dir, paths.run_dir, paths.logs_dir, paths.memory_dir, paths.results_dir):
        ensure_dir(path)
    latest = base / "latest"
    try:
        if latest.exists() or latest.is_symlink():
            latest.unlink()
        os.symlink(run_dir.name, latest)
    except OSError:
        # Symlinks can fail on some filesystems; a text pointer is enough for the prototype.
        latest.write_text(run_dir.name, encoding="utf-8")
    return paths
