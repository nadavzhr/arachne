"""Load YAML/TOML configuration files and validate into pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from arachne.models.schema import Filters, JobSearchCriteria


class LoggingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = True
    directory: str = "logs"
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    central_file: str = "arachne.log"
    source_directory: str = "sources"


class GlobalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    data_dir: str = "data"
    timeout_seconds: float = 30.0
    concurrency: int = 5
    user_agent: str = "arachne/0.1.0"
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    search: JobSearchCriteria = Field(default_factory=JobSearchCriteria)
    filters: Filters = Field(default_factory=Filters)


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = True
    name: str = ""
    url: str
    search: JobSearchCriteria = Field(default_factory=JobSearchCriteria)
    headers: dict[str, str] = Field(default_factory=dict)
    user_agent: str | None = None
    filters: Filters = Field(default_factory=Filters)


def load_global(path: Path) -> GlobalConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlobalConfig(**data)


def load_sources(path: Path, global_cfg: GlobalConfig | None = None) -> dict[str, SourceConfig]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    result: dict[str, SourceConfig] = {}
    for name, raw in data.items():
        source_raw = dict(raw or {})
        source_raw["name"] = name
        source_search = source_raw.pop("search", {}) or {}
        source_filters = source_raw.pop("filters", {}) or {}
        if global_cfg is not None:
            source_raw["search"] = {
                **global_cfg.search.model_dump(mode="json"),
                **source_search,
            }
            source_raw["filters"] = {
                **global_cfg.filters.model_dump(mode="json"),
                **source_filters,
            }
        elif source_search:
            source_raw["search"] = source_search
        if global_cfg is None and source_filters:
            source_raw["filters"] = source_filters
        if global_cfg is not None and "user_agent" not in source_raw:
            source_raw["user_agent"] = global_cfg.user_agent
        result[name] = SourceConfig(**source_raw)
    return result


def load_all(config_dir: Path) -> tuple[GlobalConfig, dict[str, SourceConfig]]:
    global_cfg = load_global(config_dir / "global.yaml")
    sources = load_sources(config_dir / "sources.yaml", global_cfg=global_cfg)
    return global_cfg, sources
