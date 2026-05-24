# Google Careers Source Adapter

This adapter fetches and normalizes job listings from the Google Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/sources.yaml`.
- **Normalization (`source.py`)**: 
    - Extracts job titles, locations, and descriptions from Google's complex JSON responses.
    - Maps experience levels and employment types to our standard internal schema.

## Quirks
- Google's API often returns a high volume of data; the `fetch` method is optimized to handle pagination and filtering at the source level where possible.
