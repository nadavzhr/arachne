import json
import pathlib
from typing import Any

import pytest

import arachne.config.loader
import arachne.config.profile
import arachne.models.job
import arachne.models.schema
import arachne.services.scraper
import arachne.spiders.base
import arachne.storage.json
from arachne.clients.http import create_client


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

    spiders_yaml = """
mock_spider:
  enabled: true
  url: "http://example.com/api"
"""
    (config_dir / "spiders.yaml").write_text(spiders_yaml)

    return config_dir


class DummySpider(arachne.spiders.base.Spider):
    async def fetch(
        self,
        ctx: Any,
        search: arachne.models.schema.JobSearchCriteria,
    ) -> list[dict[str, str]]:
        del ctx, search  # Unused.
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
                        spider=self.name,
                        company="Test",
                        title=str(title),
                        url=str(url),  # type: ignore
                    )
                )
            except Exception:
                continue

        return jobs


@pytest.mark.anyio
async def test_scraper_service_runs_without_crashing(
    temp_config_dir: pathlib.Path, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Use tmp_path for data so it doesn't pollute real project
    data_dir = tmp_path / "data"

    global_cfg, spiders = arachne.config.loader.load_all(temp_config_dir)

    monkeypatch.setattr("arachne.services.scraper.get_spider_class", lambda name: DummySpider)

    storage = arachne.storage.json.JsonFileJobStorage(data_dir)
    profile = arachne.config.profile.SearchProfile()

    async with create_client(global_cfg.timeout_seconds, global_cfg.user_agent) as client:
        scraper = arachne.services.scraper.ScraperService(
            storage=storage,
            client=client,
            concurrency=global_cfg.concurrency,
        )

        results = await scraper.run_profile(spiders, profile)
        assert "mock_spider" in results
        assert not isinstance(results["mock_spider"], BaseException)

    assert data_dir.exists()

    # It should have written the mock jobs to data/mock_spider/jobs.json
    snapshot_path = data_dir / "mock_spider" / "jobs.json"
    assert snapshot_path.exists()

    saved_jobs = json.loads(snapshot_path.read_text())
    assert len(saved_jobs) == 1
    assert saved_jobs[0]["title"] == "Test Job"
