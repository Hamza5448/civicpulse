from collections.abc import AsyncIterator

import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.db.base import Base
from app.main import create_app


@pytest_asyncio.fixture
async def app(tmp_path):
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    application = create_app(Settings(database_url=database_url, log_level="WARNING"))
    redis = FakeRedis(decode_responses=True)
    application.state.redis = redis
    application.state.stats_cache.redis = redis
    application.state.rate_limiter.redis = redis
    engine = application.state.engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield application
    await redis.aclose()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest_asyncio.fixture
async def session(app) -> AsyncIterator[AsyncSession]:
    factory: async_sessionmaker[AsyncSession] = app.state.session_factory
    async with factory() as database_session:
        yield database_session
