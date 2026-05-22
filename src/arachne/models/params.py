"""Typed parameter models for source-specific search configuration."""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import quote, urlencode

from pydantic import BaseModel, ConfigDict, Field


def build_query_string(params: dict[str, Any]) -> str:
    return urlencode(params, doseq=True, quote_via=quote)


def _default_microsoft_seniority() -> list[Literal["Entry", "Mid-Level", "Senior"]]:
    return ["Entry"]


def _default_google_target_levels() -> list[Literal["EARLY", "MID"]]:
    return ["EARLY"]


class BaseParams(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MicrosoftParams(BaseParams):
    domain: str = Field(default="microsoft.com")
    query: str = Field(default="software engineer")
    location: str = Field(default="Israel")
    start: str = Field(default="0")
    filter_include_remote: str = Field(default="1")
    hl: str = Field(default="en")
    sort_by: Literal["distance", "relevance"] = Field(default="distance")
    filter_profession: str = Field(default="software engineering")
    filter_seniority: list[Literal["Entry", "Mid-Level", "Senior"]] | None = Field(
        default_factory=_default_microsoft_seniority,
    )

    def to_query(self) -> dict[str, Any]:
        query: dict[str, Any] = {
            "domain": self.domain,
            "query": self.query,
            "location": self.location,
            "start": self.start,
            "filter_include_remote": self.filter_include_remote,
            "hl": self.hl,
            "sort_by": self.sort_by,
            "filter_profession": self.filter_profession,
        }
        if self.filter_seniority is not None:
            query["filter_seniority"] = ",".join(self.filter_seniority)
        return query


class NvidiaParams(BaseParams):
    domain: str = Field(default="nvidia.com")
    query: str = Field(default="software engineering")
    location: str = Field(default="Israel")
    start: str = Field(default="0")
    filter_include_remote: str = Field(default="1")
    filter_job_category: str = Field(default="engineering")
    filter_job_type: str = Field(default="regular employee")
    filter_time_type: str = Field(default="full time")
    sort_by: Literal["distance", "relevance"] = Field(default="relevance")
    pid: str | None = None

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


class AmazonParams(BaseParams):
    category: list[str] = Field(default_factory=lambda: ["software-development"])
    schedule_type_id: list[str] = Field(default_factory=lambda: ["Full-Time"])
    normalized_country_code: list[str] = Field(default_factory=lambda: ["ISR"])
    industry_experience: list[str] = Field(default_factory=lambda: ["one_to_three_years"])
    loc_query: str = Field(default="Israel")
    result_limit: str = Field(default="10")
    offset: str = Field(default="0")
    sort: str = Field(default="relevant")

    def to_query(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "result_limit": self.result_limit,
            "sort": self.sort,
            "category[]": self.category,
            "schedule_type_id[]": self.schedule_type_id,
            "normalized_country_code[]": self.normalized_country_code,
            "industry_experience[]": self.industry_experience,
            "loc_query": self.loc_query,
        }


class GoogleParams(BaseParams):
    location: list[str] = Field(default_factory=lambda: ["Israel"])
    target_level: list[Literal["EARLY", "MID"]] = Field(
        default_factory=_default_google_target_levels,
    )
    employment_type: Literal["FULL_TIME"] = Field(default="FULL_TIME")

    def to_query(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "target_level": self.target_level,
            "employment_type": self.employment_type,
        }


class AppleParams(BaseParams):
    location: list[str] = Field(default_factory=lambda: ["israel-ISR"])
    key: str = Field(default="software engineer")
    language: str = Field(default="en-il")

    def to_query(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "key": self.key,
            "language": self.language,
        }


class MetaParams(BaseParams):
    query: str = Field(default="software engineer")
    offices: list[str] = Field(default_factory=lambda: ["Tel Aviv, Israel"])
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
