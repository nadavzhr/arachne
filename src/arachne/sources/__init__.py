"""Source loader that maps source names to fetcher callables.

The runner should call `get_fetcher(name)` to obtain an async `fetch(cfg, client)` callable.
If a specific source module doesn't exist or doesn't expose `fetch`,
a plain HTTP+JSON fetcher is returned.
"""

from __future__ import annotations

import importlib
import logging
from types import ModuleType
from typing import cast

from arachne.sources.base import Source
from arachne.sources.http_json import HTTPSource as _GenericSource

logger = logging.getLogger(__name__)


def _import_module(name: str) -> ModuleType | None:
    module_name = f"arachne.sources.{name}"
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - dynamic import
        logger.debug("Could not import source module %s: %s", module_name, exc)
        return None


def get_source_class(name: str) -> type[Source]:
    """Return a `Source` class for the given source name.

    The returned value is a class that can be instantiated with a `SourceConfig`.
    Falls back to `GenericSource` when a specific implementation is missing.
    """
    module = _import_module(name)
    if module is None:
        return _GenericSource
    cls = getattr(module, "Source", None)
    if cls is None:
        logger.debug("Source module %s has no Source class, using GenericSource", module.__name__)
        return _GenericSource
    return cast(type[Source], cls)
