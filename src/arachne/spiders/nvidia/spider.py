"""NVIDIA spider implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from arachne.clients.http import fetch_paginated_json
from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.nvidia.params import NvidiaParams
from arachne.utils.normalization import build_url, parse_datetime

if TYPE_CHECKING:
    from arachne.clients.base import FetchContext

logger = logging.getLogger(__name__)


class NvidiaSpider(BaseSpider):
    """Spider for NVIDIA Careers portal.

    This spider uses NVIDIA's job search API (Workday-based) to fetch
    job listings. It supports pagination and maps the response to
    the standard JobPosting model.
    """

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize NVIDIA spider.

        Args:
            cfg: Spider configuration.
        """
        super().__init__(cfg)

    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> Any:
        """Fetch job listings from NVIDIA Careers.

        Args:
            ctx: The fetch context containing shared clients.
            search: Standard search criteria.

        Returns:
            Any: Raw JSON response data (list of job records).
        """
        params = NvidiaParams.from_search(search)
        self.log.info("paginated http request started: url=%s", self.cfg.url)
        return await fetch_paginated_json(
            ctx.http, self.cfg.url, params=params.to_query(), headers=self.cfg.headers
        )

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Normalize raw NVIDIA job data into JobPosting models.

        Args:
            raw: Raw JSON data from fetch().

        Returns:
            list[JobPosting]: A list of normalized job postings.
        """
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

            location_str = None
            locs = rec.get("standardizedLocations") or rec.get("locations")
            if isinstance(locs, list) and locs:
                location_str = " | ".join(str(x) for x in locs)

            try:
                jobs.append(
                    JobPosting(
                        spider=self.name,
                        company="Nvidia",
                        title=str(title).strip(),
                        url=job_url,  # type: ignore
                        location=location_str,
                        external_id=str(rec.get("displayJobId") or rec.get("id") or ""),
                        description=rec.get("description"),
                        posted_at=parse_datetime(rec.get("postedTs")),
                    )
                )
            except Exception as e:
                logger.debug("Failed to map nvidia record: %s", e)

        return jobs


# Backwards-compatible name used by dynamic loader
Spider = NvidiaSpider
