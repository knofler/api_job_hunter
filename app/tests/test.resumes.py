from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_resumes():
    response = client.get("/resumes/")
    assert response.status_code == 200
    assert "message" in response.json()