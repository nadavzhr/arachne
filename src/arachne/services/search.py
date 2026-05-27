"""Search service for executing the fetch/normalize/filter pipeline."""

from __future__ import annotations

import dataclasses
from typing import Any

import arachne.clients.base
import arachne.models.job
import arachne.models.schema
import arachne.services.filters
import arachne.spiders.base


@dataclasses.dataclass(frozen=True)
class SearchResult:
    """Container for the results of a spider execution.

    Attributes:
        raw: The raw data fetched from the provider.
        normalized: List of job postings normalized to the internal schema.
        filtered: List of job postings after applying filters.
        normalization_error: Any exception encountered during normalization.
    """

    raw: Any
    normalized: list[arachne.models.job.JobPosting]
    filtered: list[arachne.models.job.JobPosting]
    normalization_error: Exception | None = None


def _ensure_spider(
    spider: str,
    jobs: list[arachne.models.job.JobPosting],
) -> list[arachne.models.job.JobPosting]:
    """Ensure all job postings are tagged with the correct spider name.

    Args:
        spider: The name of the spider.
        jobs: List of job postings to verify.

    Returns:
        list[arachne.models.job.JobPosting]: Updated list of job postings.
    """
    normalized: list[arachne.models.job.JobPosting] = []
    for job in jobs:
        if job.spider == spider:
            normalized.append(job)
        else:
            normalized.append(job.model_copy(update={"spider": spider}))
    return normalized


async def execute_search(
    spider: arachne.spiders.base.Spider,
    ctx: arachne.clients.base.FetchContext,
    search: arachne.models.schema.JobSearchCriteria,
    filters: arachne.models.schema.Filters | None = None,
) -> SearchResult:
    """Execute the full search pipeline for a spider.

    Fetches raw data, normalizes it, and applies filters.

    Args:
        spider: The spider instance to use.
        ctx: The fetch context containing shared clients.
        search: The search criteria to apply.

        filters: Optional filters to apply after normalization.

    Returns:
        SearchResult: The aggregated results of the search pipeline.
    """
    raw = await spider.fetch(ctx, search)

    normalize_error: Exception | None = None
    try:
        normalized = spider.normalize(raw)
    except Exception as exc:
        normalize_error = exc
        normalized = []

    normalized = _ensure_spider(spider.name, normalized)
    filtered = arachne.services.filters.apply_filters(normalized, filters)

    return SearchResult(
        raw=raw,
        normalized=normalized,
        filtered=filtered,
        normalization_error=normalize_error,
    )
