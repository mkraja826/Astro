"""Integration tests for service-to-service calculation-route authentication."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROTECTED_ROUTE = "/v1/classical/varahamihira_v1/profile"
VALID_KEY = "astro-ci-service-key-0123456789abcdef"


def _clear_security(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JYOTHISYAM_REQUIRE_API_KEY", raising=False)
    monkeypatch.delenv("JYOTHISYAM_API_KEY", raising=False)


def test_local_calculation_routes_remain_available_without_security_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_security(monkeypatch)

    response = client.get(PROTECTED_ROUTE)

    assert response.status_code == 200


def test_required_auth_without_configured_key_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_security(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_API_KEY", "true")

    response = client.get(PROTECTED_ROUTE)

    assert response.status_code == 503
    assert response.json()["code"] == "API_AUTH_NOT_CONFIGURED"


def test_configured_service_key_requires_bearer_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_security(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)

    response = client.get(PROTECTED_ROUTE)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["code"] == "API_KEY_REQUIRED"


def test_invalid_service_key_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_security(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)

    response = client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": "Bearer wrong-service-key-0123456789abcdef"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "API_KEY_INVALID"


def test_valid_service_key_authorizes_calculation_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_security(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)

    response = client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": f"Bearer {VALID_KEY}"},
    )

    assert response.status_code == 200


def test_security_health_never_exposes_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_security(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)

    response = client.get("/health/security")
    payload = response.json()

    assert response.status_code == 200
    assert payload == {
        "status": "ready",
        "ready": True,
        "protection_enabled": True,
        "required": True,
        "configured": True,
        "valid_length": True,
        "scheme": "bearer",
        "minimum_key_length": 32,
    }
    assert VALID_KEY not in response.text


def test_openapi_declares_service_bearer_scheme() -> None:
    response = client.get("/openapi.json")
    document = response.json()

    assert response.status_code == 200
    assert "AstroServiceKey" in document["components"]["securitySchemes"]
    operation = document["paths"][PROTECTED_ROUTE]["get"]
    assert {"AstroServiceKey": []} in operation["security"]
