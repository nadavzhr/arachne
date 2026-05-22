#! /usr/bin/env python3
"""Orchestrator that loads config, fetches from sources and writes snapshots."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import arachne.filters
import arachne.models.job
from arachne.clients.http import create_client
from arachne.config.loader import load_all
from arachne.sources import get_source_class
from arachne.sources.base import Source
from arachne.storage.json import JsonFileJobStorage

logger = logging.getLogger(__name__)


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


async def run_from_config(config_dir: Path) -> None:
    global_cfg, sources = load_all(config_dir)

    data_dir = Path(global_cfg.data_dir)
    storage = JsonFileJobStorage(data_dir)

    async with create_client(global_cfg.timeout_seconds, global_cfg.user_agent) as client:
        concurrency_limit = max(1, global_cfg.concurrency)
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def _fetch_with_limit(source: Source) -> Any:
            await semaphore.acquire()
            try:
                return await source.fetch(client)
            finally:
                semaphore.release()

        tasks: dict[str, asyncio.Task[Any]] = {}
        sources_instances: dict[str, Source] = {}
        for name, cfg in sources.items():
            if not cfg.enabled:
                logger.info("Skipping disabled source %s", name)
                continue
            SourceCls = get_source_class(name)
            src = SourceCls(cfg)
            sources_instances[name] = src
            tasks[name] = asyncio.create_task(_fetch_with_limit(src))

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for (name, _task), result in zip(tasks.items(), results, strict=False):
            if isinstance(result, Exception):
                logger.error("Source %s failed: %s", name, result)
                continue
            # Persist raw fetched payload for inspection
            storage.save_raw(name, result)

            # Normalize fetched payload into JobPosting models using per-source normalizer
            src = sources_instances[name]
            try:
                jobs = src.normalize(result)
            except Exception as exc:
                logger.error("Normalization failed for %s: %s", name, exc)
                jobs = []
            if not jobs:
                logger.warning("No normalized jobs for %s", name)

            normalized_jobs = _ensure_source(name, jobs)
            filtered_jobs = arachne.filters.apply_filters(normalized_jobs, src.cfg.filters)

            unfiltered_payload = [j.model_dump(mode="json") for j in normalized_jobs]
            filtered_payload = [j.model_dump(mode="json") for j in filtered_jobs]

            storage.save(name, unfiltered_payload, filename="jobs.unfiltered.json")
            storage.save(name, filtered_payload)
            logger.info("Wrote snapshot for %s", name)


def run_sync(config_dir: Path | str = "config") -> None:
    asyncio.run(run_from_config(Path(config_dir)))


if __name__ == "__main__":
    run_sync()
