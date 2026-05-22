from arachne.sources import get_source_class
from arachne.sources.http_json import HTTPSource
from arachne.sources.microsoft.source import MicrosoftSource


def test_registry_loads_source_package() -> None:
    assert get_source_class("microsoft") is MicrosoftSource


def test_registry_falls_back_to_http_source() -> None:
    assert get_source_class("unknown_provider") is HTTPSource
