"""Normalization helpers moved under utils package."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from pydantic import ValidationError

from arachne.models.job import JobPosting

logger = logging.getLogger(__name__)


_TITLE_KEYS = ("title", "position", "name", "jobTitle")
_URL_KEYS = ("url", "applyUrl", "jobUrl", "link", "url_next_step", "positionUrl")
_LOCATION_KEYS = ("location", "locations", "locationName")
_ID_KEYS = ("id", "externalId", "jobId")
_DESCRIPTION_KEYS = ("description", "desc", "summary")
_POSTED_KEYS = ("posted_at", "postedAt", "datePosted", "posted", "posted_date")
_REMOTE_KEYS = ("remote", "isRemote")


def _first_str(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for k in keys:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        # sometimes location is nested dict
        if isinstance(v, dict):
            name = v.get("name") or v.get("label")
            if isinstance(name, str) and name.strip():
                return name.strip()
    return None


def _first_any(record: dict[str, Any], keys: tuple[str, ...]) -> Any | None:
    for k in keys:
        if k in record:
            return record[k]
    return None


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            try:
                # try common short formats
                return datetime.strptime(value, "%Y-%m-%d")
            except Exception:
                return None
    return None


def first_str(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    return _first_str(record, keys)


def build_url(base: str | None, suffix: str | None) -> str | None:
    if not suffix:
        return None
    s = suffix.strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s
    if not base:
        return None
    return base.rstrip("/") + "/" + s.lstrip("/")


def try_parse_json_string(value: Any) -> Any:
    """If value is a JSON-encoded string, parse it and return parsed value, else return original."""
    if isinstance(value, str) and value.strip().startswith("{"):
        try:
            import json

            return json.loads(value)
        except Exception:
            return value
    return value


def normalize_record(source: str, company: str | None, record: dict[str, Any]) -> JobPosting:
    title = _first_str(record, _TITLE_KEYS) or ""
    url = _first_str(record, _URL_KEYS) or ""
    location = _first_str(record, _LOCATION_KEYS)
    external_id = _first_any(record, _ID_KEYS)
    description = _first_str(record, _DESCRIPTION_KEYS)
    posted_at = _parse_datetime(_first_any(record, _POSTED_KEYS))
    remote = bool(_first_any(record, _REMOTE_KEYS))

    payload: dict[str, Any] = {
        "source": source,
        "company": company,
        "title": title,
        "url": url,
        "location": location,
        "external_id": str(external_id) if external_id is not None else None,
        "posted_at": posted_at,
        "description": description,
        "remote": remote,
    }

    return JobPosting(**payload)


def normalize_records(source: str, raw: Any, company: str | None = None) -> list[JobPosting]:
    results: list[JobPosting] = []
    items: list[dict[str, Any]]
    if raw is None:
        return results
    if isinstance(raw, list):
        items = [x for x in raw if isinstance(x, dict)]
    elif isinstance(raw, dict):
        # Some APIs return {'jobs': [...]} or similar
        if "jobs" in raw and isinstance(raw["jobs"], list):
            items = [x for x in raw["jobs"] if isinstance(x, dict)]
        else:
            items = [raw]
    else:
        return results

    for rec in items:
        try:
            jp = normalize_record(source, company, rec)
            results.append(jp)
        except ValidationError as exc:
            logger.debug("Skipping record from %s due to validation error: %s", source, exc)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Unexpected error normalizing record from %s: %s", source, exc)

    return results
