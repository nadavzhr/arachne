# 🗺️ Arachne Roadmap

This document outlines the planned trajectory for the Arachne project. As a personal project, these milestones are subject to change but represent the core vision for the application.

---

## 🛰️ Phase 1: API Layer (Backend)
The goal is to move beyond the CLI and allow external applications to interact with the Arachne engine.

- [ ] **FastAPI Integration**: Scaffold a modern, typed API.
- [ ] **Background Task Orchestration**: Allow trigger-and-forget scraping runs via the API.
- [X] **Dockerization**: Create a production-ready container image.
- [X] **GitHub Actions Automation**: Set up a scheduled workflow to run spiders once a day.
- [ ] **Status Monitoring**: Endpoints to check the progress and logs of active spider runs.
- [ ] **Profile Management**: API endpoints to CRUD search profiles and configurations.
- [ ] **Job Retrieval**: Paginated and searchable endpoints for the aggregated job data.

## 🗄️ Phase 2: Persistence & Scalability
Transitioning from simple file snapshots to a robust local database.

- [X] **SQLite Implementation**: Replace JSON file storage with a relational database for faster querying.
- [ ] **Historical Tracking**: Detect when jobs are added, updated, or closed (differential snapshots).
- [ ] **Deduplication**: Logic to handle the same job appearing across multiple spiders or search runs.
- [ ] **Search Engine**: Full-text search (FTS) capabilities within the local database.

## 🎨 Phase 3: The Web Interface (Frontend)
A visual dashboard to manage the web of job data.

- [ ] **Interactive Dashboard**: Overview of recent scraping activity and job market trends.
- [ ] **Job Explorer**: A rich table interface with advanced filtering, sorting, and direct links.
- [ ] **Config Editor**: A UI-based editor for search profiles and global settings.
- [ ] **Spider Control Center**: Manual trigger buttons and live log streaming for active runs.

## 🕷️ Phase 4: Advanced Spider Capabilities
Expanding the reach of our web.

- [ ] **Advanced Replay**: Support for JS-heavy portals via authenticated HTTP replay.
- [ ] **Proxy Support**: Native handling for rotating proxies to avoid rate-limiting.
- [ ] **Notification Sinks**: Webhooks or integrations (Slack/Discord) for new job alerts.
