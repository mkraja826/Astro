"""Tests for public system endpoints."""

from pathlib import Path

import pytest
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


def test_ephemeris_health_reports_missing_jpl_kernel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    response = client.get("/health/ephemeris")
    payload = response.json()

    assert response.status_code == 503
    assert payload["status"] == "degraded"
    assert payload["ready"] is False
    assert payload["provider"] == "skyfield_jpl"
    assert payload["model"] == "de440s"
    assert payload["automatic_download_enabled"] is False
    assert payload["issues"]


def test_jpl_specific_health_url_remains_an_alias(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    canonical = client.get("/health/ephemeris")
    alias = client.get("/health/ephemeris/jpl")

    assert alias.status_code == canonical.status_code
    assert alias.json() == canonical.json()


def test_openapi_document_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Jyothisyam API"
