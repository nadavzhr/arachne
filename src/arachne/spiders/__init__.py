"""Spider registry that maps configured spider names to spider adapter classes."""

from __future__ import annotations

import importlib
import logging
from types import ModuleType
from typing import cast

from arachne.spiders.base import Spider

logger = logging.getLogger(__name__)


def _import_module(name: str) -> ModuleType | None:
    """Attempt to dynamically import a spider module by name.

    Args:
        name: The name of the spider (e.g., 'amazon').

    Returns:
        ModuleType | None: The imported module, or None if not found.

    Raises:
        ModuleNotFoundError: If the module is not found and the error name
            doesn't match the expected module path.
    """
    module_name = f"arachne.spiders.{name}"
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:  # pragma: no cover - dynamic import
        if exc.name != module_name:
            raise
        logger.debug("Could not import spider module %s: %s", module_name, exc)
        return None


def get_spider_class(name: str) -> type[Spider]:
    """Return the `Spider` class implementation for the given spider name.

    This function searches the `arachne.spiders.<name>` package for a class
    named `Spider` or any class ending with `Spider`.

    Args:
        name: The name of the spider to retrieve.

    Returns:
        type[Spider]: The spider class implementation.

    Raises:
        ValueError: If no specific implementation package or 'Spider' class is found.
    """
    module = _import_module(name)
    if module is None:
        raise ValueError(
            f"No spider adapter found for '{name}'. Please create one in arachne.spiders.{name}"
        )

    cls = getattr(module, "Spider", None)
    if cls is None:
        # Try to find a class that ends with Spider
        for attr_name in dir(module):
            if attr_name.endswith("Spider") and attr_name != "Spider":
                cls = getattr(module, attr_name)
                break

    if cls is None:
        raise ValueError(f"Spider module arachne.spiders.{name} has no 'Spider' class.")

    return cast(type[Spider], cls)
