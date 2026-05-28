from __future__ import annotations

from pathlib import Path

from .io import ensure_dir, read_jsonl


def plot_scores(scores_path: Path, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return

    rows = [r for r in read_jsonl(scores_path) if isinstance(r.get("iter"), int)]
    if not rows:
        return
    xs = [int(r["iter"]) for r in rows]
    ys = [float(r["primary_metric"]) for r in rows]
    ensure_dir(output_path.parent)
    plt.figure(figsize=(8, 4.5))
    plt.plot(xs, ys, marker="o")
    plt.xlabel("Iteration")
    plt.ylabel("Primary metric")
    plt.title("AutoSOTA Laboratory Optimization Curve")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
