# Arachne Core Implementation

This directory contains the core logic for the Arachne job aggregation engine. It is organized into several sub-packages, each handling a specific responsibility of the scraping pipeline.

## Directory Structure

-   **`cli.py`**: The Typer-powered CLI entrypoint. It bootstraps the application, configures logging, and maps CLI commands to service methods.
-   **`logging.py`**: A specialized logging system that supports central logging and per-spider log isolation.
-   **`clients/`**: HTTP client abstractions.
-   **`config/`**: Configuration loading and Pydantic validation for global and spider-specific settings.
-   **`models/`**: Central data models (JobPosting, SearchCriteria, etc.) that define the project's "language".
-   **`services/`**: High-level orchestrators (`ScraperService`, `JobService`, `ProfileService`) designed to be clean, stateless dependencies.
-   **`spiders/`**: The extensibility point. Contains adapters for various company job portals. The `BaseSpider` orchestrates the core fetching and normalization pipeline.
-   **`storage/`**: The core `Database` implementation (SQLite) for persisting normalized job data.
-   **`utils/`**: Shared helper functions for date parsing, URL normalization, and type casting.

## Execution Flow

When a scrape is triggered:
1.  **Bootstrap**: `cli.py` loads the global configuration and selected search profile.
2.  **Initialization**: `ScraperService` is instantiated with an HTTP client and the SQLite `Database`.
3.  **Dispatch**: For each enabled spider, a task is spawned in the `asyncio` event loop calling `spider.run()`.
4.  **Pipeline (`BaseSpider.run()`)**: 
    - **Fetch**: Retrieves raw data via the adapter's `fetch()` method.
    - **Debug**: If enabled, dumps the raw JSON payload to `data/debug/`.
    - **Normalize**: Converts raw data into `JobPosting` objects via the adapter's `normalize()` method.
    - **Dedupe & Filter**: Cleans the data using profile-specific rules.
5.  **Persist**: The `ScraperService` saves the filtered results using the injected `Database`.
