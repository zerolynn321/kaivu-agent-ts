from __future__ import annotations

import shlex
from pathlib import Path


def available_environment_profiles() -> list[str]:
    return ["rtx5090-cu128"]


def environment_profile_commands(profile: str, conda_env: str, repo_path: Path) -> list[str]:
    if profile != "rtx5090-cu128":
        raise ValueError(f"Unknown environment profile: {profile}")

    env = shlex.quote(conda_env)
    repo = shlex.quote(str(repo_path))
    activate = f'source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate {env}'
    return [
        f"conda create -n {env} python=3.10 pip -y",
        f"{activate} && python -m pip install --upgrade pip setuptools wheel",
        f"cd {repo} && {activate} && python -m pip install -r requirements.txt",
        (
            f"{activate} && python -m pip install --upgrade --force-reinstall "
            "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128"
        ),
        f'{activate} && python -m pip install --force-reinstall "numpy<2.0" "pillow<12"',
    ]


def environment_profile_notes(profile: str) -> str:
    if profile != "rtx5090-cu128":
        raise ValueError(f"Unknown environment profile: {profile}")
    return (
        "Use Python 3.10 with CUDA 12.8 PyTorch for RTX 5090/sm_120, then pin "
        "numpy<2.0 and pillow<12 to keep faiss/autogluon-compatible ABI constraints."
    )
