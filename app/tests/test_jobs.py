from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_jobs():
    response = client.get("/jobs/")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert "total" in payload
    assert "page" in payload and payload["page"] == 1
    assert "page_size" in payload