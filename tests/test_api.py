import requests
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_current_temp_success():
    response = client.get("/current_temperature/?city_name=London&country_code=GB")
    assert response.status_code == 200
    assert "Temperature" in response.json()
    assert "Description" in response.json()


def test_get_current_temp_invalid_city_name():
    response = client.get("/current_temperature/?city_name=&country_code=GB")
    assert response.status_code == 422  # Unprocessable Entity due to validation error


def test_get_current_temp_invalid_country_code():
    response = client.get("/current_temperature/?city_name=London&country_code=")
    assert response.status_code == 422  # Unprocessable Entity due to validation error


def test_get_current_temp_api_failure(monkeypatch):
    # Simulate an API failure
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 404
            json = lambda x: {"message": "Not Found"}

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    response = client.get("/current_temperature/?city_name=London&country_code=GB")
    assert response.status_code == 404
    assert response.json() == {"detail": "Failed to fetch temperature data"}


def test_missing_api_key(monkeypatch):
    # Remove API key from environment variables
    monkeypatch.delenv("API_KEY", raising=False)

    response = client.get("/current_temperature/?city_name=London&country_code=GB")
    assert response.status_code == 401
