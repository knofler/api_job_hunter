import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def client():
    """Synchronous test client for simple tests."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for async tests."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client