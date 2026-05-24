"""NVIDIA Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


def _primary_location(search: JobSearchCriteria) -> str:
    if not search.locations:
        return "Remote" if search.remote else ""
    return search.locations[0]


def _remote_flag(search: JobSearchCriteria) -> str:
    return "1" if search.remote else "0"


def _job_types(levels: list[ExperienceLevel]) -> list[str]:
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
    if EmploymentType.FULL_TIME in employment_types:
        return "full time"
    if EmploymentType.PART_TIME in employment_types:
        return "part time"
    return "full time"


class NvidiaParams(BaseParams):
    domain: str = Field(default="nvidia.com")
    query: str = Field(default="software engineering")
    location: str = Field(default="")
    start: str = Field(default="0")
    filter_include_remote: str = Field(default="1")
    filter_job_category: str = Field(default="engineering")
    filter_job_type: list[str] = Field(default_factory=lambda: ["new college graduate"])
    filter_time_type: str = Field(default="full time")
    sort_by: Literal["distance", "relevance"] = Field(default="relevance")
    pid: str | None = None

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> NvidiaParams:
        return cls(
            query=search.title,
            location=_primary_location(search),
            filter_include_remote=_remote_flag(search),
            filter_job_type=_job_types(search.experience_levels),
            filter_time_type=_time_type(search.employment_types),
        )

    def to_query(self) -> dict[str, Any]:
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
