"""Meta Careers spider implementation using GraphQL replay via curl.

Note on HTTP Clients:
This spider intentionally shells out to `curl` via a subprocess instead of
using the shared `httpx` client. Meta heavily rate-limits or blocks standard
Python HTTP libraries with 429 Too Many Requests errors. Using `curl` allows
us to bypass these basic anti-bot protections.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import TYPE_CHECKING, Any

from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.meta import utils
from arachne.spiders.meta.params import MetaParams

if TYPE_CHECKING:
    from arachne.clients.base import FetchContext

logger = logging.getLogger(__name__)

META_JOBS_URL = "https://www.metacareers.com/jobs"
META_GRAPHQL_URL = "https://www.metacareers.com/graphql"
META_QUERY_NAME = "CareersJobSearchResultsDataQuery"
DEFAULT_DOC_ID = "29615178951461218"

LSD_PATTERN = re.compile(r'"LSD",\[\],\{"token":"([^"]+)"\}')


class MetaSpider(BaseSpider):
    """Spider for Meta Careers portal using direct GraphQL replay via curl."""

    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> list[dict[str, Any]]:
        """Fetch job listings from Meta Careers via GraphQL using curl for bypass."""

        ua = (
            self.cfg.user_agent
            or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        cookie_file = f"/tmp/meta_cookies_{self.name}.txt"

        # 1. Fetch base page to get LSD token and set cookies
        cmd_get = ["curl", "-s", "-L", "-c", cookie_file, "-H", f"User-Agent: {ua}", META_JOBS_URL]

        proc_get = await asyncio.create_subprocess_exec(
            *cmd_get, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_get, stderr_get = await proc_get.communicate()

        if proc_get.returncode != 0:
            self.log.error("curl get failed: %s", stderr_get.decode())
            return []

        html = stdout_get.decode("utf-8", errors="ignore")
        match = LSD_PATTERN.search(html)
        lsd_token = match.group(1) if match else None

        if not lsd_token:
            self.log.error("failed to extract LSD token using curl")
            return []

        # 2. Prepare GraphQL request
        params = MetaParams.from_search(search)
        variables = params.to_variables()

        payload = {
            "lsd": lsd_token,
            "doc_id": params.doc_id or DEFAULT_DOC_ID,
            "variables": json.dumps(variables),
            "fb_api_req_friendly_name": META_QUERY_NAME,
            "fb_api_caller_class": "RelayModern",
            "av": "0",
            "__user": "0",
            "__a": "1",
        }

        from urllib.parse import urlencode

        # 3. Send GraphQL request
        cmd_post = [
            "curl",
            "-s",
            "-X",
            "POST",
            "-b",
            cookie_file,
            "-H",
            f"User-Agent: {ua}",
            "-H",
            "Origin: https://www.metacareers.com",
            "-H",
            f"Referer: {self.cfg.url or META_JOBS_URL}",
            "-H",
            "Content-Type: application/x-www-form-urlencoded",
            "-H",
            f"X-Fb-Lsd: {lsd_token}",
            "-H",
            f"X-Fb-Friendly-Name: {META_QUERY_NAME}",
            "-H",
            "X-Asbd-Id: 129477",
            "-H",
            "Sec-Fetch-Dest: empty",
            "-H",
            "Sec-Fetch-Mode: cors",
            "-H",
            "Sec-Fetch-Site: same-origin",
            "--data-raw",
            urlencode(payload),
            META_GRAPHQL_URL,
        ]

        proc_post = await asyncio.create_subprocess_exec(
            *cmd_post, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout_post, stderr_post = await proc_post.communicate()

        if proc_post.returncode != 0:
            self.log.error("curl post failed: %s", stderr_post.decode())
            return []

        return utils.parse_graphql_text(stdout_post.decode("utf-8", errors="ignore"))

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw Meta GraphQL payloads into JobPosting models."""
        if not isinstance(raw, list):
            return []

        all_jobs: list[JobPosting] = []
        for payload in raw:
            if not isinstance(payload, dict):
                continue

            # Navigate to the job list in the response
            data = payload.get("data", {})
            job_container = data.get("job_search_with_featured_jobs", {})

            items = job_container.get("all_jobs", [])

            for item in items:
                job_id = item.get("id")
                title = item.get("title")
                if not title or not job_id:
                    continue

                locations = item.get("locations", [])

                all_jobs.append(
                    JobPosting(
                        spider=self.name,
                        company="Meta",
                        title=title,
                        url=f"{META_JOBS_URL}/{job_id}/",  # type: ignore
                        location=", ".join(locations) if locations else "Unknown",
                        external_id=job_id,
                    )
                )

        return self._dedupe_jobs(all_jobs)

    def _dedupe_jobs(self, records: list[JobPosting]) -> list[JobPosting]:
        seen: set[str] = set()
        unique: list[JobPosting] = []
        for r in records:
            key = r.external_id or str(r.url) or r.title
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique


Spider = MetaSpider
