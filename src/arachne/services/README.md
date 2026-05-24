# Arachne Services

Services are the "orchestrators" of the application. They contain the business logic that coordinates between models, spider adapters, and infrastructure (clients/storage).

## Key Services

### `ScraperService` (`scraper.py`)
The main entry point for running a scrape.
- **Concurrency**: Uses `asyncio.Semaphore` to limit the number of simultaneous network requests.
- **Workflow**: For each spider, it triggers a fetch, normalization, filtering, and persistence sequence.

### `SearchService` (`search.py`)
A lower-level service that handles the execution of a single spider's search pipeline.
- Bridges the gap between a `Spider` adapter and the `FilterService`.
- Captures normalization errors without crashing the entire run.

### `FilterService` (`filters.py`)
Contains logic to prune the normalized list of jobs based on the user's `Filters` configuration.
- Supports keyword inclusion/exclusion and remote-status checks.

### `ProfileService` (`profiles.py`)
Manages the lifecycle of search profiles.
- Handles loading `.yaml` profiles from the `profiles/` directory and validating them into `SearchProfile` models.

### `JobService` (`jobs.py`)
A high-level service for querying stored job data.
- Used by the CLI and eventually the API to retrieve the "latest" jobs across one or more spiders.

## Design Principles
- **Statelessness**: Services do not hold state; they operate on data passed to them.
- **Dependency Injection**: Services receive their dependencies (like `storage` or `client`) during initialization, making them easy to test.
