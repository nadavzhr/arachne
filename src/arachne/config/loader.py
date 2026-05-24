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
    spider_directory: str = "spiders"


class GlobalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    data_dir: str = "data"
    timeout_seconds: float = 30.0
    concurrency: int = 5
    user_agent: str = "arachne/0.1.0"
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class SpiderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = True
    name: str = ""
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    user_agent: str | None = None


def load_global(path: Path) -> GlobalConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlobalConfig(**data)


def load_spiders(path: Path, global_cfg: GlobalConfig | None = None) -> dict[str, SpiderConfig]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    result: dict[str, SpiderConfig] = {}
    for name, raw in data.items():
        spider_raw = dict(raw or {})
        spider_raw["name"] = name
        # Remove unsupported config items if they exist to prevent validation errors
        spider_raw.pop("search", None)
        spider_raw.pop("filters", None)

        if global_cfg is not None and "user_agent" not in spider_raw:
            spider_raw["user_agent"] = global_cfg.user_agent
        result[name] = SpiderConfig(**spider_raw)
    return result


def load_all(config_dir: Path) -> tuple[GlobalConfig, dict[str, SpiderConfig]]:
    global_cfg = load_global(config_dir / "global.yaml")
    spiders = load_spiders(config_dir / "spiders.yaml", global_cfg=global_cfg)
    return global_cfg, spiders
