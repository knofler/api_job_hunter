import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_get_users(async_client: AsyncClient):
    response = await async_client.get("/users/")
    assert response.status_code == 200
    payload = response.json()
    assert "users" in payload