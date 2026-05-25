# 🕷️ Arachne

> *"A weaver so skilled, she challenged the gods themselves. Now, she weaves the scattered threads of the tech job market into a single, unbreakable web."*

**Arachne** is a high-performance, asynchronous job scraping aggregator designed for tracking listings across major tech companies. It fetches, normalizes, and filters job postings from multiple provider APIs concurrently, providing a unified view of the tech job market.

---

## 🏛️ The Legend

In Greek mythology, [**Arachne**](https://en.wikipedia.org/wiki/Arachne) was a mortal weaver of such extraordinary skill that she dared to challenge Athena, the goddess of wisdom and crafts, to a weaving contest. 

Arachne's tapestry was a masterpiece of flawless technique, but it depicted the failings and indiscretions of the gods. Infuriated by the girl's hubris and the perfection of her work, Athena transformed her into a spider—condemning her to weave intricate webs for all eternity.

This project carries that spirit forward: transforming the complex, messy "threads" of corporate job boards into a single, perfectly woven web of data.

---

## 🚀 Features

- **Concurrent Execution:** Powered by `asyncio` and `httpx` for high-throughput scraping.
- **Unified Schema:** Normalizes heterogeneous API responses into a strict `JobPosting` Pydantic model.
- **Profile-Based Filtering:** Decouples search criteria (keywords, location, remote) from provider-specific implementation details.
- **Deep Observability:** Isolated per-spider logging to debug individual scrapers without noise.
- **Extensible Architecture:** Simple adapter pattern for adding new job spiders in minutes.

---

## 🛠️ Installation

### 1. Install `uv` (Recommended)
Arachne uses `uv` for lightning-fast dependency management and project isolation.

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "ir https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Project
Clone the repository and sync dependencies:

```bash
git clone https://github.com/your-repo/arachne.git
cd arachne
uv sync
```

---

## 📖 Quick Start

### Run a Scrape
Execute the default search profile across all enabled spiders:
```bash
uv run arachne run
```

### View Results
List a summary of the latest scraped jobs from the CLI:
```bash
uv run arachne jobs
```

### List Profiles
See all available search configurations:
```bash
uv run arachne profiles
```

---

## 🏗️ Architecture

Arachne is built on a modular "Service-Adapter" architecture:

1.  **CLI/Entrypoint (`cli.py`):** Bootstraps the environment and orchestrates the services.
2.  **Scraper Service:** Coordinates the `asyncio` event loop and manages the lifecycle of shared clients (HTTP and Browser).
3.  **Spider Adapters:** Provider-specific modules that receive a `FetchContext` to handle the "Fetch" phase and subsequently "Normalize" data.
4.  **Filter Service:** Applies search profiles (keywords, remote status, etc.) to the normalized data.
5.  **Storage Layer:** Pluggable interface for persisting data (defaults to **SQLite** for deduplication and history).

```mermaid
graph TD
    CLI[CLI / API] --> Scraper[Scraper Service]
    Scraper --> ClientMgr[Client/Browser Manager]
    ClientMgr --> FetchCtx[FetchContext]
    FetchCtx --> Spider[Spider Adapters]
    Spider --> Normalize[Normalize: Pydantic]
    Normalize --> Filter[Filter Service]
    Filter --> Storage[Storage Layer: SQLite]
```

---

## ⚙️ Configuration

-   **`config/global.yaml`**: System-wide settings (concurrency, storage type, logging).
-   **`config/spiders.yaml`**: Registry of supported companies and their base API endpoints.
-   **`profiles/*.yaml`**: Definitions of *what* to search for (e.g., "Software Engineer", "Remote", "London").

---

## 🔌 Extending: Adding a New Spider

To add a new company:
1.  Create a directory in `src/arachne/spiders/<company_name>/`.
2.  Implement a `Spider` class inheriting from `arachne.spiders.base.Spider`.
3.  Define the `fetch` (API call) and `normalize` (mapping to `JobPosting`) methods.
4.  Register the spider in `config/spiders.yaml`.

*See [src/arachne/spiders/README.md](src/arachne/spiders/README.md) for a detailed guide.*

---

## 🗺️ Roadmap

- [ ] **API Layer:** FastAPI-based backend to expose scraping triggers and data.
- [ ] **Web UI:** Interactive dashboard for viewing jobs and managing profiles.
- [x] **Persistent Database:** Transition from JSON snapshots to a relational database (SQLite).

---

## 📜 License
This project is licensed under the MIT License.
