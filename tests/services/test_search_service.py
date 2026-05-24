import httpx
import pytest

import arachne.config.loader
import arachne.models.job
import arachne.models.schema
import arachne.spiders.base
from arachne.services import search as search_service


class DummySpider(arachne.spiders.base.Spider):
    async def fetch(
        self,
        client: httpx.AsyncClient,
        search: arachne.models.schema.JobSearchCriteria,
    ) -> list[dict[str, str]]:
        del client, search  # Unused.
        return [
            {"id": "1", "title": "Software Engineer", "url": "https://example.com/jobs/1"},
            {"id": "2", "title": "Software Intern", "url": "https://example.com/jobs/2"},
        ]

    def normalize(self, raw: object) -> list[arachne.models.job.JobPosting]:
        if not isinstance(raw, list):
            return []

        jobs: list[arachne.models.job.JobPosting] = []
        for rec in raw:
            if not isinstance(rec, dict):
                continue
            title = rec.get("title")
            url = rec.get("url")
            if not title or not url:
                continue
            try:
                jobs.append(
                    arachne.models.job.JobPosting(
                        spider="other",
                        company="Test",
                        title=str(title),
                        url=str(url),  # type: ignore
                    )
                )
            except Exception:
                continue

        return jobs


class BrokenSpider(arachne.spiders.base.Spider):
    async def fetch(
        self,
        client: httpx.AsyncClient,
        search: arachne.models.schema.JobSearchCriteria,
    ) -> list[dict[str, str]]:
        del client, search  # Unused.
        return [{"id": "1", "title": "Software Engineer", "url": "https://example.com"}]

    def normalize(self, raw: object) -> list[arachne.models.job.JobPosting]:
        del raw  # Unused.
        raise ValueError("boom")


@pytest.mark.anyio
async def test_execute_search_applies_filters_and_spider() -> None:
    cfg = arachne.config.loader.SpiderConfig(url="https://example.com", name="dummy")
    spider = DummySpider(cfg)
    filters = arachne.models.schema.Filters(
        include_keywords=["engineer"],
        exclude_keywords=["intern"],
    )

    async with httpx.AsyncClient() as client:
        result = await search_service.execute_search(
            spider=spider,
            client=client,
            search=arachne.models.schema.JobSearchCriteria(),
            filters=filters,
        )

    assert result.raw[0]["id"] == "1"
    assert result.normalization_error is None
    assert {job.spider for job in result.normalized} == {"dummy"}
    assert [job.title for job in result.filtered] == ["Software Engineer"]


@pytest.mark.anyio
async def test_execute_search_reports_normalize_errors() -> None:
    cfg = arachne.config.loader.SpiderConfig(url="https://example.com", name="broken")
    spider = BrokenSpider(cfg)

    async with httpx.AsyncClient() as client:
        result = await search_service.execute_search(
            spider=spider,
            client=client,
            search=arachne.models.schema.JobSearchCriteria(),
        )

    assert result.normalization_error is not None
    assert result.normalized == []
    assert result.filtered == []
