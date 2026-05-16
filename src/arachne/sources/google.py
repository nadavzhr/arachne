"""
THIS IS A TEMPORARY IMPLEMENATION
Google Careers page is a bit more complex than the other sources, so I'm implementing it as a temporary standalone script to test and iterate faster.
I will later refactor it so it fits the Arachne architecture and can be used as a proper source.
"""

import asyncio
import json
from urllib.parse import urljoin

from playwright.async_api import Locator, async_playwright

# Configuration Constants
BASE_URL = "https://www.google.com/about/careers/applications/"
SEARCH_URL = f"{BASE_URL}jobs/results?location=Israel&target_level=EARLY&employment_type=FULL_TIME"
DEFAULT_TIMEOUT_MS = 10000

# String Cleansing Constants
CLEANUP_CHARS = " ;|•,-"
ICON_ARTIFACT = "place"


async def parse_job_card(card: Locator) -> dict[str, str]:
    """Extracts details cleanly from a single job card element."""
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
    except Exception as e:
        print(f"Error parsing a card item: {e}")
        return {"title": "Error Parsing", "location": "Error", "url": "Error"}


async def scrape_google_careers() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        print("Opening Google Careers...")
        await page.goto(SEARCH_URL, wait_until="load")

        try:
            await page.wait_for_selector(
                "li:has(h3)", timeout=DEFAULT_TIMEOUT_MS
            )  # Wait for job cards to load
        except Exception:
            print("Timeout waiting for job elements to load.")
            await browser.close()
            return

        """
        # Note: Google Careers obviously has pagination, but junior roles are rare (sad emoji)
        # so I'm only scraping the first page for demo purposes.
        # In a real setup, we'd handle pagination properly.
        # Looking at `SEARCH_URL` pages are controlled via query params.
        # like `page=2`, `page=3`, etc.
        # We could loop through pages until no more results are found.
        """
        job_cards = await page.locator("li:has(h3)").all()  # More specific selector for job cards
        print(f"\nFound {len(job_cards)} jobs. Extracting details...\n" + "=" * 50)

        tasks = [parse_job_card(card) for card in job_cards]
        extracted_jobs = await asyncio.gather(*tasks)

        # Remove bad parsing items
        extracted_jobs = [j for j in extracted_jobs if j["title"] != "Error Parsing"]

        for idx, job in enumerate(extracted_jobs):
            log_line = (
                f"{idx + 1}. Title: {job['title']}\n"
                f"   Location: {job['location']}\n"
                f"   URL: {job['url']}\n"
                f"{'-' * 50}"
            )
            print(log_line)

        with open("google_jobs.json", "w", encoding="utf-8") as f:
            json.dump(extracted_jobs, f, indent=4, ensure_ascii=False)

        print("\nAll data successfully saved to 'google_jobs.json'")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_google_careers())
