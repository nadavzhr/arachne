# Meta Careers Spider Adapter

This adapter fetches and normalizes job listings from the Meta Careers portal.

## Implementation Details

- **Target URL**: Defined in `config/spiders.yaml`.
- **Normalization (`spider.py`)**: 
    - Maps Meta's job schema to the `JobPosting` model.
    - Specifically handles remote-friendly flags and team-based classification.

## Quirks
- Meta Careers uses GraphQL rather than a public REST API for job listings.
- The adapter uses an authenticated HTTP replay strategy to fetch job listings directly from Meta's GraphQL gateway. 
- It first visits the careers homepage to establish a session and extract an `LSD` security token, then re-uses those credentials to submit a search query.
- Requests are executed with session cookie persistence to ensure required tokens are preserved.

## Anti-Bot Evasion (Why `curl`?)
This spider intentionally shells out to `curl` via a subprocess instead of using the shared `httpx` client provided by `FetchContext`. Meta heavily rate-limits or outright blocks standard Python HTTP libraries, immediately returning a `429 Too Many Requests` error. By utilizing `curl`, the requests bypass these basic anti-bot heuristics and successfully retrieve the payload.

## GraphQL Document IDs (`doc_id`)

The adapter uses a hardcoded `doc_id` (`DEFAULT_DOC_ID` in `spider.py`) to identify the specific GraphQL query schema for job searches at Meta. This ID is relatively stable but may change if Meta updates their frontend.

### Design Decision
While it is possible to dynamically scrape the `doc_id` from the JavaScript bundles on the careers homepage, doing so is computationally expensive and fragile due to the complexity of Meta's bundled JS. A hardcoded ID is used for performance and reliability, with the understanding that it may require occasional manual updates.

### How to obtain a new `doc_id`:
If the spider returns `400 Bad Request` or empty results consistently, the `doc_id` may have changed:
1. Open a browser and go to [Meta Careers Jobs](https://www.metacareers.com/jobs).
2. Open **Developer Tools** (F12) and go to the **Network** tab.
3. Type a query into the search box on the page.
4. Look for a `POST` request to `/graphql`.
5. Check the **Payload** (or Form Data) of the request.
6. Locate the `doc_id` field and copy its value.
7. Update `DEFAULT_DOC_ID` in `src/arachne/spiders/meta/spider.py`.