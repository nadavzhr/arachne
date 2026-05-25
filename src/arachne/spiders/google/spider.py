"""Google Careers spider implementation using Playwright DOM scraping.

Scrapes job listings from Google's careers page by rendering and extracting
job card elements. Returns raw job data; normalization converts to JobPosting models.
"""

from __future__ import annotations

import asyncio
import hashlib
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from playwright.async_api import Locator

from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.google.params import GoogleParams
from arachne.utils.normalization import build_query_string

if TYPE_CHECKING:
    from arachne.clients.base import FetchContext

# Configuration Constants
BASE_URL = "https://www.google.com/about/careers/applications/"
DEFAULT_TIMEOUT_MS = 10000

# String Cleansing Constants
CLEANUP_CHARS = " ;|•,-"
ICON_ARTIFACT = "place"


class GoogleSpider(BaseSpider):
    """Scrape Google Careers using Playwright DOM scraping.

    Navigates to the Google Careers page, waits for job cards to render,
    extracts job details (title, location, URL) from each card.
    """

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize the Google spider.

        Args:
            cfg: The spider configuration.
        """
        super().__init__(cfg)

    def _build_search_url(self, params: GoogleParams) -> str:
        """Construct the full search URL with query parameters.

        Args:
            params: The Google-specific search parameters.

        Returns:
            str: The full URL for Google Careers search results.
        """
        return f"{BASE_URL}jobs/results?{build_query_string(params.to_query())}"

    async def _parse_job_card(
        self, card: Locator, preferred_locations: list[str]
    ) -> dict[str, str]:
        """Extract details cleanly from a single job card element.

        Args:
            card: The Playwright Locator for the job card.
            preferred_locations: List of locations to prioritize during extraction.

        Returns:
            dict[str, str]: Dictionary containing 'title', 'location', and 'url'.
        """
        try:
            title_el = card.locator("h3")
            title = await title_el.inner_text() if await title_el.count() else "Unknown Title"

            anchor = card.locator("a").first
            href = await anchor.get_attribute("href") if await anchor.count() else None
            job_url = urljoin(BASE_URL, href.split("?")[0]) if href else "Link not found"

            # Build a dynamic locator for location. We try standard attributes/classes first,
            # then fall back to spans containing any of our preferred location names.
            fallback_location = preferred_locations[0] if preferred_locations else "Remote"
            loc_selectors = ['[aria-label*="Location"]', ".gc-job-card__location"]
            for loc in preferred_locations:
                loc_selectors.append(f'span:has-text("{loc}")')

            loc_el = card.locator(", ".join(loc_selectors)).first
            raw_location = await loc_el.inner_text() if await loc_el.count() else fallback_location

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

    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> list[dict[str, str]]:
        """Fetch jobs by rendering Google Careers page and scraping job cards.

        Since Google does not provide a public API, this method relies on web scraping
        via Playwright. Pagination is currently not supported.

        Args:
            ctx: The fetch context containing HTTP and browser clients.
            search: The search criteria to apply.

        Returns:
            list[dict[str, str]]: List of raw job dictionaries extracted from the page.
        """
        params = GoogleParams.from_search(search)

        async with ctx.browser.new_page(user_agent=self.cfg.user_agent) as page:
            search_url = self._build_search_url(params)
            self.log.info("search page opened: url=%s", search_url)
            await page.goto(search_url, wait_until="load")

            try:
                await page.wait_for_selector("li:has(h3)", timeout=DEFAULT_TIMEOUT_MS)
            except Exception:
                self.log.warning("job cards wait timed out: timeout_ms=%d", DEFAULT_TIMEOUT_MS)
                return []

            job_cards = await page.locator("li:has(h3)").all()
            self.log.info("job cards found: count=%d", len(job_cards))

            tasks = [self._parse_job_card(card, params.location) for card in job_cards]
            extracted_jobs = await asyncio.gather(*tasks)

            # Filter out parsing errors
            extracted_jobs = [j for j in extracted_jobs if j["title"] != "Error Parsing"]
            self.log.info("job cards parsed: count=%d", len(extracted_jobs))

            return extracted_jobs

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw scraped job data into JobPosting models.

        Args:
            raw: The raw data (list of dictionaries) from fetch().

        Returns:
            list[JobPosting]: A list of normalized job postings.
        """
        if not isinstance(raw, list):
            return []

        jobs: list[JobPosting] = []
        for rec in raw:
            if not isinstance(rec, dict):
                continue

            title = rec.get("title")
            url = rec.get("url")

            if not title or not url:
                continue

            # Generate a stable unique ID by hashing the URL, since Google
            # cards don't provide an explicit external ID.
            external_id = hashlib.sha256(str(url).encode()).hexdigest()[:16]

            try:
                jobs.append(
                    JobPosting(
                        spider=self.name,
                        company="Google",
                        title=str(title).strip(),
                        url=str(url).strip(),  # type: ignore
                        location=rec.get("location"),
                        external_id=external_id,
                    )
                )
            except Exception as e:
                self.log.debug("Failed to map google record: %s", e)

        return jobs


# Backwards-compatible name used by dynamic loader
Spider = GoogleSpider
