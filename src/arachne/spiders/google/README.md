# Google Careers Spider Adapter

This adapter fetches and normalizes job listings from the Google Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Extracts job titles, locations, and descriptions from Google's complex JSON responses.
    - Maps experience levels and employment types to our standard internal schema.

## Quirks
- Google does not provide a public API for job postings.
Therefore - we rely on web scraping techniques which may require frequent updates to the parsing logic as Google's page structure changes.
- Pagination is currently not supported, but junior roles (my main focus) are scarce enough that we can get by with just the first page of results for now.
