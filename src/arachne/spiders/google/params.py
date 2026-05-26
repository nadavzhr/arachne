"""Google Careers request parameter mapping."""

from __future__ import annotations

import typing

import pydantic

import arachne.models.params as params_models
import arachne.models.schema as schema_models

DEFAULT_LANGUAGE = "en-US"
DEFAULT_FILTER_FLAGS = [1]  # Default to Early
TARGET_LEVEL_FLAGS = {
    "INTERN": 0,
    "EARLY": 1,
    "MID": 2,
    "ADVANCED": 3,
    "DIRECTOR": 4,
}
EMPLOYMENT_TYPE_FLAGS = {
    schema_models.EmploymentType.FULL_TIME: 1,
    schema_models.EmploymentType.PART_TIME: 3,
    schema_models.EmploymentType.CONTRACT: 2,  # Best guess for Temporary/Contract
    schema_models.EmploymentType.INTERNSHIP: 4,  # Hypothetical
}


def _default_target_levels() -> list[
    typing.Literal["INTERN", "EARLY", "MID", "ADVANCED", "DIRECTOR"]
]:
    """Default value for target levels.

    Returns:
        list[str]: List containing 'EARLY'.
    """
    return ["EARLY"]


def _target_levels(
    levels: list[schema_models.ExperienceLevel],
) -> list[typing.Literal["INTERN", "EARLY", "MID", "ADVANCED", "DIRECTOR"]]:
    """Map internal experience levels to Google target levels."""
    mapping: dict[
        schema_models.ExperienceLevel,
        typing.Literal["INTERN", "EARLY", "MID", "ADVANCED", "DIRECTOR"],
    ] = {
        schema_models.ExperienceLevel.ENTRY: "EARLY",
        schema_models.ExperienceLevel.MID: "MID",
        schema_models.ExperienceLevel.SENIOR: "ADVANCED",
    }
    return list(dict.fromkeys(mapping[level] for level in levels))


def _experience_flags(
    levels: list[typing.Literal["INTERN", "EARLY", "MID", "ADVANCED", "DIRECTOR"]],
) -> list[int]:
    """Get the numerical flags for experience levels (Index 16)."""
    return [TARGET_LEVEL_FLAGS[level] for level in levels if level in TARGET_LEVEL_FLAGS]


def _employment_flags(
    employment_types: list[schema_models.EmploymentType],
) -> list[int]:
    """Get the numerical flags for employment types (Index 3)."""
    flags = [EMPLOYMENT_TYPE_FLAGS[et] for et in employment_types if et in EMPLOYMENT_TYPE_FLAGS]
    return flags or [1]  # Default to Full-time if none specified


class GoogleParams(params_models.BaseParams):
    """Parameter model for Google Careers search URL construction."""

    location: list[str] = pydantic.Field(default_factory=list, description="List of location names")
    target_level: list[typing.Literal["INTERN", "EARLY", "MID", "ADVANCED", "DIRECTOR"]] = (
        pydantic.Field(
            default_factory=_default_target_levels, description="Experience level filters"
        )
    )
    employment_types: list[schema_models.EmploymentType] = pydantic.Field(
        default_factory=list, description="Employment type filters"
    )
    remote: bool = pydantic.Field(default=False, description="Remote filter")

    @classmethod
    def from_search(cls, search: schema_models.JobSearchCriteria) -> GoogleParams:
        """Create GoogleParams from generic JobSearchCriteria.

        Args:
            search: The generic search criteria.

        Returns:
            GoogleParams: Populated Google parameters.
        """
        return cls(
            location=search.locations,
            target_level=_target_levels(search.experience_levels),
            employment_types=search.employment_types,
            remote=search.remote,
        )

    def to_query(self) -> dict[str, typing.Any]:
        """Convert parameters to a dictionary for query string generation."""
        return {
            "location": self.location,
            "target_level": self.target_level,
            "employment_types": self.employment_types,
            "remote": self.remote,
        }

    def to_batchexecute_inner_params(
        self,
        query: str,
        page_index: int = 1,
        language: str = DEFAULT_LANGUAGE,
    ) -> list[typing.Any]:
        """Build the inner batchexecute params array for Google Careers.

        Args:
            query: The search query string.
            page_index: Pagination index.
            language: Language locale string.

        Returns:
            list[typing.Any]: Inner params array used by batchexecute.
        """
        location_entries = [[loc] for loc in self.location]
        exp_flags = _experience_flags(self.target_level)
        emp_flags = _employment_flags(self.employment_types)
        remote_flag = 1 if self.remote else None

        # Structure based on browser payload analysis:
        # Index 0: Query
        # Index 3: Employment Types [1=FT, 3=PT, ...]
        # Index 6: Locations [[loc1], [loc2]]
        # Index 7: Page Index (1-based)
        # Index 9: Remote (1 if true)
        # Index 16: Experience Levels [1=Early, 2=Mid, ...]

        return [
            f'"{query}"',  # 0
            None,  # 1
            None,  # 2
            emp_flags,  # 3
            language,  # 4
            None,  # 5
            location_entries,  # 6
            page_index,  # 7
            None,  # 8
            remote_flag,  # 9
            None,  # 10
            None,  # 11
            None,  # 12
            None,  # 13
            None,  # 14
            None,  # 15
            exp_flags,  # 16
        ]
