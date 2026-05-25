"""Apple Careers request parameter mapping."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from arachne.models.params import BaseParams
from arachne.models.schema import JobSearchCriteria


def _location_slug(location: str) -> str:
    """Convert a location string into an Apple-specific location slug.

    Args:
        location: Raw location string.

    Returns:
        str: Apple-formatted location slug (e.g., 'israel-ISR').
    """
    normalized = location.strip().lower()
    if normalized in {"israel", "tel aviv, israel", "haifa, israel"}:
        return "israel-ISR"
    if normalized.startswith("postlocation-"):
        return location.strip()
    return normalized.replace(", ", "-").replace(" ", "-")


class AppleParams(BaseParams):
    """Parameter model for Apple Careers search requests."""

    location: list[str] = Field(default_factory=list, description="List of location slugs")
    key: str = Field(default="software engineer", description="Search keywords")
    language: str = Field(default="en-us", description="Target language/locale code")

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> AppleParams:
        """Create AppleParams from generic JobSearchCriteria.

        Args:
            search: The generic search criteria.

        Returns:
            AppleParams: Populated Apple parameters.
        """
        locations = [_location_slug(location) for location in search.locations]
        if not locations and search.remote:
            locations = ["remote"]
        return cls(location=locations, key=search.title)

    def to_query(self) -> dict[str, Any]:
        """Convert parameters to a dictionary for search URL construction.

        Returns:
            dict[str, Any]: Dictionary of search parameters.
        """
        return {
            "location": self.location,
            "key": self.key,
            "language": self.language,
        }
