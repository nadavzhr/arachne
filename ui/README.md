# Arachne UI

Static React + Vite dashboard for viewing exported job data.

## Run locally

```bash
npm install
uv run arachne run
uv run arachne export \
  --output ui/public/jobs.json \
  --analytics-output ui/public/analytics.json \
  --config-output ui/public/system_config.json
npm run dev
```

## Data source

The UI reads from public/jobs.json. Write a static snapshot directly into
`ui/public` (local/CI):

```bash
uv run arachne export \
  --output ui/public/jobs.json \
  --analytics-output ui/public/analytics.json \
  --config-output ui/public/system_config.json
```

For GitHub Pages, the scheduled workflow scrapes, exports into ui/public, builds, and deploys in one run.
