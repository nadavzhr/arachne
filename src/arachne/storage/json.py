"""Simple JSON file storage for snapshots."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from arachne.models.job import JobPosting
from arachne.storage.base import JobStorage


class JsonFileJobStorage(JobStorage):
    """JSON implementation of job storage using local files.

    Each spider gets its own directory, and jobs are stored as
    pretty-printed JSON files.
    """

    def __init__(self, root: Path) -> None:
        """Initialize JSON file storage.

        Args:
            root: The root directory where data will be stored.
        """
        self.root = root

    def _get_filename(self, category: str) -> str:
        """Get the filename for a given job category.

        Args:
            category: The job category (e.g., 'filtered', 'unfiltered').

        Returns:
            str: The corresponding filename.
        """
        if category == "filtered":
            return "jobs.json"
        return f"jobs.{category}.json"

    def save_jobs(
        self, spider: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save a list of job postings for a given spider to a JSON file.

        Args:
            spider: Name of the spider.
            jobs: Sequence of job postings.
            category: Job category for the filename.
        """
        target_dir = self.root / spider
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / self._get_filename(category)

        payload = [j.model_dump(mode="json") for j in jobs]
        target_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def save_raw(self, spider: str, raw_payload: Any) -> None:
        """Save the raw fetched payload to raw.json for inspection.

        Args:
            spider: Name of the spider.
            raw_payload: The raw data object.
        """
        target_dir = self.root / spider
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "raw.json"
        target_file.write_text(
            json.dumps(raw_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def load_jobs(self, spider: str, category: str = "filtered") -> list[JobPosting]:
        """Load job postings for a given spider from a JSON file.

        Args:
            spider: Name of the spider.
            category: Job category to load.

        Returns:
            list[JobPosting]: A list of JobPosting models.
        """
        target_file = self.root / spider / self._get_filename(category)
        if not target_file.exists():
            return []

        data = json.loads(target_file.read_text(encoding="utf-8"))
        return [JobPosting(**item) for item in data]
