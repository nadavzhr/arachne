import json
from pathlib import Path
from typing import Any

import pytest

from arachne.config.profile import SearchProfile
from arachne.runner import run_from_config


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    global_yaml = """
data_dir: data
timeout_seconds: 5.0
concurrency: 1
user_agent: "arachne-test"
logging:
  enabled: false
"""
    (config_dir / "global.yaml").write_text(global_yaml)

    sources_yaml = """
mock_source:
  enabled: true
  url: "http://example.com/api"
"""
    (config_dir / "sources.yaml").write_text(sources_yaml)

    return config_dir


@pytest.mark.anyio
async def test_pipeline_runs_without_crashing(
    temp_config_dir: Path, mocker: Any, tmp_path: Path
) -> None:
    # Use tmp_path for data so it doesn't pollute real project
    global_yaml_path = temp_config_dir / "global.yaml"
    content = global_yaml_path.read_text()
    global_yaml_path.write_text(content.replace("data_dir: data", f"data_dir: {tmp_path}/data"))

    # We mock out HTTPClient or the generic HTTP fetch so it doesn't do real requests
    async def _mock_fetch(*args: Any, **kwargs: Any) -> list[Any]:
        return [{"id": "1", "title": "Test Job", "url": "http://example.com/job/1"}]

    mocker.patch("arachne.sources.http_json.fetch", side_effect=_mock_fetch)
    mocker.patch("arachne.sources.http_json.fetch_paginated", side_effect=_mock_fetch)

    # Note: Because the dynamic loader falls back to HTTPSource, our mock_source
    # will be an instance of HTTPSource, which calls `arachne.sources.http_json.fetch`.

    await run_from_config(temp_config_dir, SearchProfile())

    data_dir = tmp_path / "data"
    assert data_dir.exists()

    # It should have written the mock jobs to data/mock_source/jobs.json
    snapshot_path = data_dir / "mock_source" / "jobs.json"
    assert snapshot_path.exists()

    saved_jobs = json.loads(snapshot_path.read_text())
    assert len(saved_jobs) == 1
    assert saved_jobs[0]["title"] == "Test Job"
