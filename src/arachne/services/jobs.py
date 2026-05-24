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

    def get_jobs_for_spider(self, spider_name: str, category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings for a given spider."""
        return self.storage.load_jobs(spider_name, category=category)

    def get_all_jobs(self, spider_names: list[str], category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings across multiple spiders."""
        all_jobs = []
        for name in spider_names:
            all_jobs.extend(self.get_jobs_for_spider(name, category=category))
        return all_jobs
