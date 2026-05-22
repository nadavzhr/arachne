# 🕷️ Arachne — Job Aggregation and Normalization

[![Python](https://img.shields.io/badge/python-3.14-blue?logo=python\&style=flat-square)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-prototype-yellow?style=flat-square)]()
[![httpx](https://img.shields.io/badge/httpx-async%20client-green?style=flat-square)](https://www.python-httpx.org/)

Arachne (uh-RACK-nee) is a small asynchronous job listing aggregator that fetches job postings from multiple
provider APIs, normalizes them into a common schema, and persists snapshots locally for later analysis.

The project is currently in an early prototype stage. Right now, normalized snapshots are written
to JSON files on disk to keep iteration simple and transparent during development. The longer-term
goal is to move local storage to SQLite and eventually expose the aggregated data to a frontend
application.

## Key ideas:

* Fetch provider payloads concurrently using an async HTTP client.
* Normalize heterogeneous provider responses into a single `JobPosting` model.
* Keep user-facing search configuration provider-neutral.
* Persist raw provider payloads and normalized snapshots locally.
* Keep the architecture simple and easy to extend with additional providers.

## Features

* Asynchronous HTTP fetching with `httpx`.
* Per-source fetchers and normalizers with a consistent `fetch` / `normalize` interface.
* Validation and normalization via Pydantic models (`JobPosting`).
* Local JSON persistence of raw payloads and normalized snapshots.

## Quick start

* Ensure a Python 3.14+ virtual environment is activated.
* Install dependencies using [`uv`](https://github.com/astral-sh/uv) (recommended):

```bash
uv sync
```

* Run the runner to fetch and snapshot all configured sources:

```bash
uv run arachne
```

* Alternatively, you can install dependencies with pip:
```bash
pip install -r requirements.txt
```

* Run using python directly:

```bash
python3 src/arachne/runner.py
```

## Configuration

* `config/global.yaml` — runtime defaults plus shared search, filter, and logging criteria.
* `config/sources.yaml` — per-source configuration (URL, headers, enabled flag, optional
  shared-schema search overrides).

Provider-specific request parameters are translated inside the Python source adapters. YAML should
describe the job search in terms of the shared schema (`title`, `locations`, `remote`,
`employment_types`, `experience_levels`) rather than raw provider query keys.

## Output

* Data is written under the configured data directory (default `data/`). For each source the
  runner writes:

  * `{data_dir}/{source}/raw.json` — raw fetched payloads
  * `{data_dir}/{source}/jobs.unfiltered.json` — normalized job snapshots (unfiltered)
  * `{data_dir}/{source}/jobs.json` — normalized job snapshots after filters

## Logging

* Logging is configured centrally from `config/global.yaml`.
* The runner writes file logs only by default:
  * `logs/arachne.log` — full application log
  * `logs/sources/{source}.log` — per-source log slices for parallel debugging
* Source adapters should use `self.log` for fetch, pagination, scraping, and parsing messages.

## Supported providers

* Microsoft Careers
* NVIDIA Careers
* Amazon Jobs
* Google Careers
* Apple Careers
* Meta Careers (adapter present, disabled in the default config)

## Roadmap

* Replace JSON snapshot persistence with SQLite storage for local runs.
* Add historical tracking and deduplication.
* Expose aggregated data through a lightweight backend/API for a frontend client.

## Extending

* Add a package under `src/arachne/sources/<name>/` exposing `Source` from `__init__.py`.
* Keep provider-specific request mapping in `src/arachne/sources/<name>/params.py` and adapter
  behavior in `src/arachne/sources/<name>/source.py`.
* Map `SourceConfig.search` into provider-specific request parameters inside the source package
  rather than adding raw provider keys to `config/sources.yaml`.
