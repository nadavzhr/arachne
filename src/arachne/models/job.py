"""Models for the Arachne project (job-related types)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from arachne.models.schema import EmploymentType, ExperienceLevel


class JobPosting(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source: str
    company: str | None = None
    title: str
    url: HttpUrl
    location: str | None = None
    external_id: str | None = None
    posted_at: datetime | None = None
    description: str | None = None
    remote: bool = False
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
