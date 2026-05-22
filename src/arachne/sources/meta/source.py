"""Meta Careers source implementation using Playwright API replay.

Captures a search request from Meta Careers (GraphQL) to obtain required
payload fields, then replays the request with configured search input.
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import UTC, datetime
from typing import Any, cast
from urllib.parse import parse_qs

from httpx import AsyncClient
from playwright.async_api import Locator, Response

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting
from arachne.sources.meta.params import MetaParams
from arachne.sources.playwright import PlaywrightSource
from arachne.utils.normalization import normalize_records

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
    if text.startswith(FOR_LOOP_PREFIX):
        return text[len(FOR_LOOP_PREFIX) :].lstrip()
    return text


def _parse_form_data(post_data: str) -> dict[str, str]:
    parsed = parse_qs(post_data, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items() if values}


def _parse_graphql_text(text: str) -> list[dict[str, Any]]:
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


class MetaSource(PlaywrightSource):
    def __init__(self, cfg: SourceConfig) -> None:
        super().__init__(cfg)
        self.params = MetaParams.from_search(cfg.search)

    def _response_is_job_search(self, response: Response) -> bool:
        if response.request.method != "POST":
            return False
        if not response.url.startswith(META_GRAPHQL_URL):
            return False
        post_data = response.request.post_data or ""
        parsed = _parse_form_data(post_data)
        return bool(parsed) and self._is_job_search_payload(parsed)

    def _response_is_search_fallback(self, response: Response) -> bool:
        if response.request.method != "POST":
            return False
        if not response.url.startswith(META_GRAPHQL_URL):
            return False
        post_data = response.request.post_data or ""
        parsed = _parse_form_data(post_data)
        return bool(parsed) and self._is_search_like_payload(parsed)

    async def _wait_for_response(
        self,
        predicate: Any,
        timeout_ms: int,
    ) -> Response | None:
        assert self.page is not None, "Page not initialized"
        try:
            async with self.page.expect_response(predicate, timeout=timeout_ms) as response_info:
                await self._trigger_search()
            return await response_info.value
        except TimeoutError:
            return None

    async def _capture_graphql_payload(self) -> dict[str, Any] | None:
        assert self.page is not None, "Page not initialized"
        await self.page.goto(META_JOBS_URL, wait_until="domcontentloaded")
        response = await self._wait_for_response(self._response_is_job_search, 15000)
        if response is None:
            response = await self._wait_for_response(self._response_is_search_fallback, 8000)
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
        if payload.get("fb_api_req_friendly_name") == META_QUERY_NAME:
            return True
        if payload.get("doc_id") == DEFAULT_DOC_ID:
            return True
        return False

    def _is_search_like_payload(self, payload: dict[str, str]) -> bool:
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

    async def _find_search_input(self) -> Locator | None:
        assert self.page is not None, "Page not initialized"
        selectors = (
            'input[type="search"]',
            'input[placeholder*="Search"]',
            'input[aria-label*="Search"]',
            'input[name*="search"]',
        )
        for selector in selectors:
            locator = self.page.locator(selector).first
            if await locator.count():
                return locator
        return None

    async def _trigger_search(self) -> None:
        assert self.page is not None, "Page not initialized"
        search_input = await self._find_search_input()
        if search_input is None:
            await self.page.wait_for_timeout(1500)
            return
        await search_input.click()
        await search_input.fill(self.params.query)
        await search_input.press("Enter")
        await self.page.wait_for_timeout(1500)

    async def _extract_lsd_token(self) -> str | None:
        assert self.page is not None, "Page not initialized"
        token = await self.page.evaluate(
            """() => {
            const el = document.querySelector('input[name="lsd"]');
            return el ? el.value : null;
        }""",
        )
        if isinstance(token, str) and token:
            return token
        html = await self.page.content()
        for pattern in LSD_PATTERNS:
            match = pattern.search(html)
            if match:
                return match.group(1)
        return None

    def _merge_variables(self, raw_variables: str | None) -> dict[str, Any]:
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
        for field in sorted(self.params.model_fields_set):
            if field == "doc_id":
                continue
            if field == "query":
                search_input["q"] = self.params.query
                continue
            search_input[field] = getattr(self.params, field)
        payload["search_input"] = search_input
        return payload

    def _build_payload(
        self,
        base_payload: dict[str, str],
        lsd_token: str,
        doc_id: str,
        variables: dict[str, Any],
    ) -> dict[str, str | float | bool]:
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

    async def fetch(self, client: AsyncClient) -> list[dict[str, Any]]:
        del client  # Unused.
        try:
            await self._launch_browser()
            assert self.page is not None, "Page not initialized"
            assert self.context is not None, "Context not initialized"

            captured = await self._capture_graphql_payload()
            base_payload: dict[str, str] = {}
            if captured:
                parsed_payload = cast(dict[str, str], captured.get("parsed", {}))
                response_text = captured.get("response_text")
                if isinstance(response_text, str):
                    payloads = _parse_graphql_text(response_text)
                    if payloads:
                        self.log.info("captured search payload parsed: payloads=%d", len(payloads))
                        return payloads
                    if captured.get("status"):
                        self.log.info("captured search response: status=%s", captured.get("status"))

                lsd_token = parsed_payload.get("lsd")
                variables = self._merge_variables(parsed_payload.get("variables"))
                doc_id = self.params.doc_id or parsed_payload.get("doc_id") or DEFAULT_DOC_ID
                base_payload = parsed_payload
            else:
                lsd_token = await self._extract_lsd_token()
                variables = self.params.to_variables()
                doc_id = self.params.doc_id or DEFAULT_DOC_ID

            if not lsd_token:
                self.log.warning("request build stopped: missing_lsd_token")
                return []

            payload = self._build_payload(base_payload, lsd_token, doc_id, variables)
            response = await self.context.request.post(
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
        finally:
            await self._close_browser()

    def normalize(self, raw: Any) -> list[JobPosting]:
        if not isinstance(raw, list):
            return []
        items = raw
        payloads = [cast(dict[str, Any], item) for item in items if isinstance(item, dict)]
        records = self._extract_jobs(payloads)
        return normalize_records("meta", records)

    def _extract_jobs(self, payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        for payload in payloads:
            jobs.extend(self._extract_jobs_from_payload(payload))
        return self._dedupe_jobs(jobs)

    def _extract_jobs_from_payload(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
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

    def _build_job_records(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for job in items:
            record = self._build_job_record(job)
            if record:
                records.append(record)
        return records

    def _resolve_path(self, data: dict[str, Any], path: tuple[str, ...]) -> Any:
        node: Any = data
        for key in path:
            if not isinstance(node, dict):
                return None
            node = cast(dict[str, Any], node).get(key)
        return node

    def _normalize_job_container(self, node: Any) -> list[dict[str, Any]]:
        if isinstance(node, list):
            return self._flatten_edges(node)
        if isinstance(node, dict):
            node_map = cast(dict[str, Any], node)
            for key in ("jobs", "results", "nodes", "edges"):
                if key in node_map:
                    return self._normalize_job_container(node_map[key])
        return []

    def _flatten_edges(self, node: list[Any]) -> list[dict[str, Any]]:
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
        score = 0
        if self._first_str(item, _TITLE_KEYS):
            score += 1
        if self._first_str(item, _URL_KEYS) or self._first_str(item, _ID_KEYS):
            score += 1
        if self._extract_location(item):
            score += 1
        return score >= 2

    def _build_job_record(self, job: dict[str, Any]) -> dict[str, Any] | None:
        title = self._first_str(job, _TITLE_KEYS)
        if not title:
            return None

        url = self._first_str(job, _URL_KEYS)
        job_id = self._first_str(job, _ID_KEYS)
        if not url and job_id:
            url = f"{META_JOBS_URL}/{job_id}/"
        if not url:
            return None

        location = self._extract_location(job)
        description = self._first_str(job, _DESCRIPTION_KEYS)
        posted_raw = self._first_any(job, _POSTED_KEYS)
        posted_at = self._coerce_posted_at(posted_raw)

        record: dict[str, Any] = {
            "id": job_id,
            "title": title,
            "url": url,
            "location": location,
            "description": description,
            "posted_at": posted_at,
        }
        return {key: value for key, value in record.items() if value is not None}

    def _extract_location(self, record: dict[str, Any]) -> str | None:
        value = self._first_any(record, _LOCATION_KEYS)
        return self._format_location(value)

    def _format_location(self, value: Any) -> str | None:
        if isinstance(value, str):
            return value.strip() or None
        if isinstance(value, dict):
            value_map = cast(dict[str, Any], value)
            for key in ("name", "label", "city", "region", "country"):
                loc = value_map.get(key)
                if isinstance(loc, str) and loc.strip():
                    return loc.strip()
            return None
        if isinstance(value, list):
            names: list[str] = []
            value_list = value
            for item in value_list:
                if isinstance(item, str) and item.strip():
                    names.append(item.strip())
                elif isinstance(item, dict):
                    item_map = cast(dict[str, Any], item)
                    for key in ("name", "label", "city", "region", "country"):
                        loc = item_map.get(key)
                        if isinstance(loc, str) and loc.strip():
                            names.append(loc.strip())
                            break
            if names:
                return ", ".join(dict.fromkeys(names))
        return None

    def _coerce_posted_at(self, value: Any) -> str | None:
        if isinstance(value, (int, float)):
            ts = float(value)
            if ts > 1_000_000_000_000:
                ts = ts / 1000
            return datetime.fromtimestamp(ts, tz=UTC).isoformat()
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    def _first_str(self, record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _first_any(self, record: dict[str, Any], keys: tuple[str, ...]) -> Any | None:
        for key in keys:
            if key in record:
                return record[key]
        return None

    def _dedupe_jobs(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for record in records:
            key = record.get("id") or record.get("url") or record.get("title")
            if not isinstance(key, str):
                continue
            if key in seen:
                continue
            seen.add(key)
            unique.append(record)
        return unique


async def _run_demo() -> None:
    cfg = SourceConfig(url=META_JOBS_URL)
    from arachne.logging import configure_logging, source_logger

    configure_logging(
        enabled=True,
        directory="logs",
        level="INFO",
        central_file="arachne.log",
        source_directory="sources",
    )
    demo_log = source_logger("meta", __name__)
    async with AsyncClient() as client:
        src = MetaSource(cfg)
        raw = await src.fetch(client)
        jobs = src.normalize(raw)
        demo_log.info("demo completed: jobs=%d", len(jobs))


# Backwards-compatible name used by dynamic loader
Source = MetaSource


if __name__ == "__main__":
    asyncio.run(_run_demo())
