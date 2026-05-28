"""Service for managing and querying job postings."""

from __future__ import annotations

from arachne.models.job import JobPosting
from arachne.storage.db import Database


class JobService:
    """Service to handle high-level job data operations."""

    def __init__(self, db: Database) -> None:
        """Initialize the job service.

        Args:
            db: The database backend used for job persistence.
        """
        self.db = db

    def get_jobs_for_spider(self, spider_name: str, category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings for a given spider.

        Args:
            spider_name: Name of the spider whose jobs to retrieve.
            category: The storage category (e.g., 'filtered', 'unfiltered').

        Returns:
            list[JobPosting]: List of retrieved job postings.
        """
        return self.db.load_jobs(spider_name, category=category)

    def get_all_jobs(self, spider_names: list[str], category: str = "filtered") -> list[JobPosting]:
        """Retrieve the most recent job postings across multiple spiders.

        Args:
            spider_names: List of spider names to query.
            category: The storage category to retrieve from.

        Returns:
            list[JobPosting]: Combined list of job postings from all specified spiders.
        """
        all_jobs = []
        for name in spider_names:
            all_jobs.extend(self.get_jobs_for_spider(name, category=category))
        return all_jobs
