"""Amazon Jobs request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


def _primary_location(search: JobSearchCriteria) -> str:
    if not search.locations:
        return "Remote" if search.remote else ""
    return search.locations[0]


def _country_codes(locations: list[str]) -> list[str]:
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
    mapping = {
        EmploymentType.FULL_TIME: "Full-Time",
        EmploymentType.PART_TIME: "Part-Time",
        EmploymentType.CONTRACT: "Contractor",
        EmploymentType.INTERNSHIP: "Internship",
    }
    return list(dict.fromkeys(mapping[value] for value in employment_types)) or ["Full-Time"]


def _experience_filters(levels: list[ExperienceLevel]) -> list[str]:
    mapping = {
        ExperienceLevel.ENTRY: "one_to_three_years",
        ExperienceLevel.MID: "three_to_five_years",
        ExperienceLevel.SENIOR: "five_to_ten_years",
    }
    return list(dict.fromkeys(mapping[value] for value in levels)) or ["one_to_three_years"]


class AmazonParams(BaseParams):
    base_query: str = Field(default="software engineer")
    category: list[str] = Field(default_factory=lambda: ["software-development"])
    schedule_type_id: list[str] = Field(default_factory=lambda: ["Full-Time"])
    normalized_country_code: list[str] = Field(default_factory=list)
    industry_experience: list[str] = Field(default_factory=lambda: ["one_to_three_years"])
    loc_query: str = Field(default="")
    result_limit: str = Field(default="100")
    offset: str = Field(default="0")
    sort: str = Field(default="relevant")

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> AmazonParams:
        return cls(
            base_query=search.title,
            schedule_type_id=_schedule_types(search.employment_types),
            normalized_country_code=_country_codes(search.locations),
            industry_experience=_experience_filters(search.experience_levels),
            loc_query=_primary_location(search),
        )

    def to_query(self) -> dict[str, Any]:
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
