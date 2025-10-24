from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_candidates_paginates():
    response = client.get("/candidates/", params={"page": 1, "page_size": 5})
    assert response.status_code == 200
    payload = response.json()

    assert "items" in payload
    assert len(payload["items"]) == 5
    assert payload["total"] >= 100
    assert payload["page"] == 1
    assert payload["page_size"] == 5


def test_candidate_profile_available():
    response = client.get("/candidates/candidate_1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_id"] == "candidate_1"
