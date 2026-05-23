"""Source registry that maps configured source names to source adapter classes."""

from __future__ import annotations

import importlib
import logging
from types import ModuleType
from typing import cast

from arachne.sources.base import Source

logger = logging.getLogger(__name__)


def _import_module(name: str) -> ModuleType | None:
    module_name = f"arachne.sources.{name}"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:  # pragma: no cover - dynamic import
        if exc.name != module_name:
            raise
        logger.debug("Could not import source module %s: %s", module_name, exc)
        return None


def get_source_class(name: str) -> type[Source]:
    """Return a `Source` class for the given source name.

    Raises:
        ValueError: If no specific implementation package is found for the given name.
    """
    module = _import_module(name)
    if module is None:
        raise ValueError(
            f"No source adapter found for '{name}'. Please create one in arachne.sources.{name}"
        )

    cls = getattr(module, "Source", None)
    if cls is None:
        raise ValueError(f"Source module arachne.sources.{name} has no 'Source' class.")

    return cast(type[Source], cls)
