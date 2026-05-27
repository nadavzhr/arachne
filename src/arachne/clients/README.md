# 🔌 Arachne Clients

This package contains the shared HTTP clients used by Arachne spiders.

## 🧱 Core Clients

### `http.py`
- **ThrottledClient**: A wrapper around `httpx.AsyncClient` that enforces global concurrency limits and provides automatic retries for transient network errors.
- **Helper Functions**: Includes `fetch_json` and `fetch_paginated_json` for common API patterns.

## 🏗️ Architecture

Arachne uses a shared client model to ensure resource efficiency and compliance with provider rate limits. Spiders receive a `FetchContext` during their execution, which contains:

- `http`: The primary `ThrottledClient` instance for making requests.

# 🧑‍💻 Adding New Clients
To add a new client, follow these steps:
1. Create a new client class in `arachne.clients` that encapsulates the desired functionality.
2. Ensure the client is designed to be thread-safe and can be shared across multiple spiders.
3. Update the `FetchContext` to include an instance of your new client.
4. In your spider, access the new client via the `FetchContext` and use it to perform the necessary operations.

