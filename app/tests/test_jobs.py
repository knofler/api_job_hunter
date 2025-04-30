from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_jobs():
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert "message" in response.json()