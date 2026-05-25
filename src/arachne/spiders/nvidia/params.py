"""NVIDIA Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


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


def _job_types(levels: list[ExperienceLevel]) -> list[str]:
    """Map experience levels to NVIDIA job types.

    Args:
        levels: List of experience levels to map.

    Returns:
        list[str]: List of NVIDIA job type names.
    """
    values: list[str] = []
    if ExperienceLevel.ENTRY in levels:
        values.append("new college graduate")
    if (
        ExperienceLevel.ENTRY in levels
        or ExperienceLevel.MID in levels
        or ExperienceLevel.SENIOR in levels
    ):
        values.append("regular employee")
    return values or ["new college graduate"]


def _time_type(employment_types: list[EmploymentType]) -> str:
    """Map employment types to NVIDIA time types.

    Args:
        employment_types: List of employment types to map.

    Returns:
        str: NVIDIA time type (e.g., "full time", "part time").
    """
    if EmploymentType.FULL_TIME in employment_types:
        return "full time"
    if EmploymentType.PART_TIME in employment_types:
        return "part time"
    return "full time"


class NvidiaParams(BaseParams):
    """Parameters for NVIDIA Careers search.

    This model maps standard search criteria to the query parameters
    expected by NVIDIA's job search API.
    """

    domain: str = Field(
        default="nvidia.com",
        description="The company domain for the search.",
    )
    query: str = Field(
        default="software engineering",
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
    filter_job_category: str = Field(
        default="engineering",
        description="Job category to filter by.",
    )
    filter_job_type: list[str] = Field(
        default_factory=lambda: ["new college graduate"],
        description="List of job types (e.g., 'regular employee') to filter by.",
    )
    filter_time_type: str = Field(
        default="full time",
        description="Employment time type (e.g., 'full time').",
    )
    sort_by: Literal["distance", "relevance"] = Field(
        default="relevance",
        description="Sorting criterion for results.",
    )
    pid: str | None = Field(
        default=None,
        description="Optional partner ID for the search.",
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> NvidiaParams:
        """Create NvidiaParams from standard search criteria.

        Args:
            search: The standard job search criteria.

        Returns:
            NvidiaParams: Parameters tailored for NVIDIA's API.
        """
        return cls(
            query=search.title,
            location=_primary_location(search),
            filter_include_remote=_remote_flag(search),
            filter_job_type=_job_types(search.experience_levels),
            filter_time_type=_time_type(search.employment_types),
        )

    def to_query(self) -> dict[str, Any]:
        """Convert parameters to query string dictionary.

        Returns:
            dict[str, Any]: Dictionary of query parameters.
        """
        query: dict[str, Any] = {
            "domain": self.domain,
            "query": self.query,
            "location": self.location,
            "start": self.start,
            "filter_include_remote": self.filter_include_remote,
            "filter_job_category": self.filter_job_category,
            "filter_job_type": self.filter_job_type,
            "filter_time_type": self.filter_time_type,
            "sort_by": self.sort_by,
        }
        if self.pid is not None:
            query["pid"] = self.pid
        return query
