# Apple Jobs Spider Adapter

This adapter fetches and normalizes job listings from the Apple Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Maps Apple's internal job fields to the `JobPosting` model.
    - Handles Apple-specific location formatting and job categories.

## Quirks
- Apple's job portal often has specific header requirements or rate-limiting patterns that are handled within the `fetch` logic.
