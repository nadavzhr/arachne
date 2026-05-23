import pytest

from arachne.sources import get_source_class
from arachne.sources.microsoft.source import MicrosoftSource


def test_registry_loads_source_package() -> None:
    assert get_source_class("microsoft") is MicrosoftSource


def test_registry_raises_on_unknown_provider() -> None:
    with pytest.raises(ValueError, match="No source adapter found for 'unknown_provider'"):
        get_source_class("unknown_provider")
