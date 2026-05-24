"""Service for managing and querying job postings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from arachne.models.job import JobPosting

if TYPE_CHECKING:
    from arachne.storage.base import JobStorage


class JobService:
    """Service to handle high-level job data operations."""

    def __init__(self, storage: JobStorage) -> None:
        self.storage = storage

    def get_jobs_for_source(self, source_name: str, category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings for a given source."""
        return self.storage.load_jobs(source_name, category=category)

    def get_all_jobs(self, source_names: list[str], category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings across multiple sources."""
        all_jobs = []
        for name in source_names:
            all_jobs.extend(self.get_jobs_for_source(name, category=category))
        return all_jobs
