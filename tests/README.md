# Arachne Testing Suite

Arachne is tested using `pytest` and `hypothesis`. We aim for high coverage (80%+) of the core services and normalization logic.

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage report
```bash
uv run pytest --cov=src/arachne
```

## Test Structure

-   **`config/`**: Tests for configuration loading and validation.
-   **`models/`**: Tests for Pydantic models and custom validators.
-   **`services/`**: Integration tests for orchestrators (`ScraperService`, `FilterService`).
-   **`sources/`**: Tests for source-specific normalization logic.
-   **`utils/`**: Unit tests for shared helper functions.

## Strategy

### 1. Mocking External APIs
We do not make real network calls during testing. We use `pytest-mock` to stub the `fetch` methods of source adapters, returning pre-defined "raw" payloads to test the `normalize` logic.

### 2. Property-Based Testing
For critical utilities (like date parsing or URL building), we use `hypothesis` to generate edge-case inputs and ensure the code doesn't crash on unexpected formats.

### 3. Snapshot Testing
For source adapters, we store sample JSON responses from the real APIs and verify that our normalization logic produces the expected `JobPosting` objects.
