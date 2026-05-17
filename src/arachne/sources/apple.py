"""
Replay Apple Careers search requests with Playwright.

TEMPORARY SOLUTION AS WELL
NEXT: Implement a shared thin playwright source base class
for both Google and Apple, and refactor both to use it.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from playwright.async_api import Locator, async_playwright

APPLE_SEARCH_URL = "https://jobs.apple.com/en-il/search?location=israel-ISR&key=software%2520engineer"
APPLE_API_URL = "https://jobs.apple.com/api/v1/search"
APPLE_CSRF_URL = "https://jobs.apple.com/api/v1/CSRFToken"
RAW_OUTPUT_PATH = Path("tmp/apple_jobs_raw.json")
FILTERED_OUTPUT_PATH = Path("tmp/apple_jobs.json")


async def _fetch_json_from_page(
    page: Any,
    url: str,
    options: dict[str, Any],
) -> dict[str, Any]:
    return await page.evaluate(
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


async def _get_csrf_token(page: Any) -> str | None:
    result = await _fetch_json_from_page(
        page,
        APPLE_CSRF_URL,
        {
            "method": "GET",
            "credentials": "include",
            "headers": {
                "accept": "*/*",
            },
        },
    )

    print("\nCSRF token response")
    print(f"Status: {result['status']}")
    token = result["headers"].get("x-apple-csrf-token")
    print(f"Token header: {token}")
    if isinstance(result["data"], str) and result["data"].strip():
        print("Body:")
        print(result["data"])
    return token


async def _try_search(
    page: Any,
    csrf_token: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "browserlocale": "en-il",
        "locale": "en_US",
    }
    if csrf_token:
        headers["x-apple-csrf-token"] = csrf_token

    return await _fetch_json_from_page(
        page,
        APPLE_API_URL,
        {
            "method": "POST",
            "credentials": "include",
            "headers": headers,
            "body": json.dumps(payload),
        },
    )


async def _find_search_input(page: Any) -> Locator | None:
    for selector in (
        'input[placeholder="Search by role or keyword"]',
        'input[aria-label="Search by role or keyword"]',
    ):
        locator = page.locator(selector).first
        if await locator.count():
            return locator
    return None


def _extract_results(response_body: dict[str, Any] | None) -> list[dict[str, Any]]:
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


def _job_key(job: dict[str, Any]) -> str | None:
    for field in ("reqId", "id", "positionId", "jobPositionId"):
        value = job.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def _aggregate_jobs(pages: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    aggregated: dict[str, dict[str, Any]] = {}
    for page in pages:
        for job in _extract_results(page["response"]):
            key = _job_key(job)
            if key is None:
                continue
            aggregated[key] = job
    return aggregated


def _locations(job: dict[str, Any]) -> list[str]:
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


def _build_job_record(job: dict[str, Any], fallback_key: str) -> dict[str, Any]:
    req_id = _job_key(job) or fallback_key
    title = str(job.get("transformedPostingTitle") or job.get("postingTitle") or "")
    team_code = None
    team_value = job.get("team")
    if isinstance(team_value, dict):
        team = cast(dict[str, Any], team_value)
        team_code_value = team.get("teamCode")
        if isinstance(team_code_value, str):
            team_code = team_code_value

    url = f"https://jobs.apple.com/en-il/details/{req_id}/{title}"
    if team_code:
        url = f"{url}?team={team_code}"

    return {
        "id": req_id,
        "reqId": req_id,
        "postingTitle": job.get("postingTitle"),
        "transformedPostingTitle": job.get("transformedPostingTitle"),
        "jobSummary": job.get("jobSummary"),
        "locations": _locations(job),
        "postingDate": job.get("postingDate") or job.get("postDateInGMT"),
        "teamCode": team_code,
        "url": url,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


async def _capture_ui_search_request(page: Any) -> dict[str, Any] | None:
    request_data: dict[str, Any] | None = None

    def on_request(request: Any) -> None:
        nonlocal request_data
        if request.url.startswith(APPLE_API_URL) and request.method == "POST":
            request_data = {
                "url": request.url,
                "method": request.method,
                "post_data": request.post_data,
            }

    page.on("request", on_request)

    search_input = await _find_search_input(page)
    if search_input is None:
        print("Could not find the visible Apple search input.")
        return None

    print("Filling the visible Apple search input and pressing Enter...")
    await search_input.fill("software engineer")
    await search_input.press("Enter")
    await page.wait_for_timeout(7000)
    return request_data


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        print(f"Opening {APPLE_SEARCH_URL}")
        await page.goto(APPLE_SEARCH_URL, wait_until="domcontentloaded")
        print(f"Page title: {await page.title()}")

        csrf_token = await _get_csrf_token(page)

        ui_request = await _capture_ui_search_request(page)
        if ui_request is not None:
            print("\nCaptured UI-triggered search request")
            print(f"Method: {ui_request['method']}")
            print(f"URL: {ui_request['url']}")
            print("Post data:")
            print(ui_request["post_data"] or "<empty>")
        else:
            print("No UI-triggered search request was captured.")

        exact_payload: dict[str, Any] | None = None
        if ui_request is not None and ui_request["post_data"]:
            try:
                exact_payload = json.loads(ui_request["post_data"])
            except json.JSONDecodeError:
                exact_payload = None

        if exact_payload is None:
            raise RuntimeError("Could not capture Apple payload from the UI.")

        page_dumps: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        page_number = 1

        while True:
            payload = dict(exact_payload)
            payload["page"] = page_number
            print(f"\nTrying page {page_number}: {json.dumps(payload, ensure_ascii=False)}")
            result = await _try_search(page, csrf_token, payload)
            print(f"Status: {result['status']}")
            page_dumps.append(
                {
                    "page": page_number,
                    "request": payload,
                    "status": result["status"],
                    "response": result["data"],
                }
            )

            if not isinstance(result["data"], dict):
                print("Response body:")
                print(result["data"])
                break

            body = cast(dict[str, Any], result["data"])
            error = body.get("error")

            if error is not None:
                print("Error body:")
                print(json.dumps(error, indent=2, ensure_ascii=False))
                break

            results = _extract_results(body)
            print(f"Jobs on page {page_number}: {len(results)}")

            if not results:
                break

            seen_ids.update(
                identifier
                for item in results
                if isinstance(
                    identifier := item.get("reqId") or item.get("id") or item.get("positionId"),
                    str,
                )
            )

            if len(results) < 20:
                break

            page_number += 1

        raw_dump: dict[str, Any] = {
            "search_url": APPLE_SEARCH_URL,
            "csrf_token": csrf_token,
            "captured_request": {
                "url": ui_request["url"] if ui_request is not None else None,
                "method": ui_request["method"] if ui_request is not None else None,
                "post_data": exact_payload,
            },
            "pages": page_dumps,
            "unique_job_identifiers": len(seen_ids),
            "total_jobs_collected": sum(
                len(_extract_results(page_dump["response"])) for page_dump in page_dumps
            ),
        }

        aggregated = _aggregate_jobs(page_dumps)
        filtered: dict[str, dict[str, Any]] = {
            key: _build_job_record(job, key)
            for key, job in aggregated.items()
        }

        _write_json(RAW_OUTPUT_PATH, raw_dump)
        _write_json(FILTERED_OUTPUT_PATH, {"jobs": filtered})
        print(f"\nRaw Apple JSON written to {RAW_OUTPUT_PATH}")
        print(f"Aggregated filtered Apple jobs written to {FILTERED_OUTPUT_PATH}")
        print(f"\nUnique job identifiers collected: {len(seen_ids)}")
        print(
            "Total jobs collected across pages: "
            f"{raw_dump['total_jobs_collected']}"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
