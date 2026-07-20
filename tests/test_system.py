"""Tests for public system endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Jyothisyam API",
        "version": "0.1.0",
        "status": "running",
        "documentation": "/docs",
    }


def test_health_returns_healthy_status() -> None:
    response = client.get("/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "healthy"
    assert payload["service"] == "jyothisyam-api"
    assert payload["version"] == "0.1.0"
    assert payload["timestamp"].endswith("Z")


def test_openapi_document_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Jyothisyam API"
