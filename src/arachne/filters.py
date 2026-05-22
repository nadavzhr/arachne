"""Shared filtering utilities for normalized job postings."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

import arachne.config.loader
import arachne.models.job

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _keyword_tokens(keyword: str) -> set[str]:
    return _tokenize(keyword)


def _matches_any(keywords: Sequence[str], tokens: set[str]) -> bool:
    for keyword in keywords:
        if not keyword:
            continue
        key_tokens = _keyword_tokens(keyword)
        if key_tokens and key_tokens.issubset(tokens):
            return True
    return False


def _normalize_keywords(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]


def apply_filters(
    jobs: Sequence[arachne.models.job.JobPosting],
    filters: arachne.config.loader.Filters | None,
) -> list[arachne.models.job.JobPosting]:
    """Apply include/exclude/location filters to normalized jobs."""
    if filters is None:
        return list(jobs)

    include_keywords = _normalize_keywords(filters.include_keywords)
    exclude_keywords = _normalize_keywords(filters.exclude_keywords)
    location_keywords = _normalize_keywords(filters.locations)

    filtered: list[arachne.models.job.JobPosting] = []
    for job in jobs:
        text_parts = [job.title]
        if job.description:
            text_parts.append(job.description)
        text_tokens = _tokenize(" ".join(text_parts))

        if include_keywords and not _matches_any(include_keywords, text_tokens):
            continue
        if exclude_keywords and _matches_any(exclude_keywords, text_tokens):
            continue

        if location_keywords:
            if not job.location:
                continue
            location_tokens = _tokenize(job.location)
            if not _matches_any(location_keywords, location_tokens):
                continue

        filtered.append(job)

    return filtered
