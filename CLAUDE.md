# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

`ai-l2-assistant` is a minimal async FastAPI service skeleton: FastAPI + Postgres (Docker Compose) + async SQLAlchemy 2 + Alembic + pytest + ruff. There is no business logic yet — only `GET /health`. The structure is intentionally flat; split into subpackages only when it gets crowded.

## Commands

Package manager is `uv` (Python 3.12). Prefix tools with `uv run`.

```bash
uv sync                                   # install deps (incl. dev group)
cp .env.example .env                      # first time only
docker compose up -d db                   # start Postgres (localhost:5432)
uv run uvicorn app.main:app --reload      # run app on host → http://localhost:8000
docker compose --profile app up -d --build  # run app in a container instead

uv run pytest                             # all tests (needs running db)
uv run pytest tests/test_health.py::test_health   # single test
uv run ruff check . && uv run ruff format --check .

uv run alembic revision --autogenerate -m "msg"   # new migration
uv run alembic upgrade head                       # apply migrations
```

## Architecture

- `app/config.py` — `Settings` (pydantic-settings); reads `DATABASE_URL` from env or `.env`.
- `app/db.py` — `Base` (DeclarativeBase with naming convention), async `engine`, `SessionLocal`, and `get_session()` FastAPI dependency (one `AsyncSession` per request).
- `app/main.py` — `FastAPI` app; `lifespan` disposes the engine on shutdown; `/health` runs `SELECT 1`.
- `alembic/env.py` — async template; takes the URL from `app.config.settings` (the `sqlalchemy.url` in `alembic.ini` is ignored) and uses `Base.metadata` for autogenerate. New models must be imported before `env.py` reads `Base.metadata`, or autogenerate won't see them.
- `tests/conftest.py` — `client` fixture: `httpx.AsyncClient` over `ASGITransport` (no server, no lifespan), plus a session-scoped fixture that disposes the engine. Tests hit the real Compose Postgres; there is no separate test DB.
- `docker-compose.yml` — `db` (postgres:16, healthcheck, volume `pgdata`) and `app` (behind profile `app`, `DATABASE_URL` points to host `db`). `Dockerfile` installs locked deps with uv, no dev group.

Gotchas:
- SQLAlchemy must be installed as `sqlalchemy[asyncio]` (needs `greenlet`).
- pytest uses one session-scoped event loop (`pyproject.toml`) because the engine is a module-level global.
- If the current shell isn't in the `docker` group yet, run docker commands via `sg docker -c '...'`.

## Repository

- Default branch: `main`
- Remote: `origin` → https://github.com/YU-K/ai-l2-assistant.git
