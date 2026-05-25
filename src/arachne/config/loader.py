"""Load YAML/TOML configuration files and validate into pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class LoggingConfig(BaseModel):
    """Configuration for the application's logging system."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = Field(default=True, description="Whether logging is globally enabled")
    directory: str = Field(default="logs", description="Base directory for log files")
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Global log level for stdout and central file"
    )
    central_file: str = Field(default="arachne.log", description="Filename for the combined logs")
    spider_directory: str = Field(
        default="spiders", description="Subdirectory for isolated spider logs"
    )


class GlobalConfig(BaseModel):
    """System-wide settings for the Arachne engine."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    data_dir: str = Field(default="data", description="Directory for storing scraped job data")
    timeout_seconds: float = Field(default=30.0, description="Network timeout in seconds")
    concurrency: int = Field(default=5, description="Maximum number of concurrent spider runs")
    user_agent: str = Field(default="arachne/0.1.0", description="Default HTTP User-Agent header")
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration block"
    )


class SpiderConfig(BaseModel):
    """Configuration for a specific spider adapter."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    enabled: bool = Field(default=True, description="Whether this spider is active")
    name: str = Field(default="", description="The internal name of the spider")
    url: str = Field(description="Base URL or API endpoint for the spider")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Custom HTTP headers for this spider"
    )
    user_agent: str | None = Field(default=None, description="Spider-specific User-Agent override")


def load_global(path: Path) -> GlobalConfig:
    """Load and validate global configuration from a YAML file.

    Args:
        path: Path to the global.yaml configuration file.

    Returns:
        GlobalConfig: Validated global configuration model.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return GlobalConfig(**data)


def load_spiders(path: Path, global_cfg: GlobalConfig | None = None) -> dict[str, SpiderConfig]:
    """Load and validate spider registry from a YAML file.

    Args:
        path: Path to the spiders.yaml configuration file.
        global_cfg: Optional global configuration to inherit defaults from.

    Returns:
        dict[str, SpiderConfig]: Mapping of spider names to their configurations.
    """
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
    """Load both global and spider configurations from a directory.

    Args:
        config_dir: Directory containing global.yaml and spiders.yaml.

    Returns:
        tuple[GlobalConfig, dict[str, SpiderConfig]]: A pair of (global_cfg, spiders).
    """
    global_cfg = load_global(config_dir / "global.yaml")
    spiders = load_spiders(config_dir / "spiders.yaml", global_cfg=global_cfg)
    return global_cfg, spiders
