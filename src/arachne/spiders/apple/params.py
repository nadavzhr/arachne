"""Apple Careers request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import JobSearchCriteria


def _location_slug(location: str) -> str:
    normalized = location.strip().lower()
    if normalized in {"israel", "tel aviv, israel", "haifa, israel"}:
        return "israel-ISR"
    if normalized.startswith("postlocation-"):
        return location.strip()
    return normalized.replace(", ", "-").replace(" ", "-")


class AppleParams(BaseParams):
    location: list[str] = Field(default_factory=list)
    key: str = Field(default="software engineer")
    language: str = Field(default="en-us")

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> AppleParams:
        locations = [_location_slug(location) for location in search.locations]
        if not locations and search.remote:
            locations = ["remote"]
        return cls(location=locations, key=search.title)

    def to_query(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "key": self.key,
            "language": self.language,
        }
