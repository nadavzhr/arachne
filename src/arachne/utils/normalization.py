"""Normalization and parsing utilities for job records."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, urlencode

from arachne.models.schema import EmploymentType, ExperienceLevel

logger = logging.getLogger(__name__)


def build_query_string(params: Mapping[str, Any]) -> str:
    """Format a dictionary as a URL query string.

    Args:
        params: Dictionary of query parameters.

    Returns:
        str: URL-encoded query string.
    """
    return urlencode(params, doseq=True, quote_via=quote)


def first_str(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    """Return the first non-empty string value found in the given keys.

    Handles nested dictionaries (extracting 'name' or 'label') and lists
    (joining non-empty strings).

    Args:
        record: The dictionary to search.
        keys: A tuple of keys to check in order.

    Returns:
        str | None: The first found string value, or None if no match.
    """
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        # handle nested dicts (common for locations)
        if isinstance(v, dict):
            name = v.get("name") or v.get("label")
            if isinstance(name, str) and name.strip():
                return name.strip()
        # handle lists
        if isinstance(v, list):
            names: list[str] = []
            for item in v:
                if isinstance(item, str) and item.strip():
                    names.append(item.strip())
                    continue
                if isinstance(item, dict):
                    name = item.get("name") or item.get("label")
                    if isinstance(name, str) and name.strip():
                        names.append(name.strip())
            if names:
                return " | ".join(dict.fromkeys(names))
    return None


def first_any(record: dict[str, Any], keys: tuple[str, ...]) -> Any | None:
    """Return the first value found for the given keys.

    Args:
        record: The dictionary to search.
        keys: A tuple of keys to check in order.

    Returns:
        Any | None: The first found value, or None if no match.
    """
    for k in keys:
        if k in record:
            return record[k]
    return None


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
        except ValueError, OverflowError:
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


def _as_lower_text(value: Any) -> str:
    """Internal helper to convert various types to lowercase stripped string.

    Args:
        value: The value to convert.

    Returns:
        str: Lowercase string representation.
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(_as_lower_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_lower_text(item) for item in value.values())
    return str(value).strip().lower()


def parse_bool(value: Any) -> bool:
    """Coerce various values into a boolean.

    Args:
        value: The value to coerce.

    Returns:
        bool: Coerced boolean value.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "remote"}
    return bool(value)


def parse_employment_type(value: Any) -> EmploymentType | None:
    """Infer EmploymentType from raw text.

    Args:
        value: Raw text to analyze.

    Returns:
        EmploymentType | None: The inferred employment type, or None.
    """
    text = _as_lower_text(value)
    if not text:
        return None
    if "intern" in text:
        return EmploymentType.INTERNSHIP
    if "contract" in text:
        return EmploymentType.CONTRACT
    if "part" in text:
        return EmploymentType.PART_TIME
    if "full" in text:
        return EmploymentType.FULL_TIME
    return None


def parse_experience_level(value: Any) -> ExperienceLevel | None:
    """Infer ExperienceLevel from raw text.

    Args:
        value: Raw text to analyze.

    Returns:
        ExperienceLevel | None: The inferred experience level, or None.
    """
    text = _as_lower_text(value)
    if not text:
        return None
    if "senior" in text or "sr." in text or "sr " in text:
        return ExperienceLevel.SENIOR
    if "mid" in text or "regular" in text:
        return ExperienceLevel.MID
    if "entry" in text or "early" in text or "graduate" in text or "junior" in text:
        return ExperienceLevel.ENTRY
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
