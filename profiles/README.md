# Arachne Search Profiles

Search profiles define *what* you are looking for. While `config/sources.yaml` defines *where* to look, profiles define the criteria for the search and subsequent filtering.

## Profile Structure

Each `.yaml` file in this directory represents a distinct profile.

```yaml
name: "backend-london"

# Global criteria (passed to source adapters)
search:
  keywords: ["Python", "Go", "Distributed Systems"]
  locations: ["London", "Remote"]

# Global filters (applied after normalization)
filters:
  exclude_keywords: ["Java", "Frontend", "PHP"]
  min_date: "2024-01-01"

# Source-specific overrides (Optional)
sources:
  google:
    search:
      keywords: ["Software Engineer", "Site Reliability"]
```

## How it Works
1.  **Search Criteria**: The `search` block is passed to each source adapter. The adapter translates these general terms into provider-specific query parameters (e.g., Google might use `q=Python`, while Amazon might use `search_term=Python`).
2.  **Filters**: The `filters` block is used to prune the results *after* they have been normalized into our standard schema. This is useful for providers that have weak search APIs or return too much noise.
3.  **Overrides**: If a specific company (like Google) requires different keywords to get the same results, you can override the global search/filter settings for just that source.

## Usage
Select a profile when running the scraper:
```bash
uv run arachne run --profile backend-london
```
