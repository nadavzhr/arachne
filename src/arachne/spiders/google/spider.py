"""Google Careers spider implementation using batchexecute API replay."""

from __future__ import annotations

import itertools
import json
import logging
import typing

from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.google import utils
from arachne.spiders.google.params import GoogleParams

if typing.TYPE_CHECKING:
    import arachne.clients.base

logger = logging.getLogger(__name__)

# r06xKb is the method name for the main job search endpoint,
# but it may change in the future.
# This is based on current observations and may need updates if Google changes their API.
BATCHEXECUTE_METHOD = "r06xKb"
DEFAULT_PAGE_INDEX = 1

IDX_EXTERNAL_ID = 0
IDX_TITLE = 1
IDX_APPLY_URL = 2
IDX_RESPONSIBILITIES = 3
IDX_QUALIFICATIONS = 4
IDX_COMPANY = 7
IDX_LOCATIONS = 9
IDX_DESCRIPTION = 10


class GoogleSpider(BaseSpider):
    """Spider for Google Careers using the batchexecute endpoint."""

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize Google spider.

        Args:
            cfg: Spider configuration.
        """
        super().__init__(cfg)

    async def fetch(
        self,
        ctx: arachne.clients.base.FetchContext,
        search: JobSearchCriteria,
    ) -> list[typing.Any]:
        """Fetch raw job data from Google Careers batchexecute.

        Args:
            ctx: The fetch context containing shared clients.
            search: Standard search criteria.

        Returns:
            list[typing.Any]: List of raw response payloads for each page.
        """
        params = GoogleParams.from_search(search)
        all_pages: list[typing.Any] = []

        headers = dict(self.cfg.headers or {})
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        if self.cfg.user_agent:
            headers["User-Agent"] = self.cfg.user_agent

        for page in itertools.count(1):  # Fetch until no more jobs are found
            inner_params = params.to_batchexecute_inner_params(
                query=search.title,
                page_index=page,
            )
            f_req: list[list[list[typing.Any]]] = [
                [[BATCHEXECUTE_METHOD, json.dumps([inner_params]), None, "3"]]
            ]
            payload = {"f.req": json.dumps(f_req)}

            self.log.info("http request started: url=%s page=%d", self.cfg.url, page)
            response = await ctx.http.post(self.cfg.url, data=payload, headers=headers)
            response.raise_for_status()

            raw_text = response.text
            batchexecute, payload_json = utils.parse_batchexecute_text(raw_text)

            if not payload_json or not payload_json[0]:
                self.log.info("pagination finished: no more jobs found at page %d", page)
                break

            all_pages.append(
                {
                    "raw_text": raw_text,
                    "batchexecute": batchexecute,
                    "payload": payload_json,
                    "page": page,
                }
            )

            # If we got fewer than 10 jobs, it's likely the last page
            if len(payload_json[0]) < 10:
                break

        return all_pages

    def normalize(self, raw: typing.Any) -> list[JobPosting]:
        """Normalize raw Google data into JobPosting models.

        Args:
            raw: Raw data from fetch() (list of page payloads).

        Returns:
            list[JobPosting]: Normalized job postings.
        """
        raw_list = raw if isinstance(raw, list) else [raw]
        all_jobs: list[JobPosting] = []

        for page_data in raw_list:
            payload = utils.extract_payload(page_data)
            if not payload or not payload[0]:
                continue

            for rec in payload[0]:
                if not isinstance(rec, list):
                    continue
                record = rec
                if len(record) <= IDX_DESCRIPTION:
                    continue

                title_value = record[IDX_TITLE]
                url_value = record[IDX_APPLY_URL]
                if not isinstance(title_value, str) or not title_value.strip():
                    continue
                if not isinstance(url_value, str) or not url_value.strip():
                    continue

                title = title_value.strip()
                url = url_value.strip()

                company_value = record[IDX_COMPANY]
                company = (
                    company_value.strip()
                    if isinstance(company_value, str) and company_value.strip()
                    else "Google"
                )
                location = utils.extract_locations(record[IDX_LOCATIONS])
                responsibilities_html = utils.extract_html_block(record[IDX_RESPONSIBILITIES])
                description_html = utils.extract_html_block(record[IDX_DESCRIPTION])
                qualifications_html = utils.extract_html_block(record[IDX_QUALIFICATIONS])
                description_text = utils.strip_html(
                    " ".join(
                        part
                        for part in [description_html, responsibilities_html, qualifications_html]
                        if isinstance(part, str) and part.strip()
                    )
                )

                try:
                    all_jobs.append(
                        JobPosting(
                            spider=self.name,
                            company=company,
                            title=title,
                            url=url,  # type: ignore[arg-type]
                            location=location,
                            external_id=str(record[IDX_EXTERNAL_ID]),
                            description=description_text,
                        )
                    )
                except Exception as exc:
                    logger.debug("Failed to map google record: %s", exc)

        return all_jobs


# Backwards-compatible name used by dynamic loader
Spider = GoogleSpider
