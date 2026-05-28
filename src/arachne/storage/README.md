# Arachne Storage Layer

The storage layer is responsible for persisting job data. 

## `Database` (`db.py`)
The primary storage backend for Arachne. It uses a local SQLite database file (`arachne.db`) located in the `data/` directory. This serves as the single source of truth for the upcoming FastAPI layer and the CLI.

- **Deduplication**: Automatically handles job deduplication using a unique constraint on `(spider, external_id)`.
- **History**: Tracks when a job was first discovered and when it was last seen active using `discovered_at` and `last_seen_at` timestamps.
- **Performance**: Significantly faster for large datasets and provides a structured way to query data.

## Raw Data Debugging
Raw un-normalized API responses are no longer stored in the main database. Instead, when the application is run in `--debug` mode, the `Spider` pipeline intercepts the raw payload during the fetch phase and writes it directly to timestamped JSON files in the `data/debug/` directory. This provides an easy way to inspect provider API changes without bloating the relational database.

## Database Schema (SQLite)
The SQLite implementation uses a single main table:
1.  **`jobs`**: Stores normalized job postings with timestamps for discovery, last confirmation, and associated metadata (e.g. `remote`, `employment_type`).