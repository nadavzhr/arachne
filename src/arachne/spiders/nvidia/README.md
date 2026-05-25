# NVIDIA Careers Spider Adapter

This adapter fetches and normalizes job listings from the NVIDIA Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Maps Workday-based job fields to the `JobPosting` model.
    - Extracts posting dates and location details.

## Quirks
- None, NVIDIA's API is relatively straightforward and consistent compared to other portals.
