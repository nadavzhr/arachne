"""Google Careers source implementation using Playwright DOM scraping.

Scrapes job listings from Google's careers page by rendering and extracting
job card elements. Returns raw job data; normalization converts to JobPosting models.
"""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urljoin

from httpx import AsyncClient
from playwright.async_api import Locator

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.google.params import GoogleParams
from arachne.sources.playwright import PlaywrightSource
from arachne.sources.query import build_query_string
from arachne.utils.normalization import normalize_records

# Configuration Constants
BASE_URL = "https://www.google.com/about/careers/applications/"
DEFAULT_TIMEOUT_MS = 10000

# String Cleansing Constants
CLEANUP_CHARS = " ;|•,-"
ICON_ARTIFACT = "place"


class GoogleSource(PlaywrightSource):
    """Scrape Google Careers using Playwright DOM scraping.

    Navigates to the Google Careers page, waits for job cards to render,
    extracts job details (title, location, URL) from each card.
    """

    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)
        self.params = GoogleParams.from_search(cfg.search)

    def _build_search_url(self) -> str:
        return f"{BASE_URL}jobs/results?{build_query_string(self.params.to_query())}"

    async def _parse_job_card(self, card: Locator) -> dict[str, str]:
        """Extract details cleanly from a single job card element."""
        try:
            title_el = card.locator("h3")
            title = await title_el.inner_text() if await title_el.count() else "Unknown Title"

            anchor = card.locator("a").first
            href = await anchor.get_attribute("href") if await anchor.count() else None
            job_url = urljoin(BASE_URL, href.split("?")[0]) if href else "Link not found"

            loc_el = card.locator(
                '[aria-label*="Location"], .gc-job-card__location, span:has-text("Israel")'
            ).first
            raw_location = await loc_el.inner_text() if await loc_el.count() else "Israel"

            cleaned_lines = [
                line.strip(CLEANUP_CHARS)
                for line in raw_location.replace(ICON_ARTIFACT, "").split("\n")
                if line.strip()
            ]
            location = ", ".join(cleaned_lines)

            return {"title": title.strip(), "location": location.strip(), "url": job_url}
        except Exception as exc:
            self.log.warning("job card parse failed: %s", exc)
            return {"title": "Error Parsing", "location": "Error", "url": "Error"}

    async def fetch(self, client: AsyncClient) -> list[dict[str, str]]:
        """Fetch jobs by rendering Google Careers page and scraping job cards."""
        try:
            await self._launch_browser()

            assert self.page is not None, "Page not initialized"
            search_url = self._build_search_url()
            self.log.info("search page opened: url=%s", search_url)
            await self.page.goto(search_url, wait_until="load")

            try:
                await self.page.wait_for_selector("li:has(h3)", timeout=DEFAULT_TIMEOUT_MS)
            except Exception:
                self.log.warning("job cards wait timed out: timeout_ms=%d", DEFAULT_TIMEOUT_MS)
                return []

            job_cards = await self.page.locator("li:has(h3)").all()
            self.log.info("job cards found: count=%d", len(job_cards))

            tasks = [self._parse_job_card(card) for card in job_cards]
            extracted_jobs = await asyncio.gather(*tasks)

            # Filter out parsing errors
            extracted_jobs = [j for j in extracted_jobs if j["title"] != "Error Parsing"]
            self.log.info("job cards parsed: count=%d", len(extracted_jobs))

            return extracted_jobs

        finally:
            await self._close_browser()

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw job data into JobPosting models."""
        if not isinstance(raw, list):
            return []
        return normalize_records("google", raw)


# Backwards-compatible name used by dynamic loader
Source = GoogleSource
