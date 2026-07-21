"""Safety tests for Astro-bound metering and request identity."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import RuntimeSettings
from app.core.usage import UsageAdmission
from app.core.usage_hardening import ASTRO_SUPABASE_PROJECT_REF, inspect_usage_policy
from app.main import create_app

VALID_KEY = "astro-ci-service-key-0123456789abcdef"
CONSUMER_ID = "11111111-1111-4111-8111-111111111111"
PROTECTED_ROUTE = "/v1/classical/varahamihira_v1/profile"


def _settings(**overrides: Any) -> RuntimeSettings:
    values: dict[str, Any] = {
        "environment": "production",
        "log_level": "INFO",
        "allowed_hosts": ("testserver",),
        "cors_origins": (),
        "max_request_body_bytes": 1024,
        "request_timeout_seconds": 2.0,
        "docs_enabled": False,
        "usage_backend": "supabase",
        "usage_required": True,
        "requests_per_minute": 60,
        "monthly_credit_limit": 0,
        "usage_rpc_timeout_seconds": 1.0,
    }
    values.update(overrides)
    return RuntimeSettings(**values)


def _clear_supabase_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "JYOTHISYAM_SUPABASE_URL",
        "JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_generic_supabase_credentials_are_never_used(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv("SUPABASE_URL", "https://mzjtdcpbvoximdukpukd.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "x" * 40)

    report = inspect_usage_policy(_settings())

    assert report.ready is False
    assert report.configured is False


def test_wrong_project_url_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(
        "JYOTHISYAM_SUPABASE_URL",
        "https://mzjtdcpbvoximdukpukd.supabase.co",
    )
    monkeypatch.setenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", "x" * 40)

    report = inspect_usage_policy(_settings())

    assert report.ready is False
    assert report.configured is False


def test_exact_astro_project_url_is_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_supabase_env(monkeypatch)
    monkeypatch.setenv(
        "JYOTHISYAM_SUPABASE_URL",
        f"https://{ASTRO_SUPABASE_PROJECT_REF}.supabase.co",
    )
    monkeypatch.setenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", "x" * 40)

    report = inspect_usage_policy(_settings())

    assert report.ready is True
    assert report.configured is True


class _ReusedRequestBackend:
    async def admit(self, **kwargs: Any) -> UsageAdmission:
        return UsageAdmission(
            allowed=False,
            request_id=kwargs["request_id"],
            consumer_id=kwargs["consumer_id"],
            route_key=kwargs["route_key"],
            credit_cost=kwargs["credit_cost"],
            limit=kwargs["requests_per_minute"],
            remaining=kwargs["requests_per_minute"] - 1,
            retry_after_seconds=0,
            reason="REQUEST_ID_REUSED",
        )

    async def finalize(self, *, request_id: str, response_status: int) -> None:
        del request_id, response_status


def test_reused_request_id_returns_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)
    application = create_app(
        _settings(
            environment="staging",
            usage_backend="memory",
            usage_required=False,
        )
    )
    application.state.usage_backend = _ReusedRequestBackend()
    client = TestClient(application)

    response = client.get(
        PROTECTED_ROUTE,
        headers={
            "Authorization": f"Bearer {VALID_KEY}",
            "X-Astro-Consumer-ID": CONSUMER_ID,
            "X-Request-ID": "already-used-request",
        },
    )

    assert response.status_code == 409
    assert response.json()["code"] == "REQUEST_ID_REUSED"
    assert "retry-after" not in response.headers
    assert response.headers["x-ratelimit-limit"] == "60"
