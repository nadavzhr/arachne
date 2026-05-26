# Google Careers Spider Adapter

This adapter fetches and normalizes job listings from the Google Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml` and should point to the
    `batchexecute` endpoint.
- **Fetch (`spider.py`)**:
    - Replays the batchexecute request used by the Google Careers UI.
    - Maps search criteria (query, locations, experience levels) into the payload.
- **Normalization (`spider.py`)**:
    - Extracts job titles, locations, and descriptions from the batchexecute payload.

## Quirks
- Google does not provide a public API for job postings.
    This implementation replays an internal request that may change.