from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import engine
from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # ASGITransport вызывает приложение напрямую, без запуска uvicorn
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def dispose_engine() -> AsyncIterator[None]:
    # ASGITransport не запускает lifespan, поэтому пул соединений закрываем сами
    yield
    await engine.dispose()
