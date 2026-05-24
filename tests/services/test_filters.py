from pydantic import HttpUrl

import arachne.models.job
import arachne.services.filters
from arachne.models.schema import Filters


def _job(
    title: str,
    description: str | None = None,
    location: str | None = None,
) -> arachne.models.job.JobPosting:
    return arachne.models.job.JobPosting(
        source="test",
        title=title,
        url=HttpUrl("https://example.com/jobs/1"),
        description=description,
        location=location,
    )


def test_include_keywords_any_match() -> None:
    filters = Filters(include_keywords=["software engineer"])
    jobs = [_job("Software Engineer", "backend"), _job("Product Manager")]

    result = arachne.services.filters.apply_filters(jobs, filters)

    assert len(result) == 1
    assert result[0].title == "Software Engineer"


def test_exclude_keywords_drop_match() -> None:
    filters = Filters(exclude_keywords=["intern"])
    jobs = [_job("Software Engineer"), _job("Software Intern")]

    result = arachne.services.filters.apply_filters(jobs, filters)

    assert [job.title for job in result] == ["Software Engineer"]


def test_location_filter_matches_tokens() -> None:
    filters = Filters(locations=["Remote"])
    jobs = [_job("Software Engineer", location="Remote - US"), _job("Onsite", location="NY")]

    result = arachne.services.filters.apply_filters(jobs, filters)

    assert [job.title for job in result] == ["Software Engineer"]
