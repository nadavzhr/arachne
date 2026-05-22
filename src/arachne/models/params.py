"""Base interface for source-specific search parameter models."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict

from arachne.models.schema import JobSearchCriteria


class BaseParams(BaseModel):
    """Provider adapters translate shared search criteria into provider params."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> Self:
        raise NotImplementedError
