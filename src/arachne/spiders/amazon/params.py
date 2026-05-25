"""Amazon Jobs request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


def _primary_location(search: JobSearchCriteria) -> str:
    """Extract the primary location string for Amazon's loc_query.

    Args:
        search: The job search criteria.

    Returns:
        str: The primary location name or 'Remote' if applicable.
    """
    if not search.locations:
        return "Remote" if search.remote else ""
    return search.locations[0]


def _country_codes(locations: list[str]) -> list[str]:
    """Map location strings to Amazon-specific country codes (e.g., 'ISR', 'USA').

    Args:
        locations: List of location strings.

    Returns:
        list[str]: Unique list of Amazon country codes.
    """
    country_codes = {
        "israel": "ISR",
        "united states": "USA",
        "usa": "USA",
        "us": "USA",
        "canada": "CAN",
        "united kingdom": "GBR",
        "uk": "GBR",
    }
    codes: list[str] = []
    for location in locations:
        normalized = location.lower().split(",")[-1].strip()
        if normalized in country_codes:
            codes.append(country_codes[normalized])
    return list(dict.fromkeys(codes))


def _schedule_types(employment_types: list[EmploymentType]) -> list[str]:
    """Map internal employment types to Amazon schedule types.

    Args:
        employment_types: List of internal EmploymentType enums.

    Returns:
        list[str]: List of Amazon schedule type strings.
    """
    mapping = {
        EmploymentType.FULL_TIME: "Full-Time",
        EmploymentType.PART_TIME: "Part-Time",
        EmploymentType.CONTRACT: "Contractor",
        EmploymentType.INTERNSHIP: "Internship",
    }
    return list(dict.fromkeys(mapping[value] for value in employment_types)) or ["Full-Time"]


def _experience_filters(levels: list[ExperienceLevel]) -> list[str]:
    """Map internal experience levels to Amazon industry experience filters.

    Args:
        levels: List of internal ExperienceLevel enums.

    Returns:
        list[str]: List of Amazon experience filter strings.
    """
    mapping = {
        ExperienceLevel.ENTRY: "one_to_three_years",
        ExperienceLevel.MID: "three_to_five_years",
        ExperienceLevel.SENIOR: "five_to_ten_years",
    }
    return list(dict.fromkeys(mapping[value] for value in levels)) or ["one_to_three_years"]


class AmazonParams(BaseParams):
    """Parameter model for Amazon Jobs API requests."""

    base_query: str = Field(default="software engineer", description="Search keywords")
    category: list[str] = Field(
        default_factory=lambda: ["software-development"], description="Job category filters"
    )
    schedule_type_id: list[str] = Field(
        default_factory=lambda: ["Full-Time"], description="Employment type filters"
    )
    normalized_country_code: list[str] = Field(
        default_factory=list, description="Target country code filters"
    )
    industry_experience: list[str] = Field(
        default_factory=lambda: ["one_to_three_years"], description="Experience level filters"
    )
    loc_query: str = Field(default="", description="Location search query")
    result_limit: str = Field(default="100", description="Number of results to return")
    offset: str = Field(default="0", description="Pagination offset")
    sort: str = Field(default="relevant", description="Sorting criteria")

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> AmazonParams:
        """Create AmazonParams from generic JobSearchCriteria.

        Args:
            search: The generic search criteria.

        Returns:
            AmazonParams: Populated Amazon parameters.
        """
        return cls(
            base_query=search.title,
            schedule_type_id=_schedule_types(search.employment_types),
            normalized_country_code=_country_codes(search.locations),
            industry_experience=_experience_filters(search.experience_levels),
            loc_query=_primary_location(search),
        )

    def to_query(self) -> dict[str, Any]:
        """Convert parameters to a dictionary suitable for URL query strings.

        Returns:
            dict[str, Any]: Dictionary of query parameters including list handling for Amazon's API.
        """
        return {
            "base_query": self.base_query,
            "offset": self.offset,
            "result_limit": self.result_limit,
            "sort": self.sort,
            "category[]": self.category,
            "schedule_type_id[]": self.schedule_type_id,
            "normalized_country_code[]": self.normalized_country_code,
            "industry_experience[]": self.industry_experience,
            "loc_query": self.loc_query,
        }
