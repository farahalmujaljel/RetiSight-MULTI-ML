from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SourceConfig:
    key: str
    name: str
    path: Path
    url: str
    intended_use: str


def read_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_pipeline_config(path: str | Path) -> dict[str, Any]:
    return read_yaml(path)


def load_sources(path: str | Path) -> list[SourceConfig]:
    raw = read_yaml(path).get("sources", {})
    return [
        SourceConfig(
            key=key,
            name=value["name"],
            path=Path(value["path"]),
            url=value["url"],
            intended_use=value.get("intended_use", ""),
        )
        for key, value in raw.items()
    ]

