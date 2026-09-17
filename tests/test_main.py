from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "API Monitoring Platform is running!"
    )


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

def test_invalid_route():
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404