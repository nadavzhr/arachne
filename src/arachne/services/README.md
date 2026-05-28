# Arachne Services

Services are the "orchestrators" of the application. They contain the business logic that coordinates between models, spider adapters, and infrastructure (clients/storage). 

These services are designed to be clean, stateless dependencies that can be easily injected into CLI commands and future FastAPI route handlers.

## Key Services

### `ScraperService` (`scraper.py`)
The main entry point for running a scrape.
- **Concurrency**: Uses `asyncio.Semaphore` to limit the number of simultaneous network requests.
- **Workflow**: For each spider, it triggers the unified `spider.run()` pipeline (fetch, normalize, dedupe, filter) and persists the resulting data using the injected `Database` dependency.

### `ProfileService` (`profiles.py`)
Manages the lifecycle of search profiles.
- Handles loading `.yaml` profiles from the `profiles/` directory and validating them into `SearchProfile` Pydantic models.

### `JobService` (`jobs.py`)
A high-level service for querying stored job data.
- Provides a clean interface for the CLI and API to retrieve the "latest" jobs across one or more spiders without needing to write raw SQL queries against the Database.

## Design Principles
- **Statelessness**: Services do not hold state; they operate on data passed to them.
- **Dependency Injection**: Services receive their dependencies (like `db` or `client`) during initialization, making them easy to test and decouple.