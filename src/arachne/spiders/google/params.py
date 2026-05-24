"""Google Careers request parameter mapping."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria


def _default_target_levels() -> list[Literal["EARLY", "MID"]]:
    return ["EARLY"]


def _target_levels(levels: list[ExperienceLevel]) -> list[Literal["EARLY", "MID"]]:
    mapping: dict[ExperienceLevel, Literal["EARLY", "MID"]] = {
        ExperienceLevel.ENTRY: "EARLY",
        ExperienceLevel.MID: "MID",
        ExperienceLevel.SENIOR: "MID",
    }
    return list(dict.fromkeys(mapping[level] for level in levels))


def _employment_type(
    employment_types: list[EmploymentType],
) -> Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"]:
    mapping: dict[EmploymentType, Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"]] = {
        EmploymentType.FULL_TIME: "FULL_TIME",
        EmploymentType.PART_TIME: "PART_TIME",
        EmploymentType.INTERNSHIP: "INTERN",
        EmploymentType.CONTRACT: "TEMPORARY",
    }
    first = employment_types[0] if employment_types else EmploymentType.FULL_TIME
    return mapping[first]


class GoogleParams(BaseParams):
    location: list[str] = Field(default_factory=list)
    target_level: list[Literal["EARLY", "MID"]] = Field(default_factory=_default_target_levels)
    employment_type: Literal["FULL_TIME", "PART_TIME", "INTERN", "TEMPORARY"] = Field(
        default="FULL_TIME"
    )

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> GoogleParams:
        locations = search.locations
        if not locations and search.remote:
            locations = ["Remote"]
        return cls(
            location=locations,
            target_level=_target_levels(search.experience_levels),
            employment_type=_employment_type(search.employment_types),
        )

    def to_query(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "target_level": self.target_level,
            "employment_type": self.employment_type,
        }
