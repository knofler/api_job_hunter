import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient


DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27010/jobhunter-app")
os.environ.setdefault("MONGO_URI", DEFAULT_MONGO_URI)

from app.core import database  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402  (import after setting env for settings initialisation)


@pytest.fixture(scope="session")
def mongodb_uri() -> str:
    """Provide the Mongo URI for tests; default to docker-compose mapping."""
    return DEFAULT_MONGO_URI


@pytest_asyncio.fixture(scope="session", autouse=True)
async def start_app(mongodb_uri: str) -> AsyncIterator[None]:
    # Ensure the application sees the expected Mongo URI before startup hooks run.
    os.environ.setdefault("MONGO_URI", mongodb_uri)
    database.client = AsyncIOMotorClient(mongodb_uri)
    database.db = database.client.get_database(settings.MONGO_DB_NAME)
    await app.router.startup()
    yield
    await app.router.shutdown()
    database.client.close()


@pytest_asyncio.fixture
async def async_client(mongodb_uri: str) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
