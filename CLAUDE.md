# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FigureLabs AI — AI-powered chart/image generation platform. Backend (FastAPI/Python 3.11) proxies the FigureLabs.ai API with account management, session management, image generation, and multi-format export. Frontend (React 18 + Vite) provides Dashboard/Monitor/Accounts/Generate/Logs/Settings pages.

## Commands

```bash
# Backend dev server (project root)
uvicorn src.api.app:app --port 11451 --reload

# Frontend dev server (frontend/)
npm run dev          # proxies /api to localhost:7860

# Frontend build
npm run build

# Docker (full stack)
docker-compose up -d

# Tests
pytest                          # config in pyproject.toml, test dir: test/

# Linting
ruff check src/                 # configured in pyproject.toml
black --check src/              # line-length 100

# Dependencies
pip install -r requirements.txt  # or uv pip install -r requirements.txt
```

## Architecture

### Backend (`src/`)

- **`src/api/app.py`** — Main FastAPI app. All routes defined inline (accounts CRUD, chat session/message, download/export, stats). Serves built frontend from `frontend/dist/` if it exists.
- **`src/config.py`** — Env config via `python-dotenv`: `PORT` (default 11451), `DB_PATH` (default `./data/figurelabs.db`).
- **`src/db.py`** — Legacy account store using aiosqlite directly. Tables: `accounts` (user_id, email, access_token, etc.).
- **`src/core/storage.py`** — Storage abstraction layer. Auto-detects backend: `DATABASE_URL` env → PostgreSQL, `SQLITE_PATH` → SQLite. Tables: `accounts`, `kv_settings`, `kv_stats`, `request_logs`. Provides `load_accounts/save_accounts`, `load_settings/save_settings`, `load_stats/save_stats`.
- **`src/core/database.py`** — `StatsDatabase` class for request log analytics. `get_stats_by_time_range("24h"|"7d"|"30d")`, `get_total_counts()`, `cleanup_old_data()`. Singleton: `stats_db`.
- **`src/chat/client.py`** — `FigureLabsChat` client. Talks to `chat.figurelabs.ai` REST API. Methods: `create_session()`, `send_message()`, `get_message_status()`, `expand_prompt()`.
- **`src/export/client.py`** — `ExportClient` for downloading generated figures. `get_file_urls()`, `get_message_status()`.
- **`src/export/formats.py`** — Format-specific download/conversion logic.
- **`src/export/_session.py`** — Shared requests Session factory with auth headers/cookies.
- **`src/register/client.py`** — `FigureLabsRegistration` for auto-registering accounts.
- **`src/register/mail_service.py`** — MailTM and DuckMail email service wrappers.

### Frontend (`frontend/`)

- React 18, Vite 5, Zustand 5 (state), Recharts 3 (charts), CSS Modules (styling), react-router-dom 7, lucide-react (icons).
- **`src/App.jsx`** — Tab-based navigation shell (no router, uses `useState` for tab). 6 pages: Dashboard, Monitor, Accounts, Generate, Logs, Settings.
- **`src/store.js`** — Zustand store: `activeAccount`, `stats`.
- **Components**: `DashboardPage` (statistics), `MonitorPage` (real-time monitoring), `AccountsPage` (account CRUD), `GeneratePage` (chat/generate UI), `MessageBubble` (chat message display), `LogsPage` (request logs), `SettingsPage` (settings).
- Vite proxies `/api` to backend at `localhost:7860` in dev mode.

### Database

Two coexisting schemas:
1. **Legacy** (`src/db.py` via aiosqlite) — `accounts` table with direct CRUD.
2. **New** (`src/core/storage.py`) — SQLite or PostgreSQL auto-detected. Tables: `accounts`, `kv_settings`, `kv_stats`, `request_logs`.
- `StatsDatabase` in `src/core/database.py` uses the new storage layer for request log analytics.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/accounts` | List accounts |
| POST | `/api/accounts/register` | Register (mailtm/duckmail) |
| POST | `/api/accounts/verify-duckmail` | Verify duckmail code |
| DELETE | `/api/accounts/{user_id}` | Delete account |
| PATCH | `/api/accounts/{user_id}/label` | Update label |
| POST | `/api/session` | Create chat session |
| POST | `/api/message` | Send message / generate |
| GET | `/api/status/{message_id}` | Check generation status |
| POST | `/api/expand` | Expand prompt via AI |
| GET | `/api/download/{message_id}` | Download figure (png/jpg/svg/pptx) |
| GET | `/api/stats` | Aggregated stats (24h/7d/30d) |
| GET | `/api/stats/totals` | Total success/failed counts |

### CI/CD

GitHub Actions (`.github/workflows/docker.yml`) builds and pushes Docker image to `ghcr.io/twj0/figurelabs-ai` on push to `main`. Multi-stage Dockerfile: builds frontend with Node 20, then serves with Python 3.11-slim.
