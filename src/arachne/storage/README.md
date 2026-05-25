# Arachne Storage Layer

The storage layer is responsible for persisting job data and raw API responses. It uses an interface-based design to allow for easy swapping of storage backends.

## The Interface: `JobStorage` (`base.py`)
Any storage implementation must satisfy the `JobStorage` abstract base class, which defines methods for:
- `save_jobs`: Persisting a list of `JobPosting` objects.
- `load_jobs`: Retrieving jobs for a specific spider.
- `save_raw`: Saving the raw, un-normalized API response for debugging.

## Implementations

### `SqliteJobStorage` (`sqlite.py`) - **Default**
The primary storage backend for Arachne. It uses a local SQLite database file (`arachne.db`) located in the `data/` directory.
- **Deduplication**: Automatically handles job deduplication using a unique constraint on `(spider, external_id)`.
- **History**: Tracks when a job was first discovered and when it was last seen active.
- **Performance**: Significantly faster for large datasets than file-based storage.

### `JsonFileJobStorage` (`json.py`)
A legacy/debugging backend that saves data as human-readable JSON files.
- **Pros**: Zero-config, easy to inspect with a text editor.
- **Cons**: No deduplication (overwrites files), slow, no historical tracking.

## Configuration
You can toggle between storage backends in `config/global.yaml`:

```yaml
storage_type: "sqlite"  # Options: "sqlite", "json"
data_dir: "data"
```

## Database Schema (SQLite)
The SQLite implementation uses two main tables:
1.  **`jobs`**: Stores normalized job postings with timestamps for discovery and last confirmation.
2.  **`raw_data`**: Stores the most recent raw payload from each spider for inspection.
