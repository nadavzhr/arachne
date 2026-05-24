# Amazon Jobs Source Adapter

This adapter fetches and normalizes job listings from the Amazon Jobs portal.

## Implementation Details

- **Target URL**: Defined in `config/sources.yaml` (usually a public JSON endpoint).
- **Parameters (`params.py`)**: Maps `JobSearchCriteria` to Amazon's internal query keys:
    - `keywords` -> `search_term`
    - `locations` -> `location`
- **Normalization (`source.py`)**: 
    - Maps `id_icims` or `id` to `external_id`.
    - Handles complex JSON-encoded location strings in the `locations` field.
    - Captures `basic_qualifications` and `description` for the job summary.

## Quirks
- Amazon often returns multiple locations as a JSON-encoded string within an array. This adapter includes a specialized parser to extract and format these into a single "City, Country | City, Country" string.
