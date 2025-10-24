from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_ranking():
    payload = {"user_skills": ["Python", "FastAPI"], "job_skills": ["Python", "Docker"]}
    response = client.post("/ranking/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data