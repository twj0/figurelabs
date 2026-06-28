# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Python 3.11 FastAPI backend and a Vite React frontend. Backend code lives in `src/`: `src/api/` holds the app factory, schemas, and routers; `src/core/` contains database and storage logic; `src/chat/`, `src/register/`, and `src/export/` provide client and CLI-oriented modules. Tests are under `test/`, grouped by feature such as `test/chat/` and `test/register/`. Frontend source is in `frontend/src/`, with page components in `frontend/src/components/` and matching CSS modules. Runtime data belongs in `data/`; documentation, examples, scripts, and generated output are in `docs/`, `example/`, `scripts/`, and `output/`.

## Build, Test, and Development Commands

- `uv sync --dev`: install backend runtime and development dependencies from `pyproject.toml` and `uv.lock`.
- `uv run uvicorn src.api.app:app --port 7860 --reload`: run the API locally with reload enabled.
- `uv run pytest`: run the backend test suite configured in `pyproject.toml`.
- `uv run ruff check src test` and `uv run black src test`: lint and format Python code.
- `cd frontend && npm install`: install frontend dependencies.
- `cd frontend && npm run dev`: start the Vite dev server.
- `cd frontend && npm run build`: build frontend assets for production.
- `docker-compose up -d`: run the containerized service; use `docker-compose logs -f` for logs.

## Coding Style & Naming Conventions

Use Black and Ruff defaults configured for Python 3.11 with a 100-character line length. Python modules, files, functions, and variables use `snake_case`; classes use `PascalCase`. Keep API route code in `src/api/routers/` and request/response models in `src/api/schemas/`. React components use `PascalCase.jsx`, and component-specific styles use `ComponentName.module.css`.

## Testing Guidelines

Pytest discovers files named `test_*.py`, classes named `Test*`, and functions named `test_*` under `test/`. Add tests beside the relevant feature folder, for example `test/register/test_token.py`. Use `uv run pytest --cov=src` when checking coverage locally; no minimum threshold is currently configured.

## Commit & Pull Request Guidelines

Recent commits use short, direct messages such as `Update README.md`, `Clean up README by removing FAQs and license`, and `前端优化`. Keep commits focused and imperative. Pull requests should include a concise summary, linked issues when available, validation commands run, screenshots for UI changes, and notes for any `.env`, database, Docker, or deployment changes.

## Security & Configuration Tips

Copy `.env.example` to `.env` for local configuration and keep secrets out of version control. Confirm `PORT` and `DB_PATH` before running services that write to `data/`.
