"""SQLite implementation of job storage for persistence and deduplication."""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from arachne.models.job import JobPosting


class Database:
    """SQLite implementation of job storage.

    Uses a relational database to store jobs, enabling historical tracking
    and deduplication via unique constraints.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize SQLite storage and ensure schema exists.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection to the SQLite database with dictionary-like rows."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create the necessary tables if they do not exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spider TEXT NOT NULL,
                    external_id TEXT,
                    company TEXT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    location TEXT,
                    posted_at TEXT,
                    description TEXT,
                    remote INTEGER DEFAULT 0,
                    employment_type TEXT,
                    experience_level TEXT,
                    category TEXT DEFAULT 'filtered',
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(spider, external_id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spider_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spider TEXT NOT NULL,
                    status TEXT NOT NULL,
                    found_count INTEGER DEFAULT 0,
                    filtered_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def log_spider_run(
        self,
        spider: str,
        status: str,
        found_count: int = 0,
        filtered_count: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Record a spider execution in the database."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO spider_runs (spider, status, found_count, filtered_count, error_message)
                VALUES (?, ?, ?, ?, ?)
            """,
                (spider, status, found_count, filtered_count, error_message),
            )

    def get_latest_spider_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve the most recent spider execution records."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM spider_runs ORDER BY executed_at DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def save_jobs(
        self, spider: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save job postings using an UPSERT (Update or Insert) strategy."""
        with self._get_connection() as conn:
            for job in jobs:
                conn.execute(
                    """
                    INSERT INTO jobs (
                        spider, external_id, company, title, url, location,
                        posted_at, description, remote, employment_type,
                        experience_level, category, last_seen_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(spider, external_id) DO UPDATE SET
                        title = excluded.title,
                        url = excluded.url,
                        location = excluded.location,
                        posted_at = excluded.posted_at,
                        description = excluded.description,
                        remote = excluded.remote,
                        category = excluded.category,
                        last_seen_at = CURRENT_TIMESTAMP
                """,
                    (
                        spider,
                        job.external_id,
                        job.company,
                        job.title,
                        str(job.url),
                        job.location,
                        job.posted_at.isoformat() if job.posted_at else None,
                        job.description,
                        1 if job.remote else 0,
                        job.employment_type.value if job.employment_type else None,
                        job.experience_level.value if job.experience_level else None,
                        category,
                    ),
                )

    def load_jobs(self, spider: str, category: str = "filtered") -> list[JobPosting]:
        """Query the database and convert rows back into Pydantic models."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE spider = ? AND category = ? ORDER BY posted_at DESC",
                (spider, category),
            )
            rows = cursor.fetchall()

        jobs: list[JobPosting] = []
        for row in rows:
            data = dict(row)
            data["url"] = data["url"]
            data["remote"] = bool(data["remote"])
            data.pop("id")
            data.pop("discovered_at")
            data.pop("last_seen_at")
            data.pop("category")

            try:
                jobs.append(JobPosting(**data))
            except Exception:
                continue

        return jobs
