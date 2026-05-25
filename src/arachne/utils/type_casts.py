"""Type casting helpers for JSON-like payloads."""

from __future__ import annotations

from typing import cast


def as_dict(value: object) -> dict[str, object] | None:
    """Safely cast an object to a dictionary.

    Args:
        value: The object to cast.

    Returns:
        dict[str, object] | None: The dictionary if the cast was successful,
            otherwise None.
    """
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def as_list(value: object) -> list[object] | None:
    """Safely cast an object to a list.

    Args:
        value: The object to cast.

    Returns:
        list[object] | None: The list if the cast was successful,
            otherwise None.
    """
    if not isinstance(value, list):
        return None
    return cast(list[object], value)
