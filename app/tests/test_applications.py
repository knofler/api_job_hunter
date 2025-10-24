from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_candidate_applications_paginated():
    response = client.get("/applications/candidates/candidate_1", params={"page": 1, "page_size": 5})
    assert response.status_code == 200
    payload = response.json()

    assert "items" in payload
    assert "total" in payload
    assert payload["page"] == 1
    assert payload["page_size"] == 5
    assert isinstance(payload["items"], list)
