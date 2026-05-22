"""HTTP JSON fetcher used when no provider-specific module exists.

This module implements a minimal `fetch(cfg, client)` coroutine that performs a raw
HTTP JSON fetch and returns a list of results (or a single-item list for object responses).
"""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient

from arachne.clients.http import fetch_json, fetch_paginated_json
from arachne.config.loader import SourceConfig
from arachne.logging_config import source_logger
from arachne.models.job import JobPosting
from arachne.sources.base import Source as BaseSource
from arachne.utils.normalization import normalize_records


async def fetch(
    cfg: SourceConfig,
    client: AsyncClient,
    params: dict[str, Any] | None = None,
) -> list[Any]:
    log = source_logger(cfg.name or "http", __name__)
    log.info("http request started: url=%s", cfg.url)
    raw = await fetch_json(client, cfg.url, params=params, headers=cfg.headers)
    records = raw if isinstance(raw, list) else [raw]
    log.info("http request completed: records=%d", len(records))
    return records


async def fetch_paginated(
    cfg: SourceConfig,
    client: AsyncClient,
    params: dict[str, Any] | None = None,
) -> list[Any]:
    log = source_logger(cfg.name or "http", __name__)
    log.info("paginated http request started: url=%s", cfg.url)
    records = await fetch_paginated_json(client, cfg.url, params=params, headers=cfg.headers)
    log.info("paginated http request completed: records=%d", len(records))
    return records


class HTTPSource(BaseSource):
    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)

    async def fetch(self, client: AsyncClient) -> Any:
        return await fetch(self.cfg, client)

    def normalize(self, raw: Any) -> list[JobPosting]:
        return normalize_records(self.cfg.url, raw)


# Backwards-compatible name used by dynamic loader
Source = HTTPSource
