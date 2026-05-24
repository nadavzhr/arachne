# Arachne Models

This directory defines the core data structures used throughout the Arachne project. By centralizing these models, we ensure type safety and a consistent interface between spider adapters, services, and the storage layer.

## Core Models

### `JobPosting` (`job.py`)
The primary model representing a single job listing. All spider adapters must normalize their raw data into this format.
- **Fields**: `spider`, `title`, `company`, `url`, `location`, `posted_at`, `remote`, etc.
- **Validation**: Uses Pydantic for strict type checking and string trimming.

### `JobSearchCriteria` (`schema.py`)
Defines the parameters for a job search.
- **Fields**: `keywords`, `locations`, `remote_only`, etc.
- **Usage**: Passed to spider adapters to build provider-specific API queries.

### `Filters` (`schema.py`)
Post-normalization filtering rules.
- **Fields**: `include_keywords`, `exclude_keywords`, `min_date`.
- **Usage**: Applied by the `FilterService` to the results returned by adapters.

## Why Pydantic?
We use Pydantic (v2) for several reasons:
1. **Runtime Validation**: Ensures that data entering the system from flaky external APIs matches our expectations.
2. **Serialization**: Seamless conversion to/from JSON for storage and API responses.
3. **IDEs & Static Analysis**: Provides excellent autocompletion and allows `mypy` to catch bugs early.
