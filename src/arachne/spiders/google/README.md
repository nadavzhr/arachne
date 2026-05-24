# Google Careers Spider Adapter

This adapter fetches and normalizes job listings from the Google Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Extracts job titles, locations, and descriptions from Google's complex JSON responses.
    - Maps experience levels and employment types to our standard internal schema.

## Quirks
- Google's API often returns a high volume of data; the `fetch` method is optimized to handle pagination and filtering at the spider level where possible.
