"""Playwright client for browser-based scraping."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger(__name__)


@asynccontextmanager
async def browser_session(
    user_agent: str | None = None,
    headless: bool = True,
) -> AsyncIterator[Page]:
    """Provide a managed Playwright browser session (page)."""
    playwright = await async_playwright().start()
    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None

    try:
        logger.debug("launching browser")
        browser = await playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )

        ua = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )

        context = await browser.new_context(user_agent=ua)
        page = await context.new_page()

        yield page

    finally:
        logger.debug("closing browser")
        if page:
            await page.close()
        if context:
            await context.close()
        if browser:
            await browser.close()
        await playwright.stop()
