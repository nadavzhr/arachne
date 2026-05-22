"""Type casting helpers for JSON-like payloads."""

from __future__ import annotations

from typing import cast


def as_dict(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def as_list(value: object) -> list[object] | None:
    if not isinstance(value, list):
        return None
    return cast(list[object], value)
