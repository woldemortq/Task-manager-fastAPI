import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from task_api.infrastructure.db.db import async_sessionmaker

from main import app


@pytest.fixture(scope='module')
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture()
async def db_session() -> AsyncSession:
    async with async_sessionmaker() as session:
        yield session