from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_recruiters_paginates():
    response = client.get("/recruiters/", params={"page": 1, "page_size": 5})
    assert response.status_code == 200
    payload = response.json()

    assert "items" in payload
    assert len(payload["items"]) == 5
    assert payload["total"] >= 20
    assert payload["page"] == 1
    assert payload["page_size"] == 5
