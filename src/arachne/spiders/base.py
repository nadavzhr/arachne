"""Spider interface definitions for Arachne."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from arachne.config.loader import SpiderConfig
from arachne.logging import spider_logger
from arachne.models.job import JobPosting
from arachne.models.schema import JobSearchCriteria

if TYPE_CHECKING:
    from arachne.clients.base import FetchContext


class Spider(ABC):
    """Abstract base class for all Arachne job spiders."""

    def __init__(self, cfg: SpiderConfig) -> None:
        """Initialize the spider with its configuration.

        Args:
            cfg: The configuration object for this spider.
        """
        self.cfg = cfg
        self.name = cfg.name or self.__class__.__name__.removesuffix("Spider").lower()
        self.log = spider_logger(self.name, self.__class__.__module__)

    @abstractmethod
    async def fetch(self, ctx: FetchContext, search: JobSearchCriteria) -> Any:
        """Fetch raw payload from the provider.

        Args:
            ctx: The fetch context containing HTTP and browser clients.
            search: The search criteria to apply.

        Returns:
            Any: The raw data retrieved from the provider (e.g., JSON dict or list).

        Raises:
            Exception: If the fetch operation fails.
        """

    @abstractmethod
    def normalize(self, raw: Any) -> list[JobPosting]:
        """Convert raw payload into a list of JobPosting models.

        Args:
            raw: The raw data retrieved via the fetch method.

        Returns:
            list[JobPosting]: A list of normalized job postings.
        """
