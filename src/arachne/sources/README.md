# Arachne Source Adapters

Source adapters are the bridge between Arachne and the external world. Each directory here represents a specific job portal (e.g., Amazon, Google, Meta).

## How to Add a New Source

Adding a new source is a 4-step process:

### 1. Create the Directory Structure
Create a new package under `src/arachne/sources/`.
```text
src/arachne/sources/new_company/
├── __init__.py
├── params.py   # Optional: Logic for building API query params
└── source.py   # The adapter implementation
```

### 2. Implement the `Source` Class
In `source.py`, inherit from `arachne.sources.base.Source` and implement the abstract methods:

```python
from arachne.sources.base import Source as BaseSource
from arachne.models.job import JobPosting

class NewCompanySource(BaseSource):
    async def fetch(self, client, search):
        # 1. Map 'search' criteria to API params
        # 2. Make the HTTP call using 'client'
        # 3. Return the raw payload (usually a dict or list)
        pass

    def normalize(self, raw):
        # 1. Iterate through the raw items
        # 2. Map fields to the JobPosting model
        # 3. Return a list of JobPosting objects
        pass
```

### 3. Register the Class
In `__init__.py`, export the class as `Source`:
```python
from .source import NewCompanySource as Source
```

### 4. Add to Configuration
Add the new source to `config/sources.yaml`:
```yaml
new_company:
  enabled: true
  url: "https://api.newcompany.com/jobs"
```

## Source Registry
Arachne uses a dynamic loading mechanism (`src/arachne/sources/__init__.py`). It looks for a `Source` attribute in the sub-package named in your configuration. This means you don't need to manually register your class in a central list.

## Best Practices
- **Use `self.log`**: Always use the built-in logger adapter. It ensures your logs are routed to `logs/sources/<name>.log`.
- **Be Defensive**: External APIs change. Use `.get()` and try-except blocks during normalization to ensure one bad record doesn't crash the entire scrape.
- **Isolate Param Logic**: If the API query is complex, move the logic to `params.py`.
