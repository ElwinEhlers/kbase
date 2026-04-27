# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
docker compose up -d --build   # Build and start both containers
docker compose down            # Stop containers
docker compose logs -f         # Follow logs
```

The app is accessible at `http://<SERVER-IP>:8095` after startup. First-time setup requires creating the data directories:

```bash
mkdir -p data/docs www/docs
```

There is no build step — the frontend is a single HTML file served directly by nginx.

## Architecture

Two Docker containers managed by `docker-compose.yml`:

- **kbase** (nginx:alpine) — serves the static frontend from `/www/`, proxies `/api/*` to the Flask container, and serves uploaded docs from `/data/docs/`
- **kbase-api** (python:3.12-alpine + Flask) — REST API at port 5000 (internal only)

```
Browser → nginx:8095
  ├─ /api/* → kbase-api:5000 (Flask)
  └─ /*     → /usr/share/nginx/html (static)
```

**Data persistence:** `data/` is bind-mounted into both containers. `data/pages.json` is the sole source of truth for page metadata; `data/docs/` holds uploaded HTML/PDF files.

## Key Files

| File | Purpose |
|---|---|
| `www/index.html` | Entire frontend — HTML, CSS, and JS in one file (~85 KB) |
| `api/api.py` | Flask API: `GET/POST /api/pages`, `POST /api/upload` |
| `nginx.conf` | Reverse proxy config, security headers, cache rules |
| `data/pages.json` | Persisted pages array (managed by the API) |

## Frontend Structure (`www/index.html`)

All JavaScript is embedded in a single `<script>` block. Key functions:

- `loadPages()` / `savePages()` — fetch and persist the pages array via `/api/pages`
- `renderNav()` — builds the sidebar with category grouping and SortableJS drag-and-drop
- `renderTabs()` — manages the open-tab bar
- `openPage(id)` — loads HTML files into an iframe or PDFs into an `<embed>`
- `uploadFile()` — multipart POST to `/api/upload`

State is kept in a module-level `pages` array (JS objects with `id`, `title`, `path`, `category`). Navigation order is determined by array index.

## Backend (`api/api.py`)

Flask only — no ORM, no database. Routes:

- `GET /api/pages` — reads and returns `pages.json`
- `POST /api/pages` — accepts a JSON array, overwrites `pages.json`
- `POST /api/upload` — validates extension (`.html`, `.htm`, `.pdf`), sanitizes filename (alphanumeric + `._- `), saves to `/data/docs/`, returns the relative path

## Configuration

- **Username** shown in the UI: `const USER = 'sbin'` near the top of `www/index.html`
- **Port**: left side of `"8095:80"` in `docker-compose.yml`
- **Categories**: hardcoded array in `renderNav()` inside `www/index.html`
- No environment variables or `.env` file — all config is in-file
