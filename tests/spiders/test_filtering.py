from typing import Any

import pytest

from arachne.clients.base import FetchContext
from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import Filters, JobSearchCriteria, KeywordFilter
from arachne.spiders.base import Spider


class MockSpider(Spider):
    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> Any:
        return []

    def normalize(self, raw: Any) -> list[JobPosting]:
        return []


@pytest.fixture
def spider() -> MockSpider:
    return MockSpider(SpiderConfig(name="mock", url="http://example.com"))


def test_filter_title_include(spider: MockSpider) -> None:
    filters = Filters(title=KeywordFilter(include_keywords=["software"]))
    jobs = [
        JobPosting(spider="mock", title="Software Engineer", url="http://x.com/1"),  # type: ignore
        JobPosting(spider="mock", title="Hardware Engineer", url="http://x.com/2"),  # type: ignore
    ]
    filtered = spider._apply_filters(jobs, filters)
    assert len(filtered) == 1
    assert filtered[0].title == "Software Engineer"


def test_filter_title_exclude(spider: MockSpider) -> None:
    filters = Filters(title=KeywordFilter(exclude_keywords=["senior"]))
    jobs = [
        JobPosting(spider="mock", title="Software Engineer", url="http://x.com/1"),  # type: ignore
        JobPosting(spider="mock", title="Senior Software Engineer", url="http://x.com/2"),  # type: ignore
    ]
    filtered = spider._apply_filters(jobs, filters)
    assert len(filtered) == 1
    assert filtered[0].title == "Software Engineer"


def test_filter_location_exclude(spider: MockSpider) -> None:
    filters = Filters(location=KeywordFilter(exclude_keywords=["London"]))
    jobs = [
        JobPosting(spider="mock", title="Dev", url="http://x.com/1", location="Tel Aviv, Israel"),  # type: ignore
        JobPosting(spider="mock", title="Dev", url="http://x.com/2", location="London"),  # type: ignore
    ]
    filtered = spider._apply_filters(jobs, filters)
    assert len(filtered) == 1
    assert filtered[0].location == "Tel Aviv, Israel"


def test_filter_multi_field(spider: MockSpider) -> None:
    filters = Filters(
        title=KeywordFilter(include_keywords=["software"], exclude_keywords=["senior"]),
        location=KeywordFilter(include_keywords=["israel"], exclude_keywords=["London"]),
    )
    jobs = [
        JobPosting(
            spider="mock",
            title="Software Engineer",
            url="http://x.com/1",  # type: ignore
            location="Tel Aviv, Israel",
        ),  # Pass
        JobPosting(
            spider="mock",
            title="Senior Software Engineer",
            url="http://x.com/2",  # type: ignore
            location="Tel Aviv, Israel",
        ),  # Fail (exclude senior)
        JobPosting(
            spider="mock",
            title="Software Engineer",
            url="http://x.com/3",  # type: ignore
            location="London",
        ),  # Fail (exclude London)
        JobPosting(
            spider="mock",
            title="Hardware Engineer",
            url="http://x.com/4",  # type: ignore
            location="Tel Aviv, Israel",
        ),  # Fail (include software)
    ]
    filtered = spider._apply_filters(jobs, filters)
    assert len(filtered) == 1
    assert str(filtered[0].url) == "http://x.com/1"
