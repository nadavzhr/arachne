# Arachne Search Profiles

Search profiles define *what* you are looking for. While `config/spiders.yaml` defines *where* to look, profiles define the criteria for the search and subsequent filtering.

## Profile Structure

Each `.yaml` file in this directory represents a distinct profile.

```yaml
name: "backend-london"

# Global criteria (passed to spider adapters)
search:
  title: "Software Engineer"
  locations: ["London", "Remote"]

# Global filters (applied after normalization)
# Filters are field-specific and support inclusion/exclusion keywords
filters:
  title:
    include_keywords: ["Python", "Go"]
    exclude_keywords: ["Java", "Frontend", "PHP"]
  location:
    exclude_keywords: ["london", "new york", "san francisco"]
  company:
    exclude_keywords: ["Recruitment Agency"]

# Spider-specific overrides (Optional)
spiders:
  google:
    search:
      title: "Site Reliability Engineer"
```

## How it Works
1.  **Search Criteria**: The `search` block is passed to each spider adapter. The adapter translates these general terms into provider-specific query parameters (e.g., Google might use `q=Software+Engineer`, while Amazon might use `search_term=Software+Engineer`).
2.  **Filters**: The `filters` block is used to prune the results *after* they have been normalized into our standard schema. This is useful for providers that have weak search APIs or return too much noise. Each filter field supports:
    *   `include_keywords`: If specified, at least one keyword must be present (case-insensitive) in the field.
    *   `exclude_keywords`: If specified, none of these keywords can be present (case-insensitive) in the field.
3.  **Available Filter Fields**:
    *   `title`: Job title.
    *   `location`: Geographic location string.
    *   `company`: Hiring company name.
    *   `description`: Job description or requirements.
4.  **Overrides**: If a specific company (like Google) requires different parameters to get the same results, you can override the global search/filter settings for just that spider.

## Usage
Select a profile when running the scraper:
```bash
uv run arachne run --profile backend-london
```
