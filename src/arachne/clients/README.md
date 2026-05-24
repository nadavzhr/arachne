# Arachne Clients

This package provides abstractions for network communication. By isolating the HTTP and browser logic, we can centrally manage timeouts, user-agent rotation, and retry logic.

## Supported Clients

### `http.py` (httpx)
The primary client for interacting with JSON APIs.
- **Asynchronous**: Built on top of `httpx.AsyncClient`.
- **Pre-configured**: Includes default timeouts and headers defined in `global.yaml`.

### `playwright.py` (Planned)
For job portals that are heavy on JavaScript and do not expose a clean JSON API.
- Will provide a wrapper around Playwright for headless browser scraping.

## Why Abstractions?
1. **Consistency**: Ensures every outgoing request uses the same `User-Agent`.
2. **Resilience**: A central place to implement exponential backoff or rate-limiting.
3. **Mockability**: Simplifies testing by allowing us to swap the real client with a mock in one place.
