"""Meta Careers request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, JobSearchCriteria


def _roles(employment_types: list[EmploymentType]) -> list[str]:
    if EmploymentType.FULL_TIME in employment_types:
        return ["Full time employment"]
    return []


class MetaParams(BaseParams):
    query: str = Field(default="software engineer")
    offices: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=lambda: ["Full time employment"])
    divisions: list[str] = Field(default_factory=list)
    leadership_levels: list[str] = Field(default_factory=list)
    saved_jobs: list[str] = Field(default_factory=list)
    saved_searches: list[str] = Field(default_factory=list)
    sub_teams: list[str] = Field(default_factory=list)
    teams: list[str] = Field(default_factory=list)
    is_leadership: bool = False
    is_remote_only: bool = False
    sort_by_new: bool = False
    results_per_page: int | None = None
    doc_id: str | None = None

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> MetaParams:
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
        return {"search_input": self.to_search_input()}
