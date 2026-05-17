"""Apple Careers source implementation using Playwright API replay.

Captures the UI-triggered search request from Apple Careers and replays it
against the search API. Handles pagination and deduplication across pages.
"""

from __future__ import annotations

import json
from typing import Any, cast

from httpx import AsyncClient

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.playwright import PlaywrightSource
from arachne.utils.normalization import normalize_records


APPLE_SEARCH_URL = "https://jobs.apple.com/en-il/search?location=israel-ISR&key=software%2520engineer"
APPLE_API_URL = "https://jobs.apple.com/api/v1/search"
APPLE_CSRF_URL = "https://jobs.apple.com/api/v1/CSRFToken"


class AppleSource(PlaywrightSource):
    """Scrape Apple Careers by replaying API requests from browser context.

    Captures the CSRF token and the actual POST payload sent by the UI,
    then replays search requests with pagination to collect all jobs.
    """

    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)
        self.raw_data: dict[str, Any] = {}  # Store raw response for later output

    async def _fetch_json_from_page(
        self,
        url: str,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute HTTP request from within browser context via JavaScript."""
        assert self.page is not None, "Page not initialized"
        return await self.page.evaluate(
            """async ({ url, options }) => {
                const response = await fetch(url, options);
                const text = await response.text();
                let data;
                try {
                  data = JSON.parse(text);
                } catch {
                  data = text;
                }
                return {
                  ok: response.ok,
                  status: response.status,
                  headers: Object.fromEntries(response.headers.entries()),
                  data,
                };
            }""",
            {"url": url, "options": options},
        )

    async def _get_csrf_token(self) -> str | None:
        """Fetch CSRF token from Apple API."""
        result = await self._fetch_json_from_page(
            APPLE_CSRF_URL,
            {
                "method": "GET",
                "credentials": "include",
                "headers": {"accept": "*/*"},
            },
        )
        token = result["headers"].get("x-apple-csrf-token")
        print(f"CSRF token: {token}")
        return token

    async def _try_search(
        self,
        csrf_token: str | None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single paginated search request."""
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "browserlocale": "en-il",
            "locale": "en_US",
        }
        if csrf_token:
            headers["x-apple-csrf-token"] = csrf_token

        return await self._fetch_json_from_page(
            APPLE_API_URL,
            {
                "method": "POST",
                "credentials": "include",
                "headers": headers,
                "body": json.dumps(payload),
            },
        )

    async def _find_search_input(self) -> Any:
        """Locate the search input field on the page."""
        assert self.page is not None, "Page not initialized"
        for selector in (
            'input[placeholder="Search by role or keyword"]',
            'input[aria-label="Search by role or keyword"]',
        ):
            locator = self.page.locator(selector).first
            if await locator.count():
                return locator
        return None

    async def _capture_ui_search_request(self) -> dict[str, Any] | None:
        """Trigger a search via the UI and capture the POST payload."""
        assert self.page is not None, "Page not initialized"
        request_data: dict[str, Any] | None = None

        def on_request(request: Any) -> None:
            nonlocal request_data
            if request.url.startswith(APPLE_API_URL) and request.method == "POST":
                request_data = {
                    "url": request.url,
                    "method": request.method,
                    "post_data": request.post_data,
                }

        self.page.on("request", on_request)

        search_input = await self._find_search_input()
        if search_input is None:
            print("Could not find search input.")
            return None

        print("Filling search input and pressing Enter...")
        await search_input.fill("software engineer")
        await search_input.press("Enter")
        await self.page.wait_for_timeout(7000)
        return request_data

    async def fetch(self, client: AsyncClient) -> list[dict[str, Any]]:
        """Fetch all jobs by replaying paginated API requests."""
        try:
            await self._launch_browser()
            assert self.page is not None, "Page not initialized"

            print(f"Opening {APPLE_SEARCH_URL}")
            await self.page.goto(APPLE_SEARCH_URL, wait_until="domcontentloaded")

            csrf_token = await self._get_csrf_token()

            ui_request = await self._capture_ui_search_request()
            if ui_request is None or not ui_request.get("post_data"):
                print("Could not capture search request from UI.")
                return []

            # Parse the captured payload
            try:
                exact_payload = json.loads(ui_request["post_data"])
            except json.JSONDecodeError:
                print("Could not parse captured payload.")
                return []

            # Paginate through results
            page_dumps: list[dict[str, Any]] = []
            seen_ids: set[str] = set()
            page_number = 1

            while True:
                payload = dict(exact_payload)
                payload["page"] = page_number
                print(f"Fetching page {page_number}...")

                result = await self._try_search(csrf_token, payload)
                page_dumps.append(
                    {
                        "page": page_number,
                        "request": payload,
                        "status": result["status"],
                        "response": result["data"],
                    }
                )

                if not isinstance(result["data"], dict):
                    print(f"Unexpected response format on page {page_number}.")
                    break

                body = cast(dict[str, Any], result["data"])
                if body.get("error") is not None:
                    print(f"API error on page {page_number}.")
                    break

                # Extract jobs
                results = self._extract_results(body)
                print(f"Jobs on page {page_number}: {len(results)}")

                if not results:
                    break

                # Track unique IDs
                for item in results:
                    identifier = (
                        item.get("reqId")
                        or item.get("id")
                        or item.get("positionId")
                    )
                    if isinstance(identifier, str):
                        seen_ids.add(identifier)

                if len(results) < 20:
                    break

                page_number += 1

            # Store raw data for external access (e.g., writing to file)
            self.raw_data = {
                "search_url": APPLE_SEARCH_URL,
                "csrf_token": csrf_token,
                "captured_request": {
                    "url": ui_request.get("url"),
                    "method": ui_request.get("method"),
                    "post_data": exact_payload,
                },
                "pages": page_dumps,
                "unique_job_identifiers": len(seen_ids),
                "total_jobs_collected": sum(
                    len(self._extract_results(page_dump["response"]))
                    for page_dump in page_dumps
                ),
            }

            # Return raw page dumps (raw data for fetch result)
            return page_dumps

        finally:
            await self._close_browser()

    def _extract_results(self, response_body: dict[str, Any] | None) -> list[dict[str, Any]]:
        """Extract job listings from API response."""
        if response_body is None:
            return []
        res_value = response_body.get("res")
        if not isinstance(res_value, dict):
            return []
        res = cast(dict[str, Any], res_value)
        search_results_value = res.get("searchResults")
        if not isinstance(search_results_value, list):
            return []

        search_results = cast(list[Any], search_results_value)
        return [item for item in search_results if isinstance(item, dict)]

    def _job_key(self, job: dict[str, Any]) -> str | None:
        """Extract unique job identifier."""
        for field in ("reqId", "id", "positionId", "jobPositionId"):
            value = job.get(field)
            if isinstance(value, str) and value:
                return value
        return None

    def _aggregate_jobs(self, pages: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Deduplicate jobs across paginated results."""
        aggregated: dict[str, dict[str, Any]] = {}
        for page in pages:
            for job in self._extract_results(page["response"]):
                key = self._job_key(job)
                if key is None:
                    continue
                aggregated[key] = job
        return aggregated

    def _locations(self, job: dict[str, Any]) -> list[str]:
        """Extract location names from job record."""
        raw_locations_value = job.get("locations")
        if not isinstance(raw_locations_value, list):
            return []

        locations: list[str] = []
        for location_value in cast(list[Any], raw_locations_value):
            if not isinstance(location_value, dict):
                continue

            location = cast(dict[str, Any], location_value)
            name_value = location.get("name")
            if isinstance(name_value, str) and name_value:
                locations.append(name_value)

        return locations

    def _build_job_record(self, job: dict[str, Any], fallback_key: str) -> dict[str, Any]:
        """Transform raw API job record into normalized format matching normalization keys."""
        req_id = self._job_key(job) or fallback_key
        
        # Use postingTitle for the actual job title
        title = str(job.get("postingTitle") or "")
        
        # Use transformedPostingTitle (slug) for the URL
        title_slug = str(job.get("transformedPostingTitle") or job.get("postingTitle") or "")
        
        team_code = None
        team_value = job.get("team")
        if isinstance(team_value, dict):
            team = cast(dict[str, Any], team_value)
            team_code_value = team.get("teamCode")
            if isinstance(team_code_value, str):
                team_code = team_code_value

        url = f"https://jobs.apple.com/en-il/details/{req_id}/{title_slug}"
        if team_code:
            url = f"{url}?team={team_code}"

        # Extract first location name for the location field
        locations_list = self._locations(job)
        location = locations_list[0] if locations_list else None

        return {
            "id": req_id,
            "title": title,
            "url": url,
            "location": location,
            "description": job.get("jobSummary"),
            "posted_at": job.get("postingDate") or job.get("postDateInGMT"),
        }

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw API job records into JobPosting models.
        
        Processes paginated API responses: extracts jobs, deduplicates,
        transforms via _build_job_record, then normalizes to JobPosting models.
        """
        if not isinstance(raw, list):
            return []
        
        # raw is the page_dumps list from fetch()
        # Each item has: {"page": int, "request": dict, "status": int, "response": dict}
        
        # Aggregate jobs across pages
        aggregated = self._aggregate_jobs(raw)
        if not aggregated:
            return []
        
        # Transform each job and normalize
        transformed: list[dict[str, Any]] = []
        for job_key, job in aggregated.items():
            record = self._build_job_record(job, job_key)
            transformed.append(record)
        
        # Use generic normalization to create JobPosting models
        return normalize_records("apple", transformed)


# Backwards-compatible name used by dynamic loader
Source = AppleSource
