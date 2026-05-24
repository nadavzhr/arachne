# Microsoft Careers Spider Adapter

This adapter fetches and normalizes job listings from the Microsoft Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Maps Microsoft's internal job IDs and descriptive fields to the `JobPosting` model.
    - Handles global location strings and relocation indicators.

## Quirks
- Microsoft's portal can be highly dynamic; the `fetch` method includes specific error handling for transient gateway timeouts.
