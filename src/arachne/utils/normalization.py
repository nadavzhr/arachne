"""Normalization helpers moved under utils package."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from pydantic import ValidationError

from arachne.models.job import JobPosting
from arachne.models.schema import EmploymentType, ExperienceLevel

logger = logging.getLogger(__name__)


_TITLE_KEYS = ("title", "position", "name", "jobTitle")
_URL_KEYS = ("url", "applyUrl", "jobUrl", "link", "url_next_step", "positionUrl")
_LOCATION_KEYS = ("location", "locations", "locationName")
_ID_KEYS = ("id", "externalId", "jobId")
_DESCRIPTION_KEYS = ("description", "desc", "summary")
_POSTED_KEYS = ("posted_at", "postedAt", "datePosted", "posted", "posted_date")
_REMOTE_KEYS = ("remote", "isRemote")
_EMPLOYMENT_TYPE_KEYS = (
    "employment_type",
    "employmentType",
    "jobType",
    "timeType",
    "schedule_type",
)
_EXPERIENCE_LEVEL_KEYS = ("experience_level", "experienceLevel", "seniority", "level")


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
                return ", ".join(dict.fromkeys(names))
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


def _as_lower_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(_as_lower_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_lower_text(item) for item in value.values())
    return str(value).strip().lower()


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "remote"}
    return bool(value)


def _parse_employment_type(value: Any) -> EmploymentType | None:
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


def _parse_experience_level(value: Any) -> ExperienceLevel | None:
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

# region Public API

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
    remote = _parse_bool(_first_any(record, _REMOTE_KEYS))
    employment_type = _parse_employment_type(_first_any(record, _EMPLOYMENT_TYPE_KEYS))
    experience_level = _parse_experience_level(_first_any(record, _EXPERIENCE_LEVEL_KEYS))

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
        "employment_type": employment_type,
        "experience_level": experience_level,
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
