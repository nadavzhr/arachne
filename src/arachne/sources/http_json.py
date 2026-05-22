"""HTTP JSON fetcher used when no provider-specific module exists.

This module implements a minimal `fetch(cfg, client)` coroutine that performs a raw
HTTP JSON fetch and returns a list of results (or a single-item list for object responses).
"""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient

from arachne.clients.http import fetch_json, fetch_paginated_json
from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.base import Source as BaseSource
from arachne.utils.normalization import normalize_records


async def fetch(
    cfg: SourceConfig,
    client: AsyncClient,
    params: dict[str, Any] | None = None,
) -> list[Any]:
    raw = await fetch_json(client, cfg.url, params=params, headers=cfg.headers)
    if isinstance(raw, list):
        return raw
    return [raw]


async def fetch_paginated(
    cfg: SourceConfig,
    client: AsyncClient,
    params: dict[str, Any] | None = None,
) -> list[Any]:
    return await fetch_paginated_json(client, cfg.url, params=params, headers=cfg.headers)


class HTTPSource(BaseSource):
    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)

    async def fetch(self, client: AsyncClient) -> Any:
        return await fetch(self.cfg, client)

    def normalize(self, raw: Any) -> list[JobPosting]:
        return normalize_records(self.cfg.url, raw)


# Backwards-compatible name used by dynamic loader
Source = HTTPSource
