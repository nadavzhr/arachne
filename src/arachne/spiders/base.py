"""Spider interface definitions for Arachne."""

from __future__ import annotations

import dataclasses
import json
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any

from arachne.clients.base import FetchContext
from arachne.config.loader import SpiderConfig
from arachne.config.profile import SearchProfile
from arachne.logging import spider_logger
from arachne.models.job import JobPosting
from arachne.models.schema import Filters, JobSearchCriteria

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _matches_any(keywords: Sequence[str], tokens: set[str]) -> bool:
    for keyword in keywords:
        if not keyword:
            continue
        key_tokens = _tokenize(keyword)
        if key_tokens and key_tokens.issubset(tokens):
            return True
    return False


def _normalize_keywords(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]


@dataclasses.dataclass(frozen=True)
class SpiderResult:
    """Container for the results of a spider execution."""

    raw: Any
    normalized: list[JobPosting]
    filtered: list[JobPosting]
    normalization_error: Exception | None = None


class Spider(ABC):
    """Abstract base class for all Arachne job spiders."""

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize the spider with its configuration.

        Args:
            cfg: The configuration object for this spider.
        """
        self.cfg = cfg
        self.name = cfg.name or self.__class__.__name__.removesuffix("Spider").lower()
        self.log = spider_logger(self.name, self.__class__.__module__)

    async def run(self, ctx: FetchContext, profile: SearchProfile) -> SpiderResult:
        """The unified pipeline: fetch -> normalize -> dedupe -> filter."""
        criteria = profile.get_search_for(self.name)
        filters = profile.get_filters_for(self.name)

        self.log.info("fetch started")
        try:
            raw_data = await self.fetch(ctx, criteria)
        finally:
            self.log.info("fetch finished")

        if ctx.debug and ctx.data_dir:
            self._save_raw_debug(raw_data, ctx.data_dir)

        normalize_error: Exception | None = None
        try:
            jobs = self.normalize(raw_data)
        except Exception as exc:
            normalize_error = exc
            jobs = []
            self.log.error(f"Normalization error: {exc}")

        jobs = self._ensure_spider_tags(jobs)
        jobs = self._dedupe(jobs)
        filtered_jobs = self._apply_filters(jobs, filters)

        return SpiderResult(
            raw=raw_data,
            normalized=jobs,
            filtered=filtered_jobs,
            normalization_error=normalize_error,
        )

    def _save_raw_debug(self, raw_data: Any, data_dir: Any) -> None:
        """Save raw JSON payload for debugging."""
        try:
            debug_dir = data_dir / "debug"
            debug_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = debug_dir / f"{self.name}_{timestamp}.json"
            filepath.write_text(json.dumps(raw_data, indent=2), encoding="utf-8")
            self.log.info(f"Saved raw debug payload to {filepath}")
        except Exception as e:
            self.log.error(f"Failed to save raw debug payload: {e}")

    def _ensure_spider_tags(self, jobs: list[JobPosting]) -> list[JobPosting]:
        normalized: list[JobPosting] = []
        for job in jobs:
            if job.spider == self.name:
                normalized.append(job)
            else:
                normalized.append(job.model_copy(update={"spider": self.name}))
        return normalized

    def _dedupe(self, jobs: list[JobPosting]) -> list[JobPosting]:
        seen: set[str] = set()
        unique: list[JobPosting] = []
        for job in jobs:
            key = str(job.external_id)
            if key in seen:
                continue
            seen.add(key)
            unique.append(job)
        return unique

    def _apply_filters(
        self, jobs: Sequence[JobPosting], filters: Filters | None
    ) -> list[JobPosting]:
        if filters is None:
            return list(jobs)

        include_keywords = _normalize_keywords(filters.include_keywords)
        exclude_keywords = _normalize_keywords(filters.exclude_keywords)
        location_keywords = _normalize_keywords(filters.locations)

        filtered: list[JobPosting] = []
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

    @abstractmethod
    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> Any:
        """Fetch raw payload from the provider.

        Args:
            ctx: The fetch context containing shared clients.
            search: The search criteria to apply.

        Returns:
            Any: The raw data retrieved from the provider (e.g., JSON dict or list).

        Raises:
            Exception: If the fetch operation fails.
        """

    @abstractmethod
    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw payload into a list of JobPosting models.

        Args:
            raw: The raw data retrieved via the fetch method.

        Returns:
            list[JobPosting]: A list of normalized job postings.
        """
