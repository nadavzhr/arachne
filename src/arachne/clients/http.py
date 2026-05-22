"""Shared HTTP helpers for Arachne fetchers."""

from collections.abc import Mapping
from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


def create_client(
    timeout_seconds: float = DEFAULT_TIMEOUT,
    user_agent: str | None = None,
) -> httpx.AsyncClient:
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
    resp = await client.get(url, params=params or None, headers=headers or None)
    resp.raise_for_status()
    return resp.json()
