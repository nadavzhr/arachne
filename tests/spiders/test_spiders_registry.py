import pytest

from arachne.spiders import get_spider_class
from arachne.spiders.microsoft.spider import MicrosoftSpider


def test_registry_loads_spider_package() -> None:
    assert get_spider_class("microsoft") is MicrosoftSpider


def test_registry_raises_on_unknown_provider() -> None:
    with pytest.raises(ValueError, match="No spider adapter found for 'unknown_provider'"):
        get_spider_class("unknown_provider")
