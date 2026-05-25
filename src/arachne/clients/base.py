"""Base definitions for Arachne clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

    from arachne.clients.playwright import PlaywrightManager


@dataclass(frozen=True)
class FetchContext:
    """Context provided to spiders during the fetch phase.

    Contains shared clients for HTTP and browser-based scraping.
    """

    http: httpx.AsyncClient
    browser: PlaywrightManager
