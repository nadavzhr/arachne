"""Shared HTTP helpers for Arachne fetchers."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


class ThrottledClient:
    """A wrapper for httpx.AsyncClient that enforces a global concurrency limit.

    This ensures that the total number of outoing requests across all spiders
    does not exceed a certain threshold, preventing rate-limiting.
    """

    def __init__(self, client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> None:
        self._client = client
        self._semaphore = semaphore

    async def get(self, *args: Any, **kwargs: Any) -> httpx.Response:
        async with self._semaphore:
            return await self._client.get(*args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
        async with self._semaphore:
            return await self._client.post(*args, **kwargs)

    async def request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        async with self._semaphore:
            return await self._client.request(*args, **kwargs)

    async def __aenter__(self) -> ThrottledClient:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


def create_client(
    timeout_seconds: float = DEFAULT_TIMEOUT,
    user_agent: str | None = None,
    request_concurrency: int | None = None,
) -> httpx.AsyncClient | ThrottledClient:
    """Create a configured HTTPX async client.

    Args:
        timeout_seconds: Request timeout in seconds.
        user_agent: Optional custom User-Agent string.
        request_concurrency: Optional limit for concurrent HTTP requests.

    Returns:
        httpx.AsyncClient | ThrottledClient: A configured async HTTP client.
    """
    headers = {"User-Agent": user_agent} if user_agent else None
    client = httpx.AsyncClient(
        follow_redirects=True,
        timeout=timeout_seconds,
        headers=headers,
    )

    if request_concurrency and request_concurrency > 0:
        return ThrottledClient(client, asyncio.Semaphore(request_concurrency))

    return client


async def fetch_json(
    client: httpx.AsyncClient | ThrottledClient,
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
    client: httpx.AsyncClient | ThrottledClient,
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
