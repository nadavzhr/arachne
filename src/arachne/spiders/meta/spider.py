"""Meta Careers spider implementation using Playwright API replay.

Captures a search request from Meta Careers (GraphQL) to obtain required
payload fields, then replays the request with configured search input.
"""

from __future__ import annotations

import json
import re
from typing import Any, cast
from urllib.parse import parse_qs

from httpx import AsyncClient
from playwright.async_api import Locator, Page, Response
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from arachne.clients.playwright import browser_session
from arachne.config.loader import SpiderConfig
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria
from arachne.spiders.base import Spider as BaseSpider
from arachne.spiders.meta.params import MetaParams
from arachne.utils.normalization import first_any, first_str, parse_datetime

META_JOBS_URL = "https://www.metacareers.com/jobs"
META_GRAPHQL_URL = "https://www.metacareers.com/graphql"
META_QUERY_NAME = "CareersJobSearchResultsDataQuery"
DEFAULT_DOC_ID = "29615178951461218"
FOR_LOOP_PREFIX = "for (;;);"

LSD_PATTERNS = (
    re.compile(r'"LSD",\[\],\{"token":"([^"]+)"\}'),
    re.compile(r'name="lsd" value="([^"]+)"'),
)

_TITLE_KEYS = ("title", "job_title", "position_title", "postingTitle", "name")
_URL_KEYS = ("url", "jobUrl", "applyUrl", "apply_url", "positionUrl", "positionUrlSuffix")
_ID_KEYS = ("id", "job_id", "jobId", "req_id", "reqId", "requisition_id", "requisitionId")
_LOCATION_KEYS = ("location", "locations", "job_location", "jobLocation", "locationName")
_DESCRIPTION_KEYS = ("description", "jobDescription", "job_summary", "summary")
_POSTED_KEYS = ("posted_at", "postedAt", "postingDate", "datePosted", "created_time", "postDate")

_PRIMARY_JOB_PATHS: tuple[tuple[str, ...], ...] = (
    ("jobSearch", "jobs"),
    ("jobSearch", "results"),
    ("jobSearch", "nodes"),
    ("job_search", "jobs"),
    ("job_search", "results"),
    ("job_search", "nodes"),
    ("careerJobSearch", "jobs"),
)


def _strip_js_prefix(text: str) -> str:
    """Remove common JS prefixes from GraphQL responses.

    Args:
        text: The raw response text.

    Returns:
        str: The cleaned JSON string.
    """
    if text.startswith(FOR_LOOP_PREFIX):
        return text[len(FOR_LOOP_PREFIX) :].lstrip()
    return text


def _parse_form_data(post_data: str) -> dict[str, str]:
    """Parse URL-encoded form data into a dictionary.

    Args:
        post_data: The raw POST data string.

    Returns:
        dict[str, str]: A dictionary of key-value pairs from the form data.
    """
    parsed = parse_qs(post_data, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items() if values}


def _parse_graphql_text(text: str) -> list[dict[str, Any]]:
    """Parse Meta's multi-part GraphQL response text.

    Args:
        text: The raw response text, potentially containing multiple JSON objects.

    Returns:
        list[dict[str, Any]]: A list of parsed JSON objects.
    """
    items: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = _strip_js_prefix(line)
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            items.append(cast(dict[str, Any], obj))

    if items:
        return items

    raw = _strip_js_prefix(text.strip())
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(obj, dict):
        return [cast(dict[str, Any], obj)]
    return []


