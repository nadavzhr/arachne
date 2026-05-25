"""Meta Careers request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, JobSearchCriteria


def _roles(employment_types: list[EmploymentType]) -> list[str]:
    """Map employment types to Meta roles.

    Args:
        employment_types: List of employment types to map.

    Returns:
        list[str]: List of Meta role names.
    """
    if EmploymentType.FULL_TIME in employment_types:
        return ["Full time employment"]
    return []


class MetaParams(BaseParams):
    """Parameters for Meta Careers search.

    This model maps standard search criteria to the specific GraphQL
    input fields used by Meta Careers.
    """

    query: str = Field(
        default="software engineer",
        description="Search query string for job titles or keywords.",
    )
    offices: list[str] = Field(
        default_factory=list,
        description="List of office locations to filter by.",
    )
    roles: list[str] = Field(
        default_factory=lambda: ["Full time employment"],
        description="List of roles (employment types) to filter by.",
    )
    divisions: list[str] = Field(
        default_factory=list,
        description="List of divisions to filter by.",
    )
    leadership_levels: list[str] = Field(
        default_factory=list,
        description="List of leadership levels to filter by.",
    )
    saved_jobs: list[str] = Field(
        default_factory=list,
        description="List of saved job IDs.",
    )
    saved_searches: list[str] = Field(
        default_factory=list,
        description="List of saved search IDs.",
    )
    sub_teams: list[str] = Field(
        default_factory=list,
        description="List of sub-teams to filter by.",
    )
    teams: list[str] = Field(
        default_factory=list,
        description="List of teams to filter by.",
    )
    is_leadership: bool = Field(
        default=False,
        description="Whether to filter for leadership positions.",
    )
    is_remote_only: bool = Field(
        default=False,
        description="Whether to filter for remote-only positions.",
    )
    sort_by_new: bool = Field(
        default=False,
        description="Whether to sort results by newest first.",
    )
    results_per_page: int | None = Field(
        default=None,
        description="Number of results to return per page.",
    )
    doc_id: str | None = Field(
        default=None,
        description="Specific GraphQL document ID for the search query.",
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> MetaParams:
        """Create MetaParams from standard search criteria.

        Args:
            search: The standard job search criteria.

        Returns:
            MetaParams: Parameters tailored for Meta's GraphQL API.
        """
        offices = [
            location for location in search.locations if location.strip().lower() != "remote"
        ]
        return cls(
            query=search.title,
            offices=offices,
            roles=_roles(search.employment_types),
            is_remote_only=search.remote and not offices,
        )

    def to_search_input(self) -> dict[str, Any]:
        """Convert parameters to Meta's search_input GraphQL format.

        Returns:
            dict[str, Any]: The search_input dictionary for the GraphQL query.
        """
        return {
            "q": self.query,
            "divisions": self.divisions,
            "offices": self.offices,
            "roles": self.roles,
            "leadership_levels": self.leadership_levels,
            "saved_jobs": self.saved_jobs,
            "saved_searches": self.saved_searches,
            "sub_teams": self.sub_teams,
            "teams": self.teams,
            "is_leadership": self.is_leadership,
            "is_remote_only": self.is_remote_only,
            "sort_by_new": self.sort_by_new,
            "results_per_page": self.results_per_page,
        }

    def to_variables(self) -> dict[str, Any]:
        """Convert parameters to GraphQL variables.

        Returns:
            dict[str, Any]: The variables dictionary for the GraphQL query.
        """
        return {"search_input": self.to_search_input()}
