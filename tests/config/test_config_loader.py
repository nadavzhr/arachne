from pathlib import Path

import pytest
from pydantic import ValidationError

from arachne.config.loader import load_all, load_global, load_sources


def _write_config(root: Path, global_yaml: str, sources_yaml: str) -> None:
    root.joinpath("global.yaml").write_text(global_yaml, encoding="utf-8")
    root.joinpath("sources.yaml").write_text(sources_yaml, encoding="utf-8")


def test_load_sources_ignores_legacy_search_and_filters(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
data_dir: data
""",
        """
microsoft:
  url: https://example.com/microsoft
  search:
    locations: ["Haifa, Israel"]
  filters:
    include_keywords: [backend]
nvidia:
  url: https://example.com/nvidia
""",
    )

    _global_cfg, sources = load_all(tmp_path)

    microsoft = sources["microsoft"]
    assert microsoft.url == "https://example.com/microsoft"
    # Ensure no AttributeError on search or filters, but they are not present
    assert not hasattr(microsoft, "search")
    assert not hasattr(microsoft, "filters")

    nvidia = sources["nvidia"]
    assert nvidia.url == "https://example.com/nvidia"


def test_source_config_rejects_raw_provider_params(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
data_dir: data
""",
        """
microsoft:
  url: https://example.com/microsoft
  params:
    query: software engineer
""",
    )

    global_cfg = load_global(tmp_path / "global.yaml")

    with pytest.raises(ValidationError):
        load_sources(tmp_path / "sources.yaml", global_cfg=global_cfg)
