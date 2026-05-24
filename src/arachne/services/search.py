"""Search service for executing the fetch/normalize/filter pipeline."""

from __future__ import annotations

import dataclasses
from typing import Any

import httpx

import arachne.filters
import arachne.models.job
import arachne.models.schema
import arachne.sources.base


@dataclasses.dataclass(frozen=True)
class SearchResult:
    raw: Any
    normalized: list[arachne.models.job.JobPosting]
    filtered: list[arachne.models.job.JobPosting]
    normalization_error: Exception | None = None


def _ensure_source(
    source: str,
    jobs: list[arachne.models.job.JobPosting],
) -> list[arachne.models.job.JobPosting]:
    normalized: list[arachne.models.job.JobPosting] = []
    for job in jobs:
        if job.source == source:
            normalized.append(job)
        else:
            normalized.append(job.model_copy(update={"source": source}))
    return normalized


async def execute_search(
    source: arachne.sources.base.Source,
    client: httpx.AsyncClient,
    search: arachne.models.schema.JobSearchCriteria,
    filters: arachne.models.schema.Filters | None = None,
) -> SearchResult:
    raw = await source.fetch(client, search)

    normalize_error: Exception | None = None
    try:
        normalized = source.normalize(raw)
    except Exception as exc:
        normalize_error = exc
        normalized = []

    normalized = _ensure_source(source.name, normalized)
    filtered = arachne.filters.apply_filters(normalized, filters)

    return SearchResult(
        raw=raw,
        normalized=normalized,
        filtered=filtered,
        normalization_error=normalize_error,
    )
