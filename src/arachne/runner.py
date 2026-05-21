#! /usr/bin/env python3
"""Orchestrator that loads config, fetches from sources and writes snapshots."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from arachne.clients.http import create_client
from arachne.config.loader import load_all
from arachne.sources import get_source_class
from arachne.sources.base import Source
from arachne.storage.json import JsonFileJobStorage

logger = logging.getLogger(__name__)


async def run_from_config(config_dir: Path) -> None:
    global_cfg, sources = load_all(config_dir)

    data_dir = Path(global_cfg.data_dir)
    storage = JsonFileJobStorage(data_dir)

    async with create_client(global_cfg.timeout_seconds) as client:
        tasks: dict[str, asyncio.Task[Any]] = {}
        sources_instances: dict[str, Source] = {}
        for name, cfg in sources.items():
            if not cfg.enabled:
                logger.info("Skipping disabled source %s", name)
                continue
            SourceCls = get_source_class(name)
            src = SourceCls(cfg)
            sources_instances[name] = src
            tasks[name] = asyncio.create_task(src.fetch(client))

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
            payload: list[object] = []
            if jobs:
                # Persist normalized records as JSON-serializable dicts
                payload = [j.model_dump(mode="json") for j in jobs]
            else:
                # Normalization produced no valid items; persist raw payload so
                # consumers can inspect and we don't produce empty snapshots.
                logger.warning(f"No normalized jobs for {name}")

            storage.save(name, payload)
            logger.info("Wrote snapshot for %s", name)


def run_sync(config_dir: Path | str = "config") -> None:
    asyncio.run(run_from_config(Path(config_dir)))


if __name__ == "__main__":
    run_sync()
