"""Service for managing and querying job postings."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

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

    def get_analytics(self, spider_names: list[str]) -> dict[str, Any]:
        """Compile execution statistics and job distribution data.

        Returns:
            dict: Analytics payload including latest runs and company stats.
        """
        latest_runs = self.db.get_latest_spider_runs(limit=len(spider_names) * 2)

        # Get latest run per spider for a cleaner high-level view
        spider_status = []
        seen_spiders = set()
        for run in latest_runs:
            name = run["spider"]
            if name not in seen_spiders:
                # Convert SQLite YYYY-MM-DD HH:MM:SS to ISO YYYY-MM-DDTHH:MM:SSZ
                run_copy = dict(run)
                if "executed_at" in run_copy and run_copy["executed_at"]:
                    iso_dt = run_copy["executed_at"].replace(" ", "T") + "Z"
                    run_copy["executed_at"] = iso_dt

                spider_status.append(run_copy)
                seen_spiders.add(name)

        all_jobs = self.get_all_jobs(spider_names)

        # Company distribution
        company_counts: dict[str, int] = {}
        for job in all_jobs:
            name = job.company or "Unknown"
            company_counts[name] = company_counts.get(name, 0) + 1

        # Spider distribution
        spider_counts: dict[str, int] = {}
        for job in all_jobs:
            spider_counts[job.spider] = spider_counts.get(job.spider, 0) + 1

        return {
            "last_updated": datetime.now(UTC).isoformat(),
            "total_jobs": len(all_jobs),
            "spider_status": spider_status,
            "company_distribution": [
                {"name": k, "count": v}
                for k, v in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            "spider_distribution": [
                {"name": k, "count": v}
                for k, v in sorted(spider_counts.items(), key=lambda x: x[1], reverse=True)
            ],
        }
