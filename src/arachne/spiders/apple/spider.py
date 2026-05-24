"""Apple Careers spider — public search API implementation."""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import TypedDict

import httpx
from pydantic import BaseModel, Field

import arachne.config.loader
import arachne.models.job
import arachne.spiders.base
import arachne.utils.normalization
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.apple.params import AppleParams
from arachne.utils.type_casts import as_dict, as_list

_BASE_URL = "https://jobs.apple.com"
_API_URL = f"{_BASE_URL}/api/v1/search"
_CSRF_URL = f"{_BASE_URL}/api/v1/CSRFToken"
_DATE_FORMAT = {"longDate": "MMMM D, YYYY", "mediumDate": "MMM D, YYYY"}
_PAGE_SIZE = 20
_MAX_PAGES = 10_000
_DEFAULT_LOCALE = "en_US"


# ---------------------------------------------------------------------------
# API payload / dump shapes
# ---------------------------------------------------------------------------


class _SearchFilters(TypedDict, total=False):
    keywords: list[str]
    locations: list[str]


class _SearchPayload(TypedDict):
    query: str
    filters: _SearchFilters
    page: int
    locale: str
    sort: str
    format: dict[str, str]


class _PageDump(TypedDict):
    page: int
    request: _SearchPayload
    status: int
    response: object  # raw JSON — unknown shape until validated


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class _Location(BaseModel):
    name: str | None = None


class _Team(BaseModel):
    teamCode: str | None = None


class _SearchResult(BaseModel):
    reqId: str | None = None
    id: str | None = None
    positionId: str | None = None
    jobPositionId: str | None = None
    postingTitle: str | None = None
    transformedPostingTitle: str | None = None
    team: _Team | None = None
    locations: list[_Location] = Field(default_factory=list[_Location])
    jobSummary: str | None = None
    postingDate: str | None = None
    postDateInGMT: str | None = None

    @property
    def best_id(self) -> str | None:
        return self.reqId or self.id or self.positionId or self.jobPositionId

    @property
    def first_location(self) -> str | None:
        return next(
            (loc.name.strip() for loc in self.locations if loc.name and loc.name.strip()),
            None,
        )

    def build_url(self, language: str, base_url: str = _BASE_URL) -> str:
        slug = (self.transformedPostingTitle or self.postingTitle or "").strip()
        url = f"{base_url}/{language}/details/{self.best_id}/{slug}"
        if self.team and self.team.teamCode:
            url += f"?team={self.team.teamCode}"
        return url


# ---------------------------------------------------------------------------
# Spider
# ---------------------------------------------------------------------------


