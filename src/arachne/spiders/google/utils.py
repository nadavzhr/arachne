"""Utility functions for the Google Careers spider."""

from __future__ import annotations

import json
import re
import typing


def parse_batchexecute_text(text: str) -> tuple[list[typing.Any], list[typing.Any] | None]:
    """Parse Google's batchexecute response format.

    Args:
        text: Raw response text.

    Returns:
        tuple[list[typing.Any], list[typing.Any] | None]: Parsed batch data and inner payload.

    Raises:
        ValueError: If the response is not in the expected format.
    """
    json_start = text.find("[")
    if json_start == -1:
        raise ValueError("Unexpected response format: missing '['.")
    data = json.loads(text[json_start:])
    payload_json = None
    if data and data[0] and len(data[0]) > 2 and data[0][2]:
        payload_json = json.loads(data[0][2])
    return data, payload_json


def extract_payload(raw: typing.Any) -> list[typing.Any] | None:
    """Extract the payload list from raw dictionary or return as is if list.

    Args:
        raw: Raw data.

    Returns:
        list[typing.Any] | None: Extracted payload list.
    """
    if isinstance(raw, dict) and "payload" in raw:
        payload = raw.get("payload")
        return payload if isinstance(payload, list) else None
    return raw if isinstance(raw, list) else None


def extract_html_block(value: typing.Any) -> str | None:
    """Extract HTML content from a Google structured value block.

    Args:
        value: Structured value list.

    Returns:
        str | None: Extracted HTML string.
    """
    if not isinstance(value, list):
        return None
    if len(value) > 1 and isinstance(value[1], str):
        return value[1]
    return None


def extract_locations(value: typing.Any) -> str | None:
    """Extract and format locations from Google's location block.

    Args:
        value: Location block list.

    Returns:
        str | None: Formatted locations string (pipe separated).
    """
    if not isinstance(value, list):
        return None

    names: list[str] = []
    for entry in value:
        if not isinstance(entry, list) or not entry:
            continue
        name = entry[0]
        if isinstance(name, str) and name.strip():
            names.append(name.strip())

    if not names:
        return None
    return " | ".join(dict.fromkeys(names))


def strip_html(text: str | None) -> str | None:
    """Remove HTML tags from a string.

    Args:
        text: String containing HTML.

    Returns:
        str | None: Cleaned string.
    """
    if not text:
        return None
    stripped = re.sub("<.*?>", "", text)
    return stripped.strip() or None
