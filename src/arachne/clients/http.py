"""Shared HTTP helpers for Arachne fetchers."""

from collections.abc import Mapping
from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


def create_client(
    timeout_seconds: float = DEFAULT_TIMEOUT,
    user_agent: str | None = None,
) -> httpx.AsyncClient:
    """Create a configured HTTPX async client.

    Args:
        timeout_seconds: Request timeout in seconds.
        user_agent: Optional custom User-Agent string.

    Returns:
        httpx.AsyncClient: A configured async HTTP client.
    """
    headers = {"User-Agent": user_agent} if user_agent else None
    return httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout_seconds,
        headers=headers,
    )


async def fetch_json(
    client: httpx.AsyncClient,
    url: str,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
) -> Any:
    """Fetch JSON data from a URL.

    Args:
        client: The HTTPX client to use.
        url: The URL to fetch.
        params: Optional query parameters.
        headers: Optional request headers.

    Returns:
        Any: The parsed JSON response.

    Raises:
        httpx.HTTPStatusError: If the request fails.
    """
    resp = await client.get(url, params=params or None, headers=headers or None)
    resp.raise_for_status()
    return resp.json()


async def fetch_paginated_json(
    client: httpx.AsyncClient,
    url: str,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    *,
    start_param: str = "start",
    step: int = 10,
) -> list[Any]:
    """Fetch paginated JSON data from a URL.

    This helper automatically iterates through pages until no more items
    are returned or a partial page is encountered.

    Args:
        client: The HTTPX client to use.
        url: The URL to fetch.
        params: Base query parameters.
        headers: Optional request headers.
        start_param: The query parameter used for pagination offset.
        step: The number of items per page.

    Returns:
        list[Any]: A flattened list of all items from all pages.
    """
    all_results: list[Any] = []

    start = 0

    while True:
        page_params = dict(params or {})
        page_params[start_param] = start

        try:
            data = await fetch_json(
                client,
                url,
                params=page_params,
                headers=headers,
            )
        except httpx.HTTPStatusError:
            break

        # normalize common response shapes
        items = data

        if isinstance(data, dict):
            if "jobs" in data:
                items = data["jobs"]
            elif "data" in data and isinstance(data["data"], dict) and "positions" in data["data"]:
                items = data["data"]["positions"]

        if not items:
            break

        if not isinstance(items, list):
            break

        all_results.extend(items)

        # stop if final partial page
        if len(items) < step:
            break

        start += step

    return all_results
