#! /usr/bin/env python3
"""Orchestrator that loads config, fetches from sources and writes snapshots."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import arachne.filters
import arachne.models.job
from arachne.clients.http import create_client
from arachne.config.loader import load_all
from arachne.config.profile import SearchProfile, load_profile
from arachne.logging import configure_logging, source_logger
from arachne.sources import get_source_class
from arachne.sources.base import Source
from arachne.storage.json import JsonFileJobStorage

logger = logging.getLogger(__name__)


def _timestamped_log_name(filename: str, stamp: str) -> str:
    path = Path(filename)
    suffix = path.suffix
    if suffix:
        return f"{path.stem}-{stamp}{suffix}"
    return f"{path.name}-{stamp}"


def _ensure_source(
    source: str,
    jobs: list[arachne.models.job.JobPosting],
) -> list[arachne.models.job.JobPosting]:
    normalized: list[arachne.models.job.JobPosting] = []
    for job in jobs:
        if job.source == source:
            normalized.append(job)
        else:
            normalized.append(job.model_copy(update={"source": source}))
    return normalized


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

    data_dir = Path(global_cfg.data_dir)
    storage = JsonFileJobStorage(data_dir)

    async with create_client(global_cfg.timeout_seconds, global_cfg.user_agent) as client:
        concurrency_limit = max(1, global_cfg.concurrency)
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def _fetch_with_limit(source: Source) -> Any:
            await semaphore.acquire()
            try:
                source.log.info("fetch started")
                # Ensure we type-check properly; profile is guaranteed not None here
                prof = profile or SearchProfile()
                return await source.fetch(client, prof.get_search_for(source.name))
            finally:
                source.log.info("fetch finished")
                semaphore.release()

        tasks: dict[str, asyncio.Task[Any]] = {}
        sources_instances: dict[str, Source] = {}
        for name, cfg in sources.items():
            source_log = source_logger(name, __name__)
            if not cfg.enabled:
                source_log.info("source skipped: disabled")
                continue
            SourceCls = get_source_class(name)
            src = SourceCls(cfg)
            sources_instances[name] = src
            source_log.info("source scheduled: adapter=%s", SourceCls.__name__)
            tasks[name] = asyncio.create_task(_fetch_with_limit(src))

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for (name, _task), result in zip(tasks.items(), results, strict=False):
            source_log = source_logger(name, __name__)
            if isinstance(result, Exception):
                source_log.error(
                    "fetch failed: %s",
                    result,
                    exc_info=(type(result), result, result.__traceback__),
                )
                continue
            # Persist raw fetched payload for inspection
            storage.save_raw(name, result)
            source_log.info("raw snapshot written")

            # Normalize fetched payload into JobPosting models using per-source normalizer
            src = sources_instances[name]
            try:
                source_log.info("normalization started")
                jobs = src.normalize(result)
            except Exception as exc:
                source_log.exception("normalization failed: %s", exc)
                jobs = []
            if not jobs:
                source_log.warning("normalization produced no jobs")

            normalized_jobs = _ensure_source(name, jobs)
            filtered_jobs = arachne.filters.apply_filters(
                normalized_jobs, profile.get_filters_for(name)
            )
            source_log.info(
                "normalization completed: jobs=%d filtered=%d",
                len(normalized_jobs),
                len(filtered_jobs),
            )

            unfiltered_payload = [j.model_dump(mode="json") for j in normalized_jobs]
            filtered_payload = [j.model_dump(mode="json") for j in filtered_jobs]

            storage.save(name, unfiltered_payload, filename="jobs.unfiltered.json")
            storage.save(name, filtered_payload)
            source_log.info("job snapshots written")

    logger.info("run completed")


def run_sync(config_dir: Path | str = "config", profile_path: Path | str | None = None) -> None:
    profile = load_profile(Path(profile_path)) if profile_path else None
    asyncio.run(run_from_config(Path(config_dir), profile=profile))


if __name__ == "__main__":
    import sys

    prof_path = sys.argv[1] if len(sys.argv) > 1 else "profiles/default.yaml"
    run_sync(profile_path=prof_path)
