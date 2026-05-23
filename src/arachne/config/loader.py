"""Load YAML/TOML configuration files and validate into pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


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


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = True
    name: str = ""
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    user_agent: str | None = None


def load_global(path: Path) -> GlobalConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlobalConfig(**data)


def load_sources(path: Path, global_cfg: GlobalConfig | None = None) -> dict[str, SourceConfig]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    result: dict[str, SourceConfig] = {}
    for name, raw in data.items():
        source_raw = dict(raw or {})
        source_raw["name"] = name
        # Remove unsupported config items if they exist to prevent validation errors
        source_raw.pop("search", None)
        source_raw.pop("filters", None)

        if global_cfg is not None and "user_agent" not in source_raw:
            source_raw["user_agent"] = global_cfg.user_agent
        result[name] = SourceConfig(**source_raw)
    return result


def load_all(config_dir: Path) -> tuple[GlobalConfig, dict[str, SourceConfig]]:
    global_cfg = load_global(config_dir / "global.yaml")
    sources = load_sources(config_dir / "sources.yaml", global_cfg=global_cfg)
    return global_cfg, sources
