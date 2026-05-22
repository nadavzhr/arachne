"""Load YAML/TOML configuration files and validate into pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class Filters(BaseModel):
    include_keywords: list[str] = []
    exclude_keywords: list[str] = []
    locations: list[str] = []


class GlobalConfig(BaseModel):
    data_dir: str = "data"
    timeout_seconds: float = 30.0
    concurrency: int = 5
    user_agent: str = "arachne/0.1.0"
    filters: Filters = Filters()


class SourceConfig(BaseModel):
    enabled: bool = True
    url: str
    params: dict[str, Any] | None = None
    headers: dict[str, str] | None = None
    apply_base: str | None = None
    user_agent: str | None = None
    filters: Filters = Filters()


def load_global(path: Path) -> GlobalConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlobalConfig(**data)


def load_sources(path: Path, global_cfg: GlobalConfig | None = None) -> dict[str, SourceConfig]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    result: dict[str, SourceConfig] = {}
    for name, raw in data.items():
        source_raw = dict(raw or {})
        source_filters = source_raw.pop("filters", {}) or {}
        merged_filters: dict[str, Any] = {}
        if global_cfg is not None:
            merged_filters = global_cfg.filters.model_dump()
        combined_filters = {**merged_filters, **source_filters}
        if combined_filters:
            source_raw["filters"] = combined_filters
        if global_cfg is not None and "user_agent" not in source_raw:
            source_raw["user_agent"] = global_cfg.user_agent
        result[name] = SourceConfig(**source_raw)
    return result


def load_all(config_dir: Path) -> tuple[GlobalConfig, dict[str, SourceConfig]]:
    global_cfg = load_global(config_dir / "global.yaml")
    sources = load_sources(config_dir / "sources.yaml", global_cfg=global_cfg)
    return global_cfg, sources
