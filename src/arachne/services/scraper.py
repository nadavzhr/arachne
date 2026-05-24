"""Service for orchestrating the scraping workflow."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from arachne.services import search as search_service
from arachne.sources import get_source_class

if TYPE_CHECKING:
    import httpx

    from arachne.config.loader import SourceConfig
    from arachne.config.profile import SearchProfile
    from arachne.storage.base import JobStorage

logger = logging.getLogger(__name__)


class ScraperService:
    """Service to coordinate the multi-source scraping process."""

    def __init__(
        self,
        storage: JobStorage,
        client: httpx.AsyncClient,
        concurrency: int = 1,
    ) -> None:
        self.storage = storage
        self.client = client
        self.semaphore = asyncio.Semaphore(max(1, concurrency))

    async def run_source(
        self,
        name: str,
        cfg: SourceConfig,
        profile: SearchProfile,
    ) -> search_service.SearchResult:
        """Execute search for a single source and persist results."""
        SourceCls = get_source_class(name)
        source = SourceCls(cfg)

        async with self.semaphore:
            source.log.info("fetch started")
            try:
                result = await search_service.execute_search(
                    source=source,
                    client=self.client,
                    search=profile.get_search_for(name),
                    filters=profile.get_filters_for(name),
                )
            finally:
                source.log.info("fetch finished")

            # Persist results
            self.storage.save_raw(name, result.raw)
            self.storage.save_jobs(name, result.normalized, category="unfiltered")
            self.storage.save_jobs(name, result.filtered)

            return result

    async def run_profile(
        self,
        sources_config: dict[str, SourceConfig],
        profile: SearchProfile,
    ) -> dict[str, search_service.SearchResult | BaseException]:
        """Run scraping for all enabled sources in a profile."""
        tasks: dict[str, asyncio.Task[search_service.SearchResult]] = {}

        for name, cfg in sources_config.items():
            if not cfg.enabled:
                continue
            tasks[name] = asyncio.create_task(self.run_source(name, cfg, profile))

        if not tasks:
            return {}

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        final_results: dict[str, search_service.SearchResult | BaseException] = {}
        for name, result in zip(tasks.keys(), results, strict=True):
            final_results[name] = result

        return final_results
