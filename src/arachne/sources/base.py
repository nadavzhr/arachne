"""Source interface definitions for Arachne.

Defines a small class-based interface each source should implement:
- `fetch(client)` -> raw payload (any)
- `normalize(raw)` -> list[JobPosting]

Filtering is handled after normalization in the runner, so sources should not
apply filtering inside `normalize`.

Using classes keeps per-source `cfg` and helpers together and lets the runner
always call the same two methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from arachne.config.loader import SourceConfig
from arachne.models.job import JobPosting


class Source(ABC):
    def __init__(self, cfg: SourceConfig) -> None:
        self.cfg = cfg

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient) -> Any:
        """Fetch raw payload for this source. Return whatever the provider returns."""

    @abstractmethod
    def normalize(self, raw: Any) -> list[JobPosting]:
        """Normalize raw payload into a list of `JobPosting` models."""
