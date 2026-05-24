"""Simple JSON file storage for snapshots."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from arachne.models.job import JobPosting
from arachne.storage.base import JobStorage


class JsonFileJobStorage(JobStorage):
    """JSON implementation of job storage using local files."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _get_filename(self, category: str) -> str:
        if category == "filtered":
            return "jobs.json"
        return f"jobs.{category}.json"

    def save_jobs(
        self, spider: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save a list of job postings for a given spider to a JSON file."""
        target_dir = self.root / spider
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / self._get_filename(category)

        payload = [j.model_dump(mode="json") for j in jobs]
        target_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def save_raw(self, spider: str, raw_payload: Any) -> None:
        """Save the raw fetched payload to raw.json for inspection."""
        target_dir = self.root / spider
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "raw.json"
        target_file.write_text(
            json.dumps(raw_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def load_jobs(self, spider: str, category: str = "filtered") -> list[JobPosting]:
        """Load job postings for a given spider from a JSON file."""
        target_file = self.root / spider / self._get_filename(category)
        if not target_file.exists():
            return []

        data = json.loads(target_file.read_text(encoding="utf-8"))
        return [JobPosting(**item) for item in data]
