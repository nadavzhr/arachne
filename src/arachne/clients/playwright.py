"""Playwright client for browser-based scraping."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

logger = logging.getLogger(__name__)


class PlaywrightManager:
    """Manages the lifecycle of a Playwright browser instance.

    This class allows for a single browser process to be shared across
    multiple scraping tasks, creating isolated contexts for each.
    """

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Start the Playwright process and launch the browser."""
        if self._playwright:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        logger.debug("Playwright browser launched")

    async def stop(self) -> None:
        """Stop the browser and Playwright process."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None
        logger.debug("Playwright browser stopped")

    @asynccontextmanager
    async def new_page(self, user_agent: str | None = None) -> AsyncIterator[Page]:
        """Provide a managed Playwright page within an isolated context.

        Args:
            user_agent: Optional custom User-Agent string.

        Yields:
            AsyncIterator[Page]: A Playwright Page object.
        """
        if not self._browser:
            raise RuntimeError("PlaywrightManager not started. Call start() first.")

        ua = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )

        context: BrowserContext = await self._browser.new_context(user_agent=ua)
        page = await context.new_page()
        try:
            yield page
        finally:
            await page.close()
            await context.close()


@asynccontextmanager
async def browser_session(
    user_agent: str | None = None,
    headless: bool = True,
) -> AsyncIterator[Page]:
    """Legacy helper for standalone browser sessions.

    Prefer using PlaywrightManager for shared browser lifecycles.
    """
    manager = PlaywrightManager(headless=headless)
    await manager.start()
    try:
        async with manager.new_page(user_agent=user_agent) as page:
            yield page
    finally:
        await manager.stop()
