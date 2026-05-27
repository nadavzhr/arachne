"""Utility functions for the Meta Careers spider."""

from __future__ import annotations

import json
from typing import Any

FOR_LOOP_PREFIX = "for (;;);"


def strip_js_prefix(text: str) -> str:
    """Remove common JS prefixes from GraphQL responses."""
    if text.startswith(FOR_LOOP_PREFIX):
        return text[len(FOR_LOOP_PREFIX) :].lstrip()
    return text


def parse_graphql_text(text: str) -> list[dict[str, Any]]:
    """Parse Meta's multi-part GraphQL response text."""
    items: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = strip_js_prefix(line)
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                items.append(obj)
        except json.JSONDecodeError:
            continue

    if items:
        return items

    raw = strip_js_prefix(text.strip())
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return [obj]
    except json.JSONDecodeError:
        pass
    return []
