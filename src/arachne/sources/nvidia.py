"""NVIDIA source implementation with per-source normalization.

Nvidia returns `positionUrl` suffixes; build full URLs similarly to Microsoft.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from httpx import AsyncClient

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.base import Source as BaseSource
from arachne.sources.http_json import fetch as _http_fetch
from arachne.utils.normalization import build_url, normalize_records


class NvidiaSource(BaseSource):
    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)

    async def fetch(self, client: AsyncClient) -> Any:
        return await _http_fetch(self.cfg, client)

    def normalize(self, raw: Any) -> list[JobPosting]:
        items = raw
        if isinstance(raw, dict) and "jobs" in raw:
            items = raw["jobs"]
        if isinstance(items, list) and len(items) == 1 and isinstance(items[0], dict):
            if "jobs" in items[0]:
                items = items[0]["jobs"]
            elif (
                "data" in items[0]
                and isinstance(items[0]["data"], dict)
                and "positions" in items[0]["data"]
            ):
                items = items[0]["data"]["positions"]
        if not isinstance(items, list):
            return []

        base = self.cfg.apply_base
        if not base:
            try:
                p = urlparse(self.cfg.url)
                base = f"{p.scheme}://{p.netloc}"
            except Exception:
                base = None

        for rec in items:
            if not isinstance(rec, dict):
                continue
            pos = rec.get("positionUrl") or rec.get("positionUrlSuffix")
            if pos:
                u = build_url(base, pos)
                if u:
                    rec["url"] = u

        return normalize_records("nvidia", items)


# Backwards-compatible name used by dynamic loader
Source = NvidiaSource
