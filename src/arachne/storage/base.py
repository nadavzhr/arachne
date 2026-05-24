"""Base interface for job storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from arachne.models.job import JobPosting


class JobStorage(ABC):
    """Abstract base class for storing and retrieving job postings."""

    @abstractmethod
    def save_jobs(
        self, source: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save a list of job postings for a given source.

        The 'category' can be used to distinguish between 'filtered' and 'unfiltered'
        or other types of job sets.
        """
        pass

    @abstractmethod
    def save_raw(self, source: str, raw_payload: Any) -> None:
        """Save the raw fetched payload for debugging/inspection."""
        pass

    @abstractmethod
    def load_jobs(self, source: str, category: str = "filtered") -> list[JobPosting]:
        """Load job postings for a given source and category."""
        pass
