"""Google Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


def _default_target_levels() -> list[Literal["EARLY", "MID"]]:
    """Default value for target levels.

    Returns:
        list[str]: List containing 'EARLY'.
    """
    return ["EARLY"]


def _target_levels(levels: list[ExperienceLevel]) -> list[Literal["EARLY", "MID"]]:
    """Map internal experience levels to Google target levels.

    Args:
        levels: List of internal ExperienceLevel enums.

    Returns:
        list[str]: Unique list of Google target level strings ('EARLY', 'MID').
    """
    mapping: dict[ExperienceLevel, Literal["EARLY", "MID"]] = {
        ExperienceLevel.ENTRY: "EARLY",
        ExperienceLevel.MID: "MID",
        ExperienceLevel.SENIOR: "MID",
    }
    return list(dict.fromkeys(mapping[level] for level in levels))


def _employment_type(
    employment_types: list[EmploymentType],
) -> Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"]:
    """Map internal employment types to Google employment types.

    Args:
        employment_types: List of internal EmploymentType enums.

    Returns:
        str: The primary Google employment type string.
    """
    mapping: dict[EmploymentType, Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"]] = {
        EmploymentType.FULL_TIME: "FULL_TIME",
        EmploymentType.PART_TIME: "PART_TIME",
        EmploymentType.INTERNSHIP: "INTERN",
        EmploymentType.CONTRACT: "TEMPORARY",
    }
    first = employment_types[0] if employment_types else EmploymentType.FULL_TIME
    return mapping[first]


class GoogleParams(BaseParams):
    """Parameter model for Google Careers search URL construction."""

    location: list[str] = Field(default_factory=list, description="List of location names")
    target_level: list[Literal["EARLY", "MID"]] = Field(
        default_factory=_default_target_levels, description="Experience level filters"
    )
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"] = Field(
        default="FULL_TIME", description="Employment type filter"
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> GoogleParams:
        """Create GoogleParams from generic JobSearchCriteria.

        Args:
            search: The generic search criteria.

        Returns:
            GoogleParams: Populated Google parameters.
        """
        locations = search.locations
        if not locations and search.remote:
            locations = ["Remote"]
        return cls(
            location=locations,
            target_level=_target_levels(search.experience_levels),
            employment_type=_employment_type(search.employment_types),
        )

    def to_query(self) -> dict[str, Any]:
        """Convert parameters to a dictionary for query string generation.

        Returns:
            dict[str, Any]: Dictionary of search parameters.
        """
        return {
            "location": self.location,
            "target_level": self.target_level,
            "employment_type": self.employment_type,
        }
