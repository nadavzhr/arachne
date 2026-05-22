"""Shared provider-neutral schema used by configuration and job models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class ExperienceLevel(StrEnum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"


def _default_employment_types() -> list[EmploymentType]:
    return [EmploymentType.FULL_TIME]


def _default_experience_levels() -> list[ExperienceLevel]:
    return [ExperienceLevel.ENTRY, ExperienceLevel.MID]


class Filters(BaseModel):
    """Post-normalization filters that operate on the shared job schema."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    include_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)

    @field_validator("include_keywords", "exclude_keywords", "locations")
    @classmethod
    def _drop_empty_values(cls, values: list[str]) -> list[str]:
        return [value for value in values if value]


class JobSearchCriteria(BaseModel):
    """Provider-neutral search contract exposed by configuration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = "software engineer"
    locations: list[str] = Field(default_factory=lambda: ["Israel"])
    remote: bool = True
    employment_types: list[EmploymentType] = Field(default_factory=_default_employment_types)
    experience_levels: list[ExperienceLevel] = Field(default_factory=_default_experience_levels)

    @field_validator("locations")
    @classmethod
    def _drop_empty_locations(cls, values: list[str]) -> list[str]:
        return [value for value in values if value]
