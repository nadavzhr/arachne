"""Base interface for spider-specific search parameter models."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict

from arachne.models.schema import JobSearchCriteria


class BaseParams(BaseModel):
    """Provider adapters translate shared search criteria into provider params.

    Each spider should implement its own Params model inheriting from this class
    to handle provider-specific query parameter mapping.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @classmethod
    def from_search(cls, search: JobSearchCriteria) -> Self:
        """Create provider-specific parameters from generic search criteria.

        Args:
            search: The generic JobSearchCriteria to translate.

        Returns:
            Self: An instance of the provider-specific Params model.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
