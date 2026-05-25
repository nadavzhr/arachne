"""SQLite implementation of job storage for persistence and deduplication."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from arachne.models.job import JobPosting
from arachne.storage.base import JobStorage


class SqliteJobStorage(JobStorage):
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
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection to the SQLite database with dictionary-like rows."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create the necessary tables if they do not exist.

        SQL Concepts:
        - CREATE TABLE: Defines the blueprint.
        - PRIMARY KEY: Unique identifier for each row.
        - UNIQUE: Ensures no two rows have the same combination of spider + external_id.
        - DEFAULT CURRENT_TIMESTAMP: Automatically sets the time when a row is created.
        """
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
            # Table for raw payloads to keep them separate from structured data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raw_data (
                    spider TEXT PRIMARY KEY,
                    payload TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_jobs(
        self, spider: str, jobs: Sequence[JobPosting], category: str = "filtered"
    ) -> None:
        """Save job postings using an UPSERT (Update or Insert) strategy.

        SQL Concepts:
        - INSERT INTO ... ON CONFLICT: This is the "Upsert". It tries to insert,
          but if it finds a matching (spider, external_id), it updates the existing row.
        """
        with self._get_connection() as conn:
            for job in jobs:
                # We use '?' placeholders to prevent SQL Injection (Security best practice)
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

    def save_raw(self, spider: str, raw_payload: Any) -> None:
        """Save the raw JSON payload as a string."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO raw_data (spider, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(spider) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (spider, json.dumps(raw_payload)),
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
            # sqlite3.Row acts like a dictionary
            data = dict(row)
            # Convert SQLite types back to Pydantic-friendly types
            data["url"] = data["url"]
            data["remote"] = bool(data["remote"])
            # Remove internal DB columns not needed by the model
            data.pop("id")
            data.pop("discovered_at")
            data.pop("last_seen_at")
            data.pop("category")

            try:
                jobs.append(JobPosting(**data))
            except Exception:
                continue

        return jobs
