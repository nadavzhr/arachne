"""Search service for executing the fetch/normalize/filter pipeline."""

from __future__ import annotations

import dataclasses
from typing import Any

import httpx

import arachne.models.job
import arachne.models.schema
import arachne.services.filters
import arachne.spiders.base


@dataclasses.dataclass(frozen=True)
class SearchResult:
    raw: Any
    normalized: list[arachne.models.job.JobPosting]
    filtered: list[arachne.models.job.JobPosting]
    normalization_error: Exception | None = None


def _ensure_spider(
    spider: str,
    jobs: list[arachne.models.job.JobPosting],
) -> list[arachne.models.job.JobPosting]:
    normalized: list[arachne.models.job.JobPosting] = []
    for job in jobs:
        if job.spider == spider:
            normalized.append(job)
        else:
            normalized.append(job.model_copy(update={"spider": spider}))
    return normalized


async def execute_search(
    spider: arachne.spiders.base.Spider,
    client: httpx.AsyncClient,
    search: arachne.models.schema.JobSearchCriteria,
    filters: arachne.models.schema.Filters | None = None,
) -> SearchResult:
    raw = await spider.fetch(client, search)

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
