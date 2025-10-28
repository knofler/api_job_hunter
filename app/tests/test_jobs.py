import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_jobs(async_client: AsyncClient):
    response = await async_client.get("/jobs/")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert "total" in payload
    assert "page" in payload and payload["page"] == 1
    assert "page_size" in payload