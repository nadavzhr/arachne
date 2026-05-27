# Arachne Core Implementation

This directory contains the core logic for the Arachne job aggregation engine. It is organized into several sub-packages, each handling a specific responsibility of the scraping pipeline.

## Directory Structure

-   **`cli.py`**: The Typer-powered CLI entrypoint. It bootstraps the application, configures logging, and maps CLI commands to service methods.
-   **`logging.py`**: A specialized logging system that supports central logging and per-spider log isolation.
-   **`clients/`**: HTTP client abstractions.
-   **`config/`**: Configuration loading and Pydantic validation for global and spider-specific settings.
-   **`models/`**: Central data models (JobPosting, SearchCriteria, etc.) that define the project's "language".
-   **`services/`**: The "brain" of the application. High-level orchestrators that coordinate fetching, filtering, and storage.
-   **`spiders/`**: The extensibility point. Contains adapters for various company job portals.
-   **`storage/`**: Interfaces and implementations for data persistence.
-   **`utils/`**: Shared helper functions for date parsing, URL normalization, and type casting.

## Execution Flow

When a scrape is triggered:
1.  **Bootstrap**: `cli.py` loads the global configuration and selected search profile.
2.  **Initialization**: `ScraperService` is instantiated with an HTTP client and a storage backend.
3.  **Dispatch**: For each enabled spider, a task is spawned in the `asyncio` event loop.
4.  **Fetch & Normalize**: The spider adapter's `fetch()` method retrieves raw data, and its `normalize()` method converts it into `JobPosting` objects.
5.  **Filter**: The `FilterService` applies profile-specific rules (keywords, remote filters) to the normalized list.
6.  **Persist**: The results (raw, unfiltered, and filtered) are saved via the `storage` implementation.
