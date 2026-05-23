"""Load and validate search profile configurations."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from arachne.models.schema import Filters, JobSearchCriteria


class SourceOverrides(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    search: JobSearchCriteria | None = None
    filters: Filters | None = None


class SearchProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = "default"
    search: JobSearchCriteria = Field(default_factory=JobSearchCriteria)
    filters: Filters = Field(default_factory=Filters)
    sources: dict[str, SourceOverrides] = Field(default_factory=dict)

    def get_search_for(self, source_name: str) -> JobSearchCriteria:
        """Get the merged search criteria for a specific source."""
        override = self.sources.get(source_name)
        if not override or not override.search:
            return self.search

        global_dump = self.search.model_dump(mode="json")
        override_dump = override.search.model_dump(mode="json", exclude_unset=True)
        merged = {**global_dump, **override_dump}
        return JobSearchCriteria(**merged)

    def get_filters_for(self, source_name: str) -> Filters:
        """Get the merged filters for a specific source."""
        override = self.sources.get(source_name)
        if not override or not override.filters:
            return self.filters

        global_dump = self.filters.model_dump(mode="json")
        override_dump = override.filters.model_dump(mode="json", exclude_unset=True)
        merged = {**global_dump, **override_dump}
        return Filters(**merged)


def load_profile(path: Path) -> SearchProfile:
    """Load a YAML profile from the given path."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "name" not in data:
        data["name"] = path.stem
    return SearchProfile(**data)
