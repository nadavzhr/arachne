"""Shared HTTP helpers for Arachne fetchers."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from typing import Any, cast

import httpx

DEFAULT_TIMEOUT = 30.0

logger = logging.getLogger(__name__)


class ThrottledClient:
    """A wrapper for httpx.AsyncClient that enforces a global concurrency limit.

    Includes automatic retries for transient network errors.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        max_retries: int = 3,
    ) -> None:
        self._client = client
        self._semaphore = semaphore
        self._max_retries = max_retries

    async def _request_with_retry(self, method: str, *args: Any, **kwargs: Any) -> httpx.Response:
        """Execute a request with exponential backoff retries."""
        last_exc: Exception | None = None
        func = getattr(self._client, method.lower())

        for attempt in range(self._max_retries + 1):
            try:
                async with self._semaphore:
                    result = await func(*args, **kwargs)
                    return cast(httpx.Response, result)
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    delay = 2**attempt  # Exponential backoff: 1, 2, 4s
                    logger.warning(
                        "retrying request: method=%s attempt=%d delay=%ds error=%s",
                        method,
                        attempt + 1,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
                continue

        if last_exc:
            raise last_exc
        raise RuntimeError(f"Request failed after {self._max_retries} retries")

    async def get(self, *args: Any, **kwargs: Any) -> httpx.Response:
        return await self._request_with_retry("GET", *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
        return await self._request_with_retry("POST", *args, **kwargs)

    async def request(self, method: str, *args: Any, **kwargs: Any) -> httpx.Response:
        return await self._request_with_retry(method, *args, **kwargs)

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
