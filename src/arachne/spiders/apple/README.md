# Apple Jobs Spider Adapter

This adapter fetches and normalizes job listings from the Apple Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Maps Apple's internal job fields to the `JobPosting` model.
    - Handles Apple-specific location formatting and job categories.

## Quirks
- To properly interact with Apple's API, we first acquire a CSRF token (which is essentially a cookie) by making an initial request to the main jobs page. This token is then included in the headers of subsequent API requests to fetch job listings.
- Apple's API returns job listings in a paginated format, requiring multiple requests to retrieve all available jobs. The adapter includes logic to handle pagination and ensure that all listings are fetched and normalized correctly.