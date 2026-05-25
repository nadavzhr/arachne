# Arachne Data Storage

This directory contains the persisted results of scraping runs.

## Structure
Arachne uses SQLite to store all scraped jobs, ensuring deduplication and maintaining a history of job postings.

```text
data/
├── arachne.db       # The main SQLite database containing all normalized jobs
├── jobs.json        # Exported JSON dump of all jobs (used by the UI)
└── README.md
```

## Git Policy
By default, the `data/` directory contents are **ignored by Git**, with the exception of the `arachne.db` schema/baseline and this `README.md`. 
The `jobs.json` file is also ignored by default, but it is periodically updated and committed by a GitHub Actions workflow to serve as a static API for the frontend UI.
