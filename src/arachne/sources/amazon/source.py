"""Amazon source implementation with per-source request mapping and normalization."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from httpx import AsyncClient

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.amazon.params import AmazonParams
from arachne.sources.base import Source as BaseSource
from arachne.sources.http_json import fetch as _http_fetch
from arachne.utils.normalization import build_url, normalize_records, try_parse_json_string


class AmazonSource(BaseSource):
    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)
        self.params = AmazonParams.from_search(cfg.search)

    async def fetch(self, client: AsyncClient) -> Any:
        return await _http_fetch(self.cfg, client, params=self.params.to_query())

    def normalize(self, raw: Any) -> list[JobPosting]:
        # raw is expected to be {'jobs': [...] } or a list
        items = raw
        if isinstance(raw, dict) and "jobs" in raw:
            items = raw["jobs"]
        # some endpoints return a list wrapping a dict that contains `jobs`
        if (
            isinstance(items, list)
            and len(items) == 1
            and isinstance(items[0], dict)
            and "jobs" in items[0]
        ):
            items = items[0]["jobs"]
        if not isinstance(items, list):
            return []

        base = None
        try:
            p = urlparse(self.cfg.url)
            base = f"{p.scheme}://{p.netloc}"
        except Exception:
            base = None

        # massage items in-place to set `url` field
        for rec in items:
            if not isinstance(rec, dict):
                continue
            # prefer the canonical job detail path when available
            if rec.get("job_path"):
                u = build_url(base, rec.get("job_path"))
                if u:
                    rec["url"] = u
            elif rec.get("url_next_step"):
                rec["url"] = rec.get("url_next_step")

            # parse locations that are JSON-encoded strings
            locs = rec.get("locations")
            if (
                isinstance(locs, list)
                and locs
                and isinstance(locs[0], str)
                and locs[0].strip().startswith("{")
            ):
                parsed = [try_parse_json_string(x) for x in locs]
                rec["locations"] = parsed

        return normalize_records("amazon", items)


# Backwards-compatible name used by dynamic loader
Source = AmazonSource
