# Arachne Clients

This package provides abstractions for network communication. By isolating the HTTP and browser logic, we can centrally manage timeouts, user-agent rotation, and retry logic.

## Supported Clients

### `http.py` (httpx)
The primary client for interacting with JSON APIs.
- **Asynchronous**: Built on top of `httpx.AsyncClient`.
- **Pre-configured**: Includes default timeouts and headers defined in `global.yaml`.

### `playwright.py`
For job portals that are heavy on JavaScript and do not expose a clean JSON API.
- **PlaywrightManager**: Centrally manages the lifecycle of the browser process.
- **Isolated Contexts**: Provides ephemeral browser contexts and pages per spider run.

## Fetch Context
The `FetchContext` (defined in `base.py`) is the primary object passed to spiders. It contains:
- `http`: An instance of `httpx.AsyncClient`.
- `browser`: The `PlaywrightManager` instance.


## Why Abstractions?
1. **Consistency**: Ensures every outgoing request uses the same `User-Agent`.
2. **Resilience**: A central place to implement exponential backoff or rate-limiting.
3. **Mockability**: Simplifies testing by allowing us to swap the real client with a mock in one place.
