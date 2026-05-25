"""Service for orchestrating the scraping workflow."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from arachne.clients.base import FetchContext
from arachne.services import search as search_service
from arachne.spiders import get_spider_class

if TYPE_CHECKING:
    import httpx

    from arachne.clients.playwright import PlaywrightManager
    from arachne.config.loader import SpiderConfig
    from arachne.config.profile import SearchProfile
    from arachne.storage.base import JobStorage

logger = logging.getLogger(__name__)


class ScraperService:
    """Service to coordinate the multi-spider scraping process.

    This service handles concurrency and persistence for multiple spiders
    running against a specific search profile.
    """

    def __init__(
        self,
        storage: JobStorage,
        client: httpx.AsyncClient,
        browser: PlaywrightManager,
        concurrency: int = 1,
    ) -> None:
        """Initialize the scraper service.

        Args:
            storage: The storage backend to persist results.
            client: The HTTP client to use for requests.
            browser: The Playwright manager for browser-based scraping.
            concurrency: Maximum number of spiders to run in parallel.
        """
        self.storage = storage
        self.client = client
        self.browser = browser
        self.semaphore = asyncio.Semaphore(max(1, concurrency))

    async def run_spider(
        self,
        name: str,
        cfg: SpiderConfig,
        profile: SearchProfile,
    ) -> search_service.SearchResult:
        """Execute search for a single spider and persist results.

        Args:
            name: The name of the spider to run.
            cfg: Configuration for the spider.
            profile: The search profile containing criteria and filters.

        Returns:
            search_service.SearchResult: The result of the search,
                including raw and normalized data.
        """
        SpiderCls = get_spider_class(name)
        spider = SpiderCls(cfg)

        ctx = FetchContext(http=self.client, browser=self.browser)

        async with self.semaphore:
            spider.log.info("fetch started")
            try:
                result = await search_service.execute_search(
                    spider=spider,
                    ctx=ctx,
                    search=profile.get_search_for(name),
                    filters=profile.get_filters_for(name),
                )
            finally:
                spider.log.info("fetch finished")

            # Persist results
            self.storage.save_raw(name, result.raw)
            self.storage.save_jobs(name, result.normalized, category="unfiltered")
            self.storage.save_jobs(name, result.filtered)

            return result

    async def run_profile(
        self,
        spiders_config: dict[str, SpiderConfig],
        profile: SearchProfile,
    ) -> dict[str, search_service.SearchResult | BaseException]:
        """Run scraping for all enabled spiders in a profile.

        Args:
            spiders_config: Dictionary mapping spider names to their configurations.
            profile: The search profile to execute.

        Returns:
            dict[str, search_service.SearchResult | BaseException]: A mapping of spider names
                to their search results or any exceptions encountered.
        """
        tasks: dict[str, asyncio.Task[search_service.SearchResult]] = {}

        await self.browser.start()
        try:
            for name, cfg in spiders_config.items():
                if not cfg.enabled:
                    continue
                tasks[name] = asyncio.create_task(self.run_spider(name, cfg, profile))

            if not tasks:
                return {}

            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        finally:
            await self.browser.stop()

        final_results: dict[str, search_service.SearchResult | BaseException] = {}
        for name, result in zip(tasks.keys(), results, strict=True):
            final_results[name] = result

        return final_results
