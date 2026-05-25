"""Microsoft Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import ExperienceLevel, JobSearchCriteria


def _default_seniority() -> list[Literal["Entry", "Mid-Level", "Senior"]]:
    """Default seniority levels for Microsoft search.

    Returns:
        list[str]: Default list of seniority levels.
    """
    return ["Entry"]


def _primary_location(search: JobSearchCriteria) -> str:
    """Extract the primary location from search criteria.

    Args:
        search: Standard job search criteria.

    Returns:
        str: Primary location string or "Remote".
    """
    if not search.locations:
        return "Remote" if search.remote else ""
    return search.locations[0]


def _remote_flag(search: JobSearchCriteria) -> str:
    """Determine the remote filter flag.

    Args:
        search: Standard job search criteria.

    Returns:
        str: "1" for remote, "0" otherwise.
    """
    return "1" if search.remote else "0"


def _seniority(
    levels: list[ExperienceLevel],
) -> list[Literal["Entry", "Mid-Level", "Senior"]]:
    """Map experience levels to Microsoft seniority levels.

    Args:
        levels: List of experience levels to map.

    Returns:
        list[str]: List of Microsoft seniority levels.
    """
    mapping: dict[ExperienceLevel, Literal["Entry", "Mid-Level", "Senior"]] = {
        ExperienceLevel.ENTRY: "Entry",
        ExperienceLevel.MID: "Mid-Level",
        ExperienceLevel.SENIOR: "Senior",
    }
    return [mapping[level] for level in levels]


class MicrosoftParams(BaseParams):
    """Parameters for Microsoft Careers search.

    This model maps standard search criteria to the query parameters
    expected by Microsoft's job search API.
    """

    domain: str = Field(
        default="microsoft.com",
        description="The company domain for the search.",
    )
    query: str = Field(
        default="software engineer",
        description="Search query string for job titles or keywords.",
    )
    location: str = Field(
        default="",
        description="Location string to filter by.",
    )
    start: str = Field(
        default="0",
        description="Pagination start offset.",
    )
    filter_include_remote: str = Field(
        default="1",
        description="Whether to include remote positions ('1' or '0').",
    )
    hl: str = Field(
        default="en",
        description="Language code for the results.",
    )
    sort_by: Literal["distance", "relevance"] = Field(
        default="distance",
        description="Sorting criterion for results.",
    )
    filter_profession: str = Field(
        default="software engineering",
        description="Profession category to filter by.",
    )
    filter_seniority: list[Literal["Entry", "Mid-Level", "Senior"]] | None = Field(
        default_factory=_default_seniority,
        description="List of seniority levels to filter by.",
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> MicrosoftParams:
        """Create MicrosoftParams from standard search criteria.

        Args:
            search: The standard job search criteria.

        Returns:
            MicrosoftParams: Parameters tailored for Microsoft's API.
        """
        return cls(
            query=search.title,
            location=_primary_location(search),
            filter_include_remote=_remote_flag(search),
            filter_seniority=_seniority(search.experience_levels),
        )

    def to_query(self) -> dict[str, Any]:
        """Convert parameters to query string dictionary.

        Returns:
            dict[str, Any]: Dictionary of query parameters.
        """
        return {
            "domain": self.domain,
            "query": self.query,
            "location": self.location,
            "start": self.start,
            "filter_include_remote": self.filter_include_remote,
            "hl": self.hl,
            "sort_by": self.sort_by,
            "filter_profession": self.filter_profession,
            "filter_seniority": self.filter_seniority,
        }