class AppleSpider(arachne.spiders.base.Spider):
    """Scrape Apple Careers via the public search API."""

    def __init__(self, cfg: arachne.config.loader.SpiderConfig) -> None:
        super().__init__(cfg)

    # region Public interface

    async def fetch(self, client: httpx.AsyncClient, search: JobSearchCriteria) -> list[_PageDump]:
        self.params = AppleParams.from_search(search)
        search_url = self._search_url()
        self.log.info("search page prepared: url=%s", search_url)

        csrf_token = await self._get_csrf_token(client)
        filters = self._build_filters()
        dumps: list[_PageDump] = []

        for page in range(1, _MAX_PAGES + 1):
            self.log.info("page fetch started: page=%d", page)
            payload = self._build_payload(page, filters)

            resp = await client.post(
                _API_URL,
                json=payload,
                headers=self._build_headers(search_url, csrf_token),
            )
            resp.raise_for_status()

            try:
                body = resp.json()
            except json.JSONDecodeError:
                self.log.warning(
                    "page response was not JSON: page=%d status=%d body=%s",
                    page,
                    resp.status_code,
                    resp.text,
                )
                body = resp.text

            dumps.append(
                {"page": page, "request": payload, "status": resp.status_code, "response": body}
            )

            body_payload = as_dict(body)
            if body_payload is None or self._has_api_error(body_payload):
                self.log.warning("pagination stopped: page=%d reason=unexpected_response", page)
                break

            results = self._parse_results(body_payload)
            self.log.info("page fetch completed: page=%d jobs=%d", page, len(results))

            if len(results) < _PAGE_SIZE:
                break

        return dumps

    def normalize(self, raw: object) -> list[arachne.models.job.JobPosting]:
        raw_pages = as_list(raw)
        if raw_pages is None:
            return []

        # Apple API can return duplicate job records across pages
        # so we dedupe by job ID before normalization.
        deduped: dict[str, arachne.models.job.JobPosting] = {}

        for page in raw_pages:
            page_payload = as_dict(page)
            if page_payload is None:
                continue
            for job in self._parse_results(page_payload.get("response", {})):
                record = self._to_record(job, self.params.language)
                if record is not None and record.external_id not in deduped:
                    # best_id maps to external_id
                    ext_id = record.external_id or ""
                    if ext_id not in deduped:
                        deduped[ext_id] = record

        return list(deduped.values())

    # region Parsing helpers

    @staticmethod
    def _parse_results(response_body: object) -> list[_SearchResult]:
        payload = as_dict(response_body)
        if payload is None:
            return []
        res_payload = as_dict(payload.get("res"))
        if res_payload is None:
            return []
        items = as_list(res_payload.get("searchResults", []))
        if items is None:
            return []
        return [_SearchResult.model_validate(item) for item in items if isinstance(item, dict)]

    def _to_record(self, job: _SearchResult, language: str) -> arachne.models.job.JobPosting | None:
        job_id = job.best_id
        title = job.postingTitle
        if not job_id or not title:
            return None

        try:
            return arachne.models.job.JobPosting(
                spider=self.name,
                company="Apple",
                title=title.strip(),
                url=job.build_url(language),  # type: ignore
                location=job.first_location,
                external_id=job_id,
                description=job.jobSummary,
                posted_at=arachne.utils.normalization.parse_datetime(
                    job.postingDate or job.postDateInGMT
                ),
            )
        except Exception as e:
            self.log.debug("Failed to map apple record: %s", e)
            return None

    @staticmethod
    def _has_api_error(body: object) -> bool:
        payload = as_dict(body)
        return payload is not None and payload.get("error") is not None

    # --- Request helpers ---

    def _search_url(self) -> str:
        location = "+".join(urllib.parse.quote(item, safe="") for item in self.params.location)
        key = urllib.parse.quote(urllib.parse.quote(self.params.key, safe=""), safe="")
        return f"{_BASE_URL}/{self.params.language}/search?location={location}&key={key}"

    def _build_filters(self) -> _SearchFilters:
        locations = [self._normalize_location(v) for v in self.params.location if v]
        filters: _SearchFilters = {}
        if self.params.key:
            filters["keywords"] = [self.params.key]
        if locations:
            filters["locations"] = locations
        return filters

    @staticmethod
    def _normalize_location(value: str) -> str:
        value = value.strip()
        if value.startswith("postLocation-"):
            return value
        suffix = value.split("-")[-1].strip().upper()
        return f"postLocation-{suffix}"

    def _build_payload(self, page: int, filters: _SearchFilters) -> _SearchPayload:
        return {
            "query": self.params.key,
            "filters": filters,
            "page": page,
            "locale": self.params.language,
            "sort": "relevance",
            "format": _DATE_FORMAT,
        }

    def _build_headers(self, referer: str, csrf_token: str | None) -> dict[str, str]:
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "browserlocale": self.params.language,
            "locale": _DEFAULT_LOCALE,
            "origin": _BASE_URL,
            "referer": referer,
        }
        if csrf_token:
            headers["x-apple-csrf-token"] = csrf_token
        return headers

    async def _get_csrf_token(self, client: httpx.AsyncClient) -> str | None:
        resp = await client.get(_CSRF_URL, headers={"accept": "*/*"})
        return str(resp.headers.get("x-apple-csrf-token")) if resp.status_code == 200 else None


Spider = AppleSpider

if __name__ == "__main__":
    import asyncio

    from arachne.logging import configure_logging, spider_logger

    async def _run_demo() -> None:
        global_cfg, spiders = arachne.config.loader.load_all(Path("config"))
        configure_logging(
            enabled=global_cfg.logging.enabled,
            directory=global_cfg.logging.directory,
            level=global_cfg.logging.level,
            central_file=global_cfg.logging.central_file,
            spider_directory=global_cfg.logging.spider_directory,
        )
        demo_log = spider_logger("apple", __name__)
        if (cfg := spiders.get("apple")) is None:
            demo_log.warning("spider config missing")
            return
        async with httpx.AsyncClient() as client:
            spider = AppleSpider(cfg)
            jobs = spider.normalize(await spider.fetch(client, JobSearchCriteria()))
        demo_log.info("demo completed: jobs=%d", len(jobs))

    asyncio.run(_run_demo())
