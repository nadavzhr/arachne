"""Service for orchestrating the scraping workflow."""

from __future__ import annotations

import asyncio
import logging

import httpx

from arachne.clients.base import FetchContext
from arachne.clients.http import ThrottledClient
from arachne.config.loader import SpiderConfig
from arachne.config.profile import SearchProfile
from arachne.spiders import get_spider_class
from arachne.spiders.base import SpiderResult
from arachne.storage.db import Database

logger = logging.getLogger(__name__)


class ScraperService:
    """Service to coordinate the multi-spider scraping process.

    This service handles concurrency and persistence for multiple spiders
    running against a specific search profile.
    """

    def __init__(
        self,
        db: Database,
        client: httpx.AsyncClient | ThrottledClient,
        concurrency: int = 1,
        debug: bool = False,
        data_dir: str | None = None,
    ) -> None:
        """Initialize the scraper service.

        Args:
            db: The database to persist results.
            client: The HTTP client to use for requests.
            concurrency: Maximum number of spiders to run in parallel.
            debug: Whether debug mode is enabled.
            data_dir: Data directory path.
        """
        self.db = db
        self.client = client
        self.semaphore = asyncio.Semaphore(max(1, concurrency))
        self.debug = debug
        self.data_dir = data_dir

    async def run_spider(
        self,
        name: str,
        cfg: SpiderConfig,
        profile: SearchProfile,
    ) -> SpiderResult:
        """Execute search for a single spider and persist results.

        Args:
            name: The name of the spider to run.
            cfg: Configuration for the spider.
            profile: The search profile containing criteria and filters.

        Returns:
            SpiderResult: The result of the search.
        """
        SpiderCls = get_spider_class(name)
        spider = SpiderCls(cfg)

        import pathlib

        data_path = pathlib.Path(self.data_dir) if self.data_dir else None
        ctx = FetchContext(http=self.client, debug=self.debug, data_dir=data_path)

        async with self.semaphore:
            try:
                result = await spider.run(ctx, profile)

                # Persist results
                self.db.save_jobs(name, result.normalized, category="unfiltered")
                self.db.save_jobs(name, result.filtered)

                # Log run stats
                status = "success"
                error_msg = None
                if result.normalization_error:
                    status = "partial_failure"
                    error_msg = f"Normalization error: {result.normalization_error}"

                self.db.log_spider_run(
                    spider=name,
                    status=status,
                    found_count=len(result.normalized),
                    filtered_count=len(result.filtered),
                    error_message=error_msg,
                )

                return result
            except Exception as exc:
                logger.error(f"Spider '{name}' failed: {exc}")
                self.db.log_spider_run(
                    spider=name,
                    status="failed",
                    error_message=str(exc),
                )
                raise

    async def run_profile(
        self,
        spiders_config: dict[str, SpiderConfig],
        profile: SearchProfile,
    ) -> dict[str, SpiderResult | BaseException]:
        """Run scraping for all enabled spiders in a profile.

        Args:
            spiders_config: Dictionary mapping spider names to their configurations.
            profile: The search profile to execute.

        Returns:
            dict[str, SpiderResult | BaseException]: A mapping of spider names
                to their search results or any exceptions encountered.
        """
        tasks: dict[str, asyncio.Task[SpiderResult]] = {}

        for name, cfg in spiders_config.items():
            if not cfg.enabled:
                continue
            tasks[name] = asyncio.create_task(self.run_spider(name, cfg, profile))

        if not tasks:
            return {}

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        final_results: dict[str, SpiderResult | BaseException] = {}
        for name, result in zip(tasks.keys(), results, strict=True):
            final_results[name] = result

        return final_results
