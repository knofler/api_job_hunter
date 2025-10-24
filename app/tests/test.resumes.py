from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_resumes():
    response = client.get("/resumes/candidate_1")
    assert response.status_code == 200
    payload = response.json()
    assert "resumes" in payload