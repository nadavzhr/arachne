"""Models for the Arachne project (job-related types)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from arachne.models.schema import EmploymentType, ExperienceLevel


class JobPosting(BaseModel):
    """Represents a normalized job posting from any supported provider."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    spider: str = Field(..., description="Name of the spider that discovered this posting")
    company: str | None = Field(default=None, description="Name of the hiring company")
    title: str = Field(..., description="Job title")
    url: HttpUrl = Field(..., description="Direct URL to the job posting")
    location: str | None = Field(default=None, description="Geographic location of the job")
    external_id: str | None = Field(default=None, description="Provider-specific unique identifier")
    posted_at: datetime | None = Field(
        default=None, description="Timestamp when the job was posted"
    )
    description: str | None = Field(
        default=None, description="Full or partial job description/requirements"
    )
    remote: bool = Field(default=False, description="Whether the position is remote-friendly")
    employment_type: EmploymentType | None = Field(
        default=None, description="Type of employment (e.g., full-time, contract)"
    )
    experience_level: ExperienceLevel | None = Field(
        default=None, description="Required experience level (e.g., entry, senior)"
    )
