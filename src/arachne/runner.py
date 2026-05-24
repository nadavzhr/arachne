#! /usr/bin/env python3
"""Orchestrator that loads config, fetches from sources and writes snapshots."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from arachne.clients.http import create_client
from arachne.config.loader import load_all
from arachne.config.profile import SearchProfile, load_profile
from arachne.logging import configure_logging, source_logger
from arachne.services.scraper import ScraperService
from arachne.storage.json import JsonFileJobStorage

logger = logging.getLogger(__name__)


def _timestamped_log_name(filename: str, stamp: str) -> str:
    path = Path(filename)
    suffix = path.suffix
    if suffix:
        return f"{path.stem}-{stamp}{suffix}"
    return f"{path.name}-{stamp}"


async def run_from_config(
    config_dir: Path,
    profile: SearchProfile | None = None,
) -> None:
    profile = profile or SearchProfile()
    global_cfg, sources = load_all(config_dir)
    run_stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    configure_logging(
        enabled=global_cfg.logging.enabled,
        directory=global_cfg.logging.directory,
        level=global_cfg.logging.level,
        central_file=_timestamped_log_name(global_cfg.logging.central_file, run_stamp),
        source_directory=str(Path(global_cfg.logging.source_directory) / run_stamp),
    )

    logger.info(
        "run started: config_dir=%s sources=%d concurrency=%d profile=%s",
        config_dir,
        len(sources),
        max(1, global_cfg.concurrency),
        profile.name,
    )

    storage = JsonFileJobStorage(Path(global_cfg.data_dir))

    async with create_client(global_cfg.timeout_seconds, global_cfg.user_agent) as client:
        scraper = ScraperService(
            storage=storage,
            client=client,
            concurrency=global_cfg.concurrency,
        )

        results = await scraper.run_profile(sources, profile)

        for name, result in results.items():
            source_log = source_logger(name, __name__)
            if isinstance(result, BaseException):
                source_log.error(
                    "fetch failed for source '%s': %s",
                    name,
                    result,
                    exc_info=(type(result), result, result.__traceback__),
                )
                continue

            # result is now guaranteed to be a SearchResult
            if result.normalization_error:
                source_log.error(
                    "normalization failed: %s",
                    result.normalization_error,
                    exc_info=(
                        type(result.normalization_error),
                        result.normalization_error,
                        result.normalization_error.__traceback__,
                    ),
                )

            if not result.normalized:
                source_log.warning("normalization produced no jobs")

            source_log.info(
                "run completed: jobs=%d filtered=%d",
                len(result.normalized),
                len(result.filtered),
            )

    logger.info("run completed")


def run_sync(config_dir: Path | str = "config", profile_path: Path | str | None = None) -> None:
    if profile_path is None:
        default_prof = Path("profiles/default.yaml")
        if default_prof.exists():
            profile_path = default_prof

    profile = load_profile(Path(profile_path)) if profile_path else None
    asyncio.run(run_from_config(Path(config_dir), profile=profile))


if __name__ == "__main__":
    import sys

    prof_path = sys.argv[1] if len(sys.argv) > 1 else "profiles/default.yaml"
    run_sync(profile_path=prof_path)
