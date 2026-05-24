# Arachne Storage Layer

The storage layer is responsible for persisting job data and raw API responses. It uses an interface-based design to allow for easy swapping of storage backends.

## The Interface: `JobStorage` (`base.py`)
Any storage implementation must satisfy the `JobStorage` abstract base class, which defines methods for:
- `save_jobs`: Persisting a list of `JobPosting` objects.
- `load_jobs`: Retrieving jobs for a specific spider.
- `save_raw`: Saving the raw, un-normalized API response for debugging.

## Implementations

### `JsonFileJobStorage` (`json.py`)
The current default implementation. It saves data as human-readable JSON files in the `data/` directory.
- **Pros**: Zero-config, easy to inspect with a text editor, git-friendly (if small).
- **Cons**: No indexing, slow for large datasets, does not support complex queries.

## Data Structure (JSON Storage)
When using the JSON backend, the `data/` directory is organized as follows:
```text
data/
└── <spider_name>/
    ├── raw.json             # The last raw API response
    ├── jobs.unfiltered.json # All normalized jobs before filtering
    └── jobs.json            # Final jobs after profile filters
```

## Future Roadmap
As the project grows, we plan to implement:
- **`SqliteJobStorage`**: For better performance and local querying.
- **`PostgresJobStorage`**: For production/multi-user deployments.
