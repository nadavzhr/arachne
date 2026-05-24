"""Microsoft spider implementation."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from httpx import AsyncClient

from arachne.clients.http import fetch_paginated_json
from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.microsoft.params import MicrosoftParams
from arachne.utils.normalization import build_url, parse_datetime

logger = logging.getLogger(__name__)


class MicrosoftSpider(BaseSpider):
    def __init__(self, cfg: SpiderConfig) -> None:
        super().__init__(cfg)

    async def fetch(self, client: AsyncClient, search: JobSearchCriteria) -> Any:
        params = MicrosoftParams.from_search(search)
        self.log.info("paginated http request started: url=%s", self.cfg.url)
        return await fetch_paginated_json(
            client, self.cfg.url, params=params.to_query(), headers=self.cfg.headers
        )

    def normalize(self, raw: Any) -> list[JobPosting]:
        if not isinstance(raw, list):
            return []

        base = None
        try:
            p = urlparse(self.cfg.url)
            base = f"{p.scheme}://{p.netloc}"
        except Exception:
            base = None

        jobs: list[JobPosting] = []
        for rec in raw:
            if not isinstance(rec, dict):
                continue

            title = rec.get("name")
            if not title:
                continue

            job_url = ""
            pos = rec.get("positionUrl")
            if pos:
                u = build_url(base, pos)
                if u:
                    job_url = u

            if not job_url:
                continue

            try:
                jobs.append(
                    JobPosting(
                        spider=self.name,
                        company="Microsoft",
                        title=str(title).strip(),
                        url=job_url,  # type: ignore
                        location=rec.get("location") or " | ".join(rec.get("locations", [])),
                        external_id=str(rec.get("displayJobId") or rec.get("id") or ""),
                        description=rec.get("description"),
                        posted_at=parse_datetime(rec.get("postedTs") or rec.get("postedDate")),
                    )
                )
            except Exception as e:
                logger.debug("Failed to map microsoft record: %s", e)

        return jobs


# Backwards-compatible name used by dynamic loader
Spider = MicrosoftSpider
