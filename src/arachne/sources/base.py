"""Source interface definitions for Arachne."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from arachne.config.loader import SourceConfig
from arachne.logging import source_logger
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria


class Source(ABC):
    """Abstract base class for all Arachne job sources."""

    def __init__(self, cfg: SourceConfig) -> None:
        self.cfg = cfg
        self.name = cfg.name or self.__class__.__name__.removesuffix("Source").lower()
        self.log = source_logger(self.name, self.__class__.__module__)

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient, search: JobSearchCriteria) -> Any:
        """Fetch raw payload from the provider."""

    @abstractmethod
    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw payload into a list of JobPosting models."""
