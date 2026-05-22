from pathlib import Path

import pytest
from pydantic import ValidationError

from arachne.config.loader import load_all, load_global, load_sources
from arachne.models.schema import EmploymentType, ExperienceLevel


def _write_config(root: Path, global_yaml: str, sources_yaml: str) -> None:
    root.joinpath("global.yaml").write_text(global_yaml, encoding="utf-8")
    root.joinpath("sources.yaml").write_text(sources_yaml, encoding="utf-8")


def test_load_sources_merges_shared_search_and_filters(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
data_dir: data
search:
  title: backend engineer
  locations: [Israel]
  remote: true
  employment_types: [full_time]
  experience_levels: [entry, mid]
filters:
  include_keywords: [backend]
  exclude_keywords: [senior]
  locations: [Israel]
""",
        """
microsoft:
  url: https://example.com/microsoft
  search:
    locations: ["Haifa, Israel"]
nvidia:
  url: https://example.com/nvidia
""",
    )

    _global_cfg, sources = load_all(tmp_path)

    microsoft = sources["microsoft"]
    assert microsoft.search.title == "backend engineer"
    assert microsoft.search.locations == ["Haifa, Israel"]
    assert microsoft.search.employment_types == [EmploymentType.FULL_TIME]
    assert microsoft.search.experience_levels == [ExperienceLevel.ENTRY, ExperienceLevel.MID]
    assert microsoft.filters.include_keywords == ["backend"]

    nvidia = sources["nvidia"]
    assert nvidia.search.locations == ["Israel"]
    assert nvidia.filters.exclude_keywords == ["senior"]


def test_source_config_rejects_raw_provider_params(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
search:
  title: software engineer
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