class MetaSpider(BaseSpider):
    """Spider for Meta Careers portal.

    This spider uses a hybrid approach: it uses Playwright to capture the
    necessary GraphQL metadata (lsd token, doc_id, variables) from a real
    browser session, and then replays the GraphQL request with custom
    search parameters.
    """

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize Meta spider.

        Args:
            cfg: Spider configuration.
        """
        super().__init__(cfg)

    def _response_is_job_search(self, response: Response) -> bool:
        """Check if a Playwright response is a Meta job search GraphQL call.

        Args:
            response: The Playwright response to check.

        Returns:
            bool: True if it matches the job search signature.
        """
        if response.request.method != "POST":
            return False
        if not response.url.startswith(META_GRAPHQL_URL):
            return False
        post_data = response.request.post_data or ""
        parsed = _parse_form_data(post_data)
        return bool(parsed) and self._is_job_search_payload(parsed)

    def _response_is_search_fallback(self, response: Response) -> bool:
        """Check if a response looks like a generic Meta search GraphQL call.

        Args:
            response: The Playwright response to check.

        Returns:
            bool: True if it matches a generic search signature.
        """
        if response.request.method != "POST":
            return False
        if not response.url.startswith(META_GRAPHQL_URL):
            return False
        post_data = response.request.post_data or ""
        parsed = _parse_form_data(post_data)
        return bool(parsed) and self._is_search_like_payload(parsed)

    async def _wait_for_response(
        self,
        page: Page,
        params: MetaParams,
        predicate: Any,
        timeout_ms: int,
    ) -> Response | None:
        """Wait for a specific response triggered by a search action.

        Args:
            page: The Playwright page.
            params: Meta search parameters.
            predicate: Function to identify the target response.
            timeout_ms: Timeout in milliseconds.

        Returns:
            Response | None: The captured response or None if timeout.
        """
        try:
            async with page.expect_response(predicate, timeout=timeout_ms) as response_info:
                await self._trigger_search(page, params)
            return await response_info.value
        except PlaywrightTimeoutError:
            return None

    async def _capture_graphql_payload(
        self, page: Page, params: MetaParams
    ) -> dict[str, Any] | None:
        """Capture GraphQL payload by performing a search in the browser.

        Args:
            page: The Playwright page.
            params: Meta search parameters.

        Returns:
            dict[str, Any] | None: Captured request and response details or None.
        """
        await page.goto(META_JOBS_URL, wait_until="domcontentloaded")
        response = await self._wait_for_response(page, params, self._response_is_job_search, 15000)
        if response is None:
            response = await self._wait_for_response(
                page, params, self._response_is_search_fallback, 8000
            )
        if response is None:
            return None

        request = response.request
        post_data = request.post_data or ""
        parsed = _parse_form_data(post_data)
        if not parsed:
            return None
        return {
            "post_data": post_data,
            "parsed": parsed,
            "status": response.status,
            "response_text": await response.text(),
        }

    def _is_job_search_payload(self, payload: dict[str, str]) -> bool:
        """Verify if a GraphQL payload is the specific job search query.

        Args:
            payload: The parsed POST data.

        Returns:
            bool: True if it is the job search query.
        """
        if payload.get("fb_api_req_friendly_name") == META_QUERY_NAME:
            return True
        if payload.get("doc_id") == DEFAULT_DOC_ID:
            return True
        return False

    def _is_search_like_payload(self, payload: dict[str, str]) -> bool:
        """Verify if a GraphQL payload contains search-like variables.

        Args:
            payload: The parsed POST data.

        Returns:
            bool: True if it has a search_input field in variables.
        """
        raw_variables = payload.get("variables")
        if not raw_variables:
            return False
        try:
            variables = json.loads(raw_variables)
        except json.JSONDecodeError:
            return False
        if not isinstance(variables, dict):
            return False
        variables_map: dict[str, Any] = {}
        for key, value in cast(dict[str, Any], variables).items():
            variables_map[key] = value
        search_input = variables_map.get("search_input")
        return isinstance(search_input, dict)

    async def _find_search_input(self, page: Page) -> Locator | None:
        """Find the search input field on the Meta Careers page.

        Args:
            page: The Playwright page.

        Returns:
            Locator | None: The search input locator or None if not found.
        """
        selectors = (
            'input[type="search"]',
            'input[placeholder*="Search"]',
            'input[aria-label*="Search"]',
            'input[name*="search"]',
        )
        for selector in selectors:
            locator = page.locator(selector).first
            if await locator.count():
                return locator
        return None

    async def _trigger_search(self, page: Page, params: MetaParams) -> None:
        """Perform search actions in the browser to trigger GraphQL requests.

        Args:
            page: The Playwright page.
            params: Meta search parameters.
        """
        search_input = await self._find_search_input(page)
        if search_input is None:
            await page.wait_for_timeout(1500)
            return
        await search_input.click()
        await search_input.fill(params.query)
        await search_input.press("Enter")
        await page.wait_for_timeout(1500)

    async def _extract_lsd_token(self, page: Page) -> str | None:
        """Extract the LSD security token from the page.

        Args:
            page: The Playwright page.

        Returns:
            str | None: The LSD token or None if not found.
        """
        token = await page.evaluate(
            """() => {
            const el = document.querySelector('input[name="lsd"]');
            return el ? el.value : null;
        }""",
        )
        if isinstance(token, str) and token:
            return token
        html = await page.content()
        for pattern in LSD_PATTERNS:
            match = pattern.search(html)
            if match:
                return match.group(1)
        return None

    def _merge_variables(self, params: MetaParams, raw_variables: str | None) -> dict[str, Any]:
        """Merge custom search parameters into existing GraphQL variables.

        Args:
            params: Custom Meta search parameters.
            raw_variables: JSON string of existing GraphQL variables.

        Returns:
            dict[str, Any]: Merged GraphQL variables.
        """
        payload: dict[str, Any] = {}
        if raw_variables:
            try:
                parsed = json.loads(raw_variables)
            except json.JSONDecodeError:
                parsed = {}
            if isinstance(parsed, dict):
                for key, value in cast(dict[str, Any], parsed).items():
                    payload[key] = value
        existing = payload.get("search_input")
        search_input: dict[str, Any] = {}
        if isinstance(existing, dict):
            for key, value in cast(dict[str, Any], existing).items():
                search_input[key] = value
        for field in sorted(params.model_fields_set):
            if field == "doc_id":
                continue
            if field == "query":
                search_input["q"] = params.query
                continue
            search_input[field] = getattr(params, field)
        payload["search_input"] = search_input
        return payload

    def _build_payload(
        self,
        base_payload: dict[str, str],
        lsd_token: str,
        doc_id: str,
        variables: dict[str, Any],
    ) -> dict[str, str | float | bool]:
        """Build the final GraphQL request payload.

        Args:
            base_payload: Base form data captured from browser.
            lsd_token: LSD security token.
            doc_id: GraphQL document ID.
            variables: GraphQL variables dictionary.

        Returns:
            dict[str, str | float | bool]: Final POST payload.
        """
        payload: dict[str, str | float | bool] = {key: value for key, value in base_payload.items()}
        payload.setdefault("av", "0")
        payload.setdefault("__user", "0")
        payload.setdefault("__a", "1")
        payload.setdefault("fb_api_caller_class", "RelayModern")
        payload.setdefault("fb_api_req_friendly_name", META_QUERY_NAME)
        payload.setdefault("server_timestamps", "true")
        payload["lsd"] = lsd_token
        payload["doc_id"] = doc_id
        payload["variables"] = json.dumps(variables)
        return payload

    async def fetch(self, client: AsyncClient, search: JobSearchCriteria) -> list[dict[str, Any]]:
        """Fetch job listings from Meta Careers.

        Uses Playwright to capture session context and replay GraphQL requests.

        Args:
            client: The HTTPX client (unused, uses Playwright context).
            search: Standard search criteria.

        Returns:
            list[dict[str, Any]]: Raw GraphQL response payloads.
        """
        del client  # Unused.
        params = MetaParams.from_search(search)

        async with browser_session(user_agent=self.cfg.user_agent) as page:
            captured = await self._capture_graphql_payload(page, params)
            base_payload: dict[str, str] = {}
            if captured:
                parsed_payload = cast(dict[str, str], captured.get("parsed", {}))
                lsd_token = parsed_payload.get("lsd")
                variables = self._merge_variables(params, parsed_payload.get("variables"))
                doc_id = params.doc_id or parsed_payload.get("doc_id") or DEFAULT_DOC_ID
                base_payload = parsed_payload
            else:
                lsd_token = await self._extract_lsd_token(page)
                variables = params.to_variables()
                doc_id = params.doc_id or DEFAULT_DOC_ID

            if not lsd_token:
                self.log.warning("request build stopped: missing_lsd_token")
                return []

            payload = self._build_payload(base_payload, lsd_token, doc_id, variables)

            # Use page context to make the request so we share cookies/headers
            response = await page.request.post(
                META_GRAPHQL_URL,
                form=payload,
                headers={
                    "Origin": "https://www.metacareers.com",
                    "Referer": META_JOBS_URL,
                },
            )

            if not response.ok:
                self.log.warning(
                    "graphql request failed: status=%d body=%s",
                    response.status,
                    await response.text(),
                )
                return []

            response_text = await response.text()
            payloads = _parse_graphql_text(response_text)
            if not payloads:
                self.log.warning("graphql response parsed no payloads")
            else:
                self.log.info("graphql response parsed: payloads=%d", len(payloads))
            return payloads

    def normalize(self, raw: Any) -> list[JobPosting]:
        """Normalize raw Meta GraphQL payloads into JobPosting models.

        Args:
            raw: The raw data returned by fetch().

        Returns:
            list[JobPosting]: A list of normalized job postings.
        """
        if not isinstance(raw, list):
            return []
        items = raw
        payloads = [cast(dict[str, Any], item) for item in items if isinstance(item, dict)]
        records = self._extract_jobs(payloads)
        return self._dedupe_jobs(records)

    def _extract_jobs(self, payloads: list[dict[str, Any]]) -> list[JobPosting]:
        """Extract job listings from multiple GraphQL payloads.

        Args:
            payloads: List of GraphQL response objects.

        Returns:
            list[JobPosting]: Extracted job postings.
        """
        jobs: list[JobPosting] = []
        for payload in payloads:
            jobs.extend(self._extract_jobs_from_payload(payload))
        return jobs

    def _extract_jobs_from_payload(self, payload: dict[str, Any]) -> list[JobPosting]:
        """Extract job listings from a single GraphQL payload.

        Args:
            payload: A single GraphQL response object.

        Returns:
            list[JobPosting]: Extracted job postings.
        """
        data = payload.get("data")
        if not isinstance(data, dict):
            return []
        data_map = cast(dict[str, Any], data)

        for path in _PRIMARY_JOB_PATHS:
            node = self._resolve_path(data_map, path)
            items = self._normalize_job_container(node)
            if items:
                return self._build_job_records(items)

        fallback_items = self._search_for_job_list(data_map)
        return self._build_job_records(fallback_items)

    def _build_job_records(self, items: list[dict[str, Any]]) -> list[JobPosting]:
        """Convert a list of raw job dictionaries into JobPosting models.

        Args:
            items: List of raw job dictionaries.

        Returns:
            list[JobPosting]: List of JobPosting models.
        """
        records: list[JobPosting] = []
        for job in items:
            record = self._build_job_record(job)
            if record:
                records.append(record)
        return records

    def _resolve_path(self, data: dict[str, Any], path: tuple[str, ...]) -> Any:
        """Resolve a nested path in a dictionary.

        Args:
            data: The dictionary to traverse.
            path: Tuple of keys representing the path.

        Returns:
            Any: The value at the path or None.
        """
        node: Any = data
        for key in path:
            if not isinstance(node, dict):
                return None
            node = cast(dict[str, Any], node).get(key)
        return node

    def _normalize_job_container(self, node: Any) -> list[dict[str, Any]]:
        """Normalize various job container formats (list, edges, results).

        Args:
            node: The raw job container node.

        Returns:
            list[dict[str, Any]]: Flattened list of job dictionaries.
        """
        if isinstance(node, list):
            return self._flatten_edges(node)
        if isinstance(node, dict):
            node_map = cast(dict[str, Any], node)
            for key in ("jobs", "results", "nodes", "edges"):
                if key in node_map:
                    return self._normalize_job_container(node_map[key])
        return []

    def _flatten_edges(self, node: list[Any]) -> list[dict[str, Any]]:
        """Flatten GraphQL 'edges' or similar list structures.

        Args:
            node: The list of items or edges.

        Returns:
            list[dict[str, Any]]: Flattened list of job dictionaries.
        """
        items: list[dict[str, Any]] = []
        for item in node:
            if not isinstance(item, dict):
                continue
            if "node" in item and isinstance(item["node"], dict):
                items.append(cast(dict[str, Any], item["node"]))
            else:
                items.append(cast(dict[str, Any], item))
        return items

    def _search_for_job_list(self, data: Any) -> list[dict[str, Any]]:
        """Recursively search for the best candidate for a job list in the data.

        Args:
            data: The raw data to search.

        Returns:
            list[dict[str, Any]]: The most likely job list found.
        """
        best: list[dict[str, Any]] = []
        best_score = 0

        def walk(value: Any) -> None:
            nonlocal best, best_score
            if isinstance(value, dict):
                for sub_value in cast(dict[str, Any], value).values():
                    walk(sub_value)
                return
            if not isinstance(value, list):
                return

            value_list = value
            dict_items = [
                cast(dict[str, Any], item) for item in value_list if isinstance(item, dict)
            ]
            if dict_items:
                score = sum(1 for item in dict_items if self._is_job_item(item))
                if score > best_score:
                    best_score = score
                    best = dict_items
            for item in value_list:
                walk(item)

        walk(data)
        return best

    def _is_job_item(self, item: dict[str, Any]) -> bool:
        """Determine if a dictionary likely represents a job listing.

        Args:
            item: The dictionary to check.

        Returns:
            bool: True if it has enough job-like fields.
        """
        score = 0
        if first_str(item, _TITLE_KEYS):
            score += 1
        if first_str(item, _URL_KEYS) or first_str(item, _ID_KEYS):
            score += 1
        if first_str(item, _LOCATION_KEYS):
            score += 1
        return score >= 2

    def _build_job_record(self, job: dict[str, Any]) -> JobPosting | None:
        """Map a raw job dictionary to a JobPosting model.

        Args:
            job: Raw job dictionary.

        Returns:
            JobPosting | None: The mapped JobPosting or None if mapping fails.
        """
        title = first_str(job, _TITLE_KEYS)
        if not title:
            return None

        url = first_str(job, _URL_KEYS)
        job_id = first_str(job, _ID_KEYS)
        if not url and job_id:
            url = f"{META_JOBS_URL}/{job_id}/"
        if not url:
            return None

        location = first_str(job, _LOCATION_KEYS)
        description = first_str(job, _DESCRIPTION_KEYS)
        posted_raw = first_any(job, _POSTED_KEYS)

        try:
            return JobPosting(
                spider=self.name,
                company="Meta",
                title=title,
                url=url,  # type: ignore
                location=location,
                external_id=job_id,
                description=description,
                posted_at=parse_datetime(posted_raw),
            )
        except Exception as e:
            self.log.debug("Failed to map meta record: %s", e)
            return None

    def _dedupe_jobs(self, records: list[JobPosting]) -> list[JobPosting]:
        """Remove duplicate job postings based on external_id, url, or title.

        Args:
            records: List of job postings to deduplicate.

        Returns:
            list[JobPosting]: Deduplicated list of job postings.
        """
        seen: set[str] = set()
        unique: list[JobPosting] = []
        for record in records:
            key = record.external_id or str(record.url) or record.title
            if key in seen:
                continue
            seen.add(key)
            unique.append(record)
        return unique


async def _run_demo() -> None:
    """Run a demo of the Meta spider."""
    cfg = SpiderConfig(url=META_JOBS_URL)
    from arachne.logging import configure_logging, spider_logger

    configure_logging(
        enabled=True,
        directory="logs",
        level="INFO",
        central_file="arachne.log",
        spider_directory="spiders",
    )
    demo_log = spider_logger("meta", __name__)
    async with AsyncClient() as client:
        src = MetaSpider(cfg)
        raw = await src.fetch(client, JobSearchCriteria())
        jobs = src.normalize(raw)
        demo_log.info("demo completed: jobs=%d", len(jobs))


# Backwards-compatible name used by dynamic loader
Spider = MetaSpider


if __name__ == "__main__":
    import asyncio

    asyncio.run(_run_demo())
