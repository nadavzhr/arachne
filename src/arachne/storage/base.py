"""Base interface for job storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from arachne.models.job import JobPosting


class JobStorage(ABC):
    """Abstract base class for storing and retrieving job postings.

    Implementations should handle persistence of both normalized job
    models and raw fetched data.
    """

    @abstractmethod
    def save_jobs(
        self, spider: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save a list of job postings for a given spider.

        Args:
            spider: Name of the spider that found the jobs.
            jobs: Sequence of JobPosting models to save.
            category: A label to distinguish between job sets
                (e.g., 'filtered', 'unfiltered').
        """
        pass

    @abstractmethod
    def save_raw(self, spider: str, raw_payload: Any) -> None:
        """Save the raw fetched payload for debugging/inspection.

        Args:
            spider: Name of the spider that fetched the data.
            raw_payload: The raw data as received from the source.
        """
        pass

    @abstractmethod
    def load_jobs(self, spider: str, category: str = "filtered") -> list[JobPosting]:
        """Load job postings for a given spider and category.

        Args:
            spider: Name of the spider whose jobs to load.
            category: The category of jobs to load.

        Returns:
            list[JobPosting]: A list of loaded JobPosting models.
        """
        pass
