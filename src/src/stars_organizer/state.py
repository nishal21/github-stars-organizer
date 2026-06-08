"""Checkpoint state for resumable apply operations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_STATE_PATH = Path(".organize-stars-state.json")


@dataclass
class ApplyState:
    plan_path: str
    lists_created: list[str] = field(default_factory=list)
    assigned_repos: list[str] = field(default_factory=list)
    failed_repos: list[str] = field(default_factory=list)

    def save(self, path: Path = DEFAULT_STATE_PATH) -> None:
        path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path = DEFAULT_STATE_PATH) -> ApplyState | None:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    @classmethod
    def clear(cls, path: Path = DEFAULT_STATE_PATH) -> None:
        if path.exists():
            path.unlink()
