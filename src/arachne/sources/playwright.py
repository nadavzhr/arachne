"""Shared Playwright source base class for browser-based scraping.

Provides browser lifecycle management (launch, close) and defines the interface
for sources that use Playwright for DOM scraping or API replay from within a browser context.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from httpx import AsyncClient
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from arachne.config.loader import SourceConfig
from arachne.sources.base import Source as BaseSource


class PlaywrightSource(BaseSource):
    """Base class for sources that use Playwright to scrape or interact with pages.

    Manages browser lifecycle. Subclasses implement `fetch()` to define how to extract
    data from the page, and `normalize()` to convert raw data into JobPosting models.
    """

    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def _launch_browser(self) -> None:
        """Launch Chromium browser and create a new context/page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        user_agent = self.cfg.user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        self.context = await self.browser.new_context(
            user_agent=user_agent,
        )
        self.page = await self.context.new_page()

    async def _close_browser(self) -> None:
        """Close browser and cleanup resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def fetch(self, client: AsyncClient) -> Any:
        """Fetch raw data using Playwright.

        Subclasses implement this to define browser interactions:
        - DOM scraping: navigate, wait for elements, extract
        - API replay: capture or make HTTP calls from within browser context

        Returns raw data structure (dict, list, or custom type).
        """

    @abstractmethod
    def normalize(self, raw: Any) -> Any:
        """Normalize raw data into JobPosting models."""
