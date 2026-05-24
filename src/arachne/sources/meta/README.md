# Meta Careers Source Adapter

This adapter fetches and normalizes job listings from the Meta Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/sources.yaml`.
- **Normalization (`source.py`)**: 
    - Maps Meta's job schema to the `JobPosting` model.
    - Specifically handles remote-friendly flags and team-based classification.

## Quirks
- Meta's API frequently updates its field names; this adapter is designed with fallback logic to remain resilient to minor schema changes.
