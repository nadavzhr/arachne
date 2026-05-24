"""Microsoft Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import ExperienceLevel, JobSearchCriteria


def _default_seniority() -> list[Literal["Entry", "Mid-Level", "Senior"]]:
    return ["Entry"]


def _primary_location(search: JobSearchCriteria) -> str:
    if not search.locations:
        return "Remote" if search.remote else ""
    return search.locations[0]


def _remote_flag(search: JobSearchCriteria) -> str:
    return "1" if search.remote else "0"


def _seniority(
    levels: list[ExperienceLevel],
) -> list[Literal["Entry", "Mid-Level", "Senior"]]:
    mapping: dict[ExperienceLevel, Literal["Entry", "Mid-Level", "Senior"]] = {
        ExperienceLevel.ENTRY: "Entry",
        ExperienceLevel.MID: "Mid-Level",
        ExperienceLevel.SENIOR: "Senior",
    }
    return [mapping[level] for level in levels]


class MicrosoftParams(BaseParams):
    domain: str = Field(default="microsoft.com")
    query: str = Field(default="software engineer")
    location: str = Field(default="")
    start: str = Field(default="0")
    filter_include_remote: str = Field(default="1")
    hl: str = Field(default="en")
    sort_by: Literal["distance", "relevance"] = Field(default="distance")
    filter_profession: str = Field(default="software engineering")
    filter_seniority: list[Literal["Entry", "Mid-Level", "Senior"]] | None = Field(
        default_factory=_default_seniority
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> MicrosoftParams:
        return cls(
            query=search.title,
            location=_primary_location(search),
            filter_include_remote=_remote_flag(search),
            filter_seniority=_seniority(search.experience_levels),
        )

    def to_query(self) -> dict[str, Any]:
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
