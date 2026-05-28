from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - fallback for bare prototype envs
    yaml = None


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        if yaml is None:
            return json.load(f)
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: BaseModel | dict) -> None:
    ensure_dir(path.parent)
    payload = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    with path.open("w", encoding="utf-8") as f:
        if yaml is None:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        else:
            yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, item: BaseModel | dict) -> None:
    ensure_dir(path.parent)
    payload = item.model_dump(mode="json") if isinstance(item, BaseModel) else item
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def render_markdown_table(rows: Iterable[dict]) -> str:
    rows = list(rows)
    if not rows:
        return ""
    keys = list(rows[0].keys())
    lines = ["| " + " | ".join(keys) + " |", "| " + " | ".join(["---"] * len(keys)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(k, "")) for k in keys) + " |")
    return "\n".join(lines)
