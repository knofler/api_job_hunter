from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_ranking():
    response = client.post("/ranking/", json={"user_id": "1", "job_id": "2", "skills": ["Python"], "experience": 3})
    assert response.status_code == 200
    assert "message" in response.json()