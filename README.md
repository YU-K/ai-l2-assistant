# ai-l2-assistant

Каркас async-сервиса на FastAPI + Postgres (SQLAlchemy 2, Alembic). Пока есть только `GET /health`.

## Требования

- [uv](https://docs.astral.sh/uv/) (Python 3.12 он поставит сам)
- Docker с Compose

## Запуск

```bash
uv sync
cp .env.example .env
docker compose up -d db                 # Postgres на localhost:5432
uv run alembic upgrade head             # применить миграции
uv run uvicorn app.main:app --reload
curl localhost:8000/health              # {"status":"ok"}
```

Документация API: http://localhost:8000/docs

Запуск приложения в контейнере вместо хоста:

```bash
docker compose --profile app up -d --build
```

Контейнер при старте сам выполняет `alembic upgrade head`, затем запускает uvicorn.
Чтобы обычный `docker compose up` поднимал и приложение, добавьте в `.env` строку `COMPOSE_PROFILES=app`.

## Тесты и линтер

Тестам нужна запущенная БД (`docker compose up -d db`).

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Миграции

```bash
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

## Структура

```
app/config.py        настройки из env / .env
app/db.py            Base, async engine, get_session
app/main.py          FastAPI-приложение и /health
alembic/             миграции
tests/               pytest + httpx.AsyncClient
docker-compose.yml   db (+ app под профилем "app")
Dockerfile           образ приложения
```
