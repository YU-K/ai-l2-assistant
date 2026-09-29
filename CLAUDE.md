# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

`ai-l2-assistant` is a small async FastAPI service: FastAPI + Postgres (Docker Compose) + async SQLAlchemy 2 + Alembic + pytest + ruff. Endpoints: `GET /health`, `POST /tickets`, `GET /tickets/{id}`. The structure is intentionally flat; split into subpackages only when it gets crowded.

## Commands

Package manager is `uv` (Python 3.12). Prefix tools with `uv run`.

First-time setup:

```bash
uv sync                                   # install deps (incl. dev group)
cp .env.example .env
docker compose up -d db                   # start Postgres (localhost:5432)
uv run alembic upgrade head               # create tables (needed before running the app on host or tests)
```

Run the app (either way):

```bash
uv run uvicorn app.main:app --reload        # on host → http://localhost:8000 (docs at /docs)
docker compose --profile app up -d --build  # in a container; it applies migrations itself on start
```

Tests and lint (need a running `db` with migrations applied):

```bash
uv run pytest                             # all tests
uv run pytest tests/test_health.py::test_health   # single test
uv run ruff check . && uv run ruff format --check .
```

Migrations:

```bash
uv run alembic revision --autogenerate -m "msg"   # new migration
uv run alembic upgrade head                       # apply migrations
uv run alembic downgrade -1                       # roll back one migration
uv run alembic current                            # show applied revision
```

## Architecture

- `app/config.py` — `Settings` (pydantic-settings); reads `DATABASE_URL` from env or `.env`.
- `app/db.py` — `Base` (DeclarativeBase with naming convention), async `engine`, `SessionLocal`, and `get_session()` FastAPI dependency (one `AsyncSession` per request).
- `app/models.py` — SQLAlchemy models: `Ticket` and `TicketStatus` (`StrEnum`, currently only `new`).
- `app/schemas.py` — Pydantic schemas: `TicketCreate` (`extra="forbid"`; `id`, `status`, `created_at` are set by the server) and `TicketRead`.
- `app/tickets.py` — `APIRouter` with prefix `/tickets`: `POST /tickets` (201) and `GET /tickets/{ticket_id}` (404 if missing).
- `app/main.py` — `FastAPI` app; includes the tickets router; `lifespan` disposes the engine on shutdown; `/health` runs `SELECT 1`.
- `alembic/env.py` — async template; takes the URL from `app.config.settings` (the `sqlalchemy.url` in `alembic.ini` is ignored) and uses `Base.metadata` for autogenerate. It does `import app.models`, so new models must live in `app/models.py` (or be imported there), otherwise autogenerate won't see them. Migrations are in `alembic/versions/` (currently one: `create tickets`).
- `tests/conftest.py` — `client` fixture: `httpx.AsyncClient` over `ASGITransport` (no server, no lifespan), plus a session-scoped fixture that disposes the engine. Tests (`test_health.py`, `test_tickets.py`) hit the real Compose Postgres; there is no separate test DB and created tickets are not cleaned up.
- `docker-compose.yml` — `db` (postgres:16, healthcheck, volume `pgdata`) and `app` (behind profile `app`, `DATABASE_URL` points to host `db`). Both ports are bound to `127.0.0.1`; Postgres credentials come from `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` in `.env` (with defaults). `app` starts only when the `app` profile is active: via `--profile app` or `COMPOSE_PROFILES=app` in `.env` (not set in `.env.example`); with it, plain `docker compose up` starts `app` too.
- `Dockerfile` — installs locked deps with uv, no dev group; the container runs `alembic upgrade head` before `exec uvicorn` (a failed migration stops startup). `.dockerignore` excludes `tests/` and `.env`, so tests can't be run inside the container.

Gotchas:
- SQLAlchemy must be installed as `sqlalchemy[asyncio]` (needs `greenlet`).
- pytest uses one session-scoped event loop (`pyproject.toml`) because the engine is a module-level global.
- `Ticket.status` is a plain `VARCHAR(20)` with a server default, not a Postgres ENUM; a new status only needs a new `TicketStatus` value, no migration.
- While the `app` container is running, port 8000 is taken, so uvicorn on the host can't start; tests on the host need only `db`.
- If the current shell isn't in the `docker` group yet, run docker commands via `sg docker -c '...'`.

## Repository

- Default branch: `main`
- Remote: `origin` → https://github.com/YU-K/ai-l2-assistant.git
