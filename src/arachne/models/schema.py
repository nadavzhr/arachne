"""Shared provider-neutral schema used by configuration and job models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmploymentType(StrEnum):
    """Standardized employment types across all providers."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class ExperienceLevel(StrEnum):
    """Standardized experience levels across all providers."""

    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"


def _default_employment_types() -> list[EmploymentType]:
    """Default value for employment types filter.

    Returns:
        list[EmploymentType]: List containing only FULL_TIME.
    """
    return [EmploymentType.FULL_TIME]


def _default_experience_levels() -> list[ExperienceLevel]:
    """Default value for experience levels filter.

    Returns:
        list[ExperienceLevel]: List containing only ENTRY.
    """
    return [ExperienceLevel.ENTRY]


class KeywordFilter(BaseModel):
    """Filter for a specific text field using include/exclude lists."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    include_keywords: list[str] = Field(
        default_factory=list, description="Keywords that must be present (case-insensitive)"
    )
    exclude_keywords: list[str] = Field(
        default_factory=list, description="Keywords that must NOT be present (case-insensitive)"
    )

    @field_validator("include_keywords", "exclude_keywords")
    @classmethod
    def _drop_empty_values(cls, values: list[str]) -> list[str]:
        """Remove empty strings from the list of filter values.

        Args:
            values: List of string filter values.

        Returns:
            list[str]: Filtered list containing only non-empty strings.
        """
        return [value for value in values if value]


class Filters(BaseModel):
    """Post-normalization filters that operate on the shared job schema."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: KeywordFilter = Field(
        default_factory=KeywordFilter, description="Filters for the job title"
    )
    location: KeywordFilter = Field(
        default_factory=KeywordFilter, description="Filters for the job location"
    )
    company: KeywordFilter = Field(
        default_factory=KeywordFilter, description="Filters for the hiring company"
    )
    description: KeywordFilter = Field(
        default_factory=KeywordFilter, description="Filters for the job description"
    )


class JobSearchCriteria(BaseModel):
    """Provider-neutral search contract exposed by configuration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(default="software engineer", description="Search query for job titles")
    locations: list[str] = Field(
        default_factory=list, description="Target geographic locations for the search"
    )
    remote: bool = Field(
        default=True, description="Whether to specifically search for remote roles"
    )
    employment_types: list[EmploymentType] = Field(
        default_factory=_default_employment_types,
        description="List of employment types to include in the search",
    )
    experience_levels: list[ExperienceLevel] = Field(
        default_factory=_default_experience_levels,
        description="List of experience levels to include in the search",
    )

    @field_validator("locations")
    @classmethod
    def _drop_empty_locations(cls, values: list[str]) -> list[str]:
        """Remove empty strings from the list of locations.

        Args:
            values: List of location strings.

        Returns:
            list[str]: Filtered list containing only non-empty strings.
        """
        return [value for value in values if value]
