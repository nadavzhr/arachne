"""Amazon spider implementation."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from httpx import AsyncClient

from arachne.clients.http import fetch_json
from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.amazon.params import AmazonParams
from arachne.spiders.base import Spider as BaseSpider
from arachne.utils.normalization import (
    build_url,
    parse_datetime,
    try_parse_json_string,
)

logger = logging.getLogger(__name__)


class AmazonSpider(BaseSpider):
    def __init__(self, cfg: SpiderConfig) -> None:
        super().__init__(cfg)

    async def fetch(self, client: AsyncClient, search: JobSearchCriteria) -> Any:
        params = AmazonParams.from_search(search)
        self.log.info("http request started: url=%s", self.cfg.url)
        raw = await fetch_json(
            client, self.cfg.url, params=params.to_query(), headers=self.cfg.headers
        )
        return raw if isinstance(raw, list) else [raw]

    def normalize(self, raw: Any) -> list[JobPosting]:
        items = raw
        if isinstance(raw, list) and len(raw) == 1 and isinstance(raw[0], dict):
            items = raw[0].get("jobs", [])
        elif isinstance(raw, dict) and "jobs" in raw:
            items = raw["jobs"]

        if not isinstance(items, list):
            return []

        base = None
        try:
            p = urlparse(self.cfg.url)
            base = f"{p.scheme}://{p.netloc}"
        except Exception:
            base = None

        jobs: list[JobPosting] = []
        for rec in items:
            if not isinstance(rec, dict):
                continue

            title = rec.get("title")
            job_path = rec.get("job_path")
            if not title or not job_path:
                continue

            job_url = build_url(base, job_path)
            if not job_url:
                continue

            # parse locations that are JSON-encoded strings
            locs = rec.get("locations")
            location_str = rec.get("location")
            if (
                isinstance(locs, list)
                and locs
                and isinstance(locs[0], str)
                and locs[0].strip().startswith("{")
            ):
                parsed = [try_parse_json_string(x) for x in locs]
                extracted = []
                for loc in parsed:
                    if isinstance(loc, dict):
                        city = loc.get("city")
                        country = loc.get("country_code") or loc.get("country")
                        if city and country:
                            extracted.append(f"{city}, {country}")
                        elif city:
                            extracted.append(str(city))
                if extracted:
                    location_str = " | ".join(extracted)

            try:
                jobs.append(
                    JobPosting(
                        spider=self.name,
                        company="Amazon",
                        title=str(title).strip(),
                        url=job_url,  # type: ignore
                        location=location_str,
                        external_id=str(rec.get("id_icims") or rec.get("id") or ""),
                        description=rec.get("description") or rec.get("basic_qualifications"),
                        posted_at=parse_datetime(rec.get("posted_date")),
                    )
                )
            except Exception as e:
                logger.debug("Failed to map amazon record: %s", e)

        return jobs


# Backwards-compatible name used by dynamic loader
Spider = AmazonSpider
