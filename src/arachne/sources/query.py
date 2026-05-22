"""Shared query-string helpers for source adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote, urlencode


def build_query_string(params: Mapping[str, Any]) -> str:
    return urlencode(params, doseq=True, quote_via=quote)
