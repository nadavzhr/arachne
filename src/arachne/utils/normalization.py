"""Normalization and parsing utilities for job records."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


def parse_datetime(value: Any) -> datetime | None:
    """Parse a date string or Unix timestamp into a datetime object.

    Supports datetime objects, numeric timestamps (seconds or milliseconds),
    ISO format strings, and short 'YYYY-MM-DD' strings.

    Args:
        value: The value to parse.

    Returns:
        datetime | None: The parsed datetime object in UTC, or None if parsing fails.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        ts = float(value)
        # Handle milliseconds
        if ts > 1_000_000_000_000:
            ts /= 1000
        try:
            return datetime.fromtimestamp(ts, tz=UTC)
        except (ValueError, OverflowError):
            return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                # try common short format
                return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                return None
    return None


def build_url(base: str | None, suffix: str | None) -> str | None:
    """Combine a base URL and a suffix into a full URL.

    Args:
        base: The base URL.
        suffix: The URL suffix or relative path.

    Returns:
        str | None: The combined full URL, or None if base/suffix is missing.
    """
    if not suffix:
        return None
    s = suffix.strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if not base:
        return None
    return base.rstrip("/") + "/" + s.lstrip("/")


def try_parse_json_string(value: Any) -> Any:
    """If value is a JSON-encoded string, parse it.

    Args:
        value: The value to attempt parsing.

    Returns:
        Any: Parsed JSON data if successful, otherwise original value.
    """
    if isinstance(value, str) and value.strip().startswith("{"):
        try:
            import json

            return json.loads(value)
        except Exception:
            return value
    return value
