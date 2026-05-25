# Arachne Configuration

Arachne is configured using YAML files. This directory contains the system-wide settings and the registry of job spiders.

## Configuration Files

### `global.yaml`
General runtime settings.
- **`data_dir`**: Where to save scraped jobs (default: `data`).
- **`concurrency`**: Max number of spiders to scrape simultaneously.
- **`timeout_seconds`**: Network timeout for API calls.
- **`logging`**: Settings for file and console logs.

### `spiders.yaml`
A registry of all supported job portals.
- **`enabled`**: Toggle a spider on or off globally.
- **`url`**: The base API endpoint for the provider.
- **`headers`**: Optional static HTTP headers (e.g., for API keys or custom user agents).

## Validation
Configuration files are loaded and validated using Pydantic models defined in `src/arachne/config/loader.py`. If a required field is missing or a type is incorrect, the application will fail fast with a descriptive error message during bootstrap.
