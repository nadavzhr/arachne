# Arachne Spider Adapters

Spider adapters are the bridge between Arachne and the external world. Each directory here represents a specific job portal (e.g., Amazon, Google, Meta).

## How to Add a New Spider

Adding a new spider is a 4-step process:

### 1. Create the Directory Structure
Create a new package under `src/arachne/spiders/`.
```text
src/arachne/spiders/new_company/
├── __init__.py
├── params.py   # Optional: Logic for building API query params
└── spider.py   # The adapter implementation
```

### 2. Implement the `Spider` Class
In `spider.py`, inherit from `arachne.spiders.base.Spider` and implement the abstract methods:

```python
from arachne.spiders.base import Spider as BaseSpider
from arachne.models.job import JobPosting

class NewCompanySpider(BaseSpider):
    async def fetch(self, ctx, search):
        # 1. Map 'search' criteria to API params
        # 2. Make the HTTP call using 'ctx.http' (or 'ctx.browser' for Playwright)
        # 3. Return the raw payload (usually a dict or list)
        pass

    def normalize(self, raw):
        # 1. Iterate through the raw items
        # 2. Map fields to the JobPosting model
        # 3. Return a list of JobPosting objects
        pass
```

### 3. Register the Class
In `__init__.py`, export the class as `Spider`:
```python
from .spider import NewCompanySpider as Spider
```

### 4. Add to Configuration
Add the new spider to `config/spiders.yaml`:
```yaml
new_company:
  enabled: true
  url: "https://api.newcompany.com/jobs"
```

## Spider Registry
Arachne uses a dynamic loading mechanism (`src/arachne/spiders/__init__.py`). It looks for a `Spider` attribute in the sub-package named in your configuration. This means you don't need to manually register your class in a central list.

## Best Practices
- **Use `self.log`**: Always use the built-in logger adapter. It ensures your logs are routed to `logs/spiders/<name>.log`.
- **Be Defensive**: External APIs change. Use `.get()` and try-except blocks during normalization to ensure one bad record doesn't crash the entire scrape.
- **Isolate Param Logic**: If the API query is complex, move the logic to `params.py`.
