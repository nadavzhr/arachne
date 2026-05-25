"""Load and validate search profile configurations."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from arachne.models.schema import Filters, JobSearchCriteria


class SpiderOverrides(BaseModel):
    """Spider-specific configuration overrides defined within a profile."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    search: JobSearchCriteria | None = Field(
        default=None, description="Criteria that override the profile-wide search settings"
    )
    filters: Filters | None = Field(
        default=None, description="Filters that override the profile-wide filter settings"
    )


class SearchProfile(BaseModel):
    """A collection of search criteria and filters for a scrape run."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(default="default", description="The display name of the profile")
    search: JobSearchCriteria = Field(
        default_factory=lambda: JobSearchCriteria(),
        description="Global search criteria for this profile",
    )
    filters: Filters = Field(
        default_factory=lambda: Filters(), description="Global post-normalization filters"
    )
    spiders: dict[str, SpiderOverrides] = Field(
        default_factory=dict, description="Per-spider configuration overrides"
    )

    def get_search_for(self, spider_name: str) -> JobSearchCriteria:
        """Get the merged search criteria for a specific spider.

        Args:
            spider_name: The name of the spider to retrieve criteria for.

        Returns:
            JobSearchCriteria: Merged criteria (spider-specific overrides + profile globals).
        """
        override = self.spiders.get(spider_name)
        if not override or not override.search:
            return self.search

        global_dump = self.search.model_dump(mode="json")
        override_dump = override.search.model_dump(mode="json", exclude_unset=True)
        merged = {**global_dump, **override_dump}
        return JobSearchCriteria(**merged)

    def get_filters_for(self, spider_name: str) -> Filters:
        """Get the merged filters for a specific spider.

        Args:
            spider_name: The name of the spider to retrieve filters for.

        Returns:
            Filters: Merged filters (spider-specific overrides + profile globals).
        """
        override = self.spiders.get(spider_name)
        if not override or not override.filters:
            return self.filters

        global_dump = self.filters.model_dump(mode="json")
        override_dump = override.filters.model_dump(mode="json", exclude_unset=True)
        merged = {**global_dump, **override_dump}
        return Filters(**merged)


def load_profile(path: Path) -> SearchProfile:
    """Load and validate a search profile from a YAML file.

    Args:
        path: Path to the .yaml profile file.

    Returns:
        SearchProfile: Validated search profile model.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "name" not in data:
        data["name"] = path.stem
    return SearchProfile(**data)
