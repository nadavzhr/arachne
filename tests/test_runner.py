import json
import pathlib
from typing import Any

import pytest

import arachne.config.profile
import arachne.models.job
import arachne.models.schema
import arachne.runner
import arachne.sources.base


@pytest.fixture
def temp_config_dir(tmp_path: pathlib.Path) -> pathlib.Path:
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


class DummySource(arachne.sources.base.Source):
    async def fetch(
        self,
        client: Any,
        search: arachne.models.schema.JobSearchCriteria,
    ) -> list[dict[str, str]]:
        del client, search  # Unused.
        return [{"id": "1", "title": "Test Job", "url": "http://example.com/job/1"}]

    def normalize(self, raw: Any) -> list[arachne.models.job.JobPosting]:
        if not isinstance(raw, list):
            return []

        jobs: list[arachne.models.job.JobPosting] = []
        for rec in raw:
            if not isinstance(rec, dict):
                continue
            title = rec.get("title")
            url = rec.get("url")
            if not title or not url:
                continue
            try:
                jobs.append(
                    arachne.models.job.JobPosting(
                        source=self.name,
                        company="Test",
                        title=str(title),
                        url=str(url),  # type: ignore
                    )
                )
            except Exception:
                continue

        return jobs


@pytest.mark.anyio
async def test_pipeline_runs_without_crashing(
    temp_config_dir: pathlib.Path, mocker: Any, tmp_path: pathlib.Path
) -> None:
    # Use tmp_path for data so it doesn't pollute real project
    global_yaml_path = temp_config_dir / "global.yaml"
    content = global_yaml_path.read_text()
    global_yaml_path.write_text(content.replace("data_dir: data", f"data_dir: {tmp_path}/data"))

    mocker.patch("arachne.services.scraper.get_source_class", return_value=DummySource)

    await arachne.runner.run_from_config(
        temp_config_dir,
        arachne.config.profile.SearchProfile(),
    )

    data_dir = tmp_path / "data"
    assert data_dir.exists()

    # It should have written the mock jobs to data/mock_source/jobs.json
    snapshot_path = data_dir / "mock_source" / "jobs.json"
    assert snapshot_path.exists()

    saved_jobs = json.loads(snapshot_path.read_text())
    assert len(saved_jobs) == 1
    assert saved_jobs[0]["title"] == "Test Job"
