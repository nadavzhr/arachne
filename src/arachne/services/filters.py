"""Shared filtering utilities for normalized job postings."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

import arachne.models.job
from arachne.models.schema import Filters

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    """Split text into lowercase alphanumeric tokens.

    Args:
        text: Input string to tokenize.

    Returns:
        set[str]: Set of lowercase alphanumeric tokens.
    """
    return set(_TOKEN_RE.findall(text.lower()))


def _keyword_tokens(keyword: str) -> set[str]:
    """Convert a keyword into a set of tokens.

    Args:
        keyword: The keyword string.

    Returns:
        set[str]: Tokens derived from the keyword.
    """
    return _tokenize(keyword)


def _matches_any(keywords: Sequence[str], tokens: set[str]) -> bool:
    """Check if any of the keywords are present in the provided tokens.

    Args:
        keywords: Sequence of keywords to check.
        tokens: Set of tokens to search within.

    Returns:
        bool: True if any keyword (as a set of tokens) is a subset of the target tokens.
    """
    for keyword in keywords:
        if not keyword:
            continue
        key_tokens = _keyword_tokens(keyword)
        if key_tokens and key_tokens.issubset(tokens):
            return True
    return False


def _normalize_keywords(values: Iterable[str]) -> list[str]:
    """Clean and filter a list of keywords.

    Args:
        values: Iterable of raw keyword strings.

    Returns:
        list[str]: Cleaned list of non-empty keyword strings.
    """
    return [value.strip() for value in values if value and value.strip()]


def apply_filters(
    jobs: Sequence[arachne.models.job.JobPosting],
    filters: Filters | None,
) -> list[arachne.models.job.JobPosting]:
    """Apply include/exclude/location filters to normalized jobs.

    Args:
        jobs: Sequence of JobPosting objects to filter.
        filters: The Filters criteria to apply.

    Returns:
        list[arachne.models.job.JobPosting]: List of job postings that passed all filters.
    """
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
