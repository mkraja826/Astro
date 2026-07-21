"""Integration tests for authenticated rate limiting and usage metering."""

import pytest
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient

from app.core.config import RuntimeSettings
from app.core.usage_hardening import require_metered_access
from app.core.usage_readiness import UsageConnectivityStatus
from app.main import create_app

VALID_KEY = "astro-ci-service-key-0123456789abcdef"
CONSUMER_ID = "11111111-1111-4111-8111-111111111111"
SECOND_CONSUMER_ID = "22222222-2222-4222-8222-222222222222"
PROTECTED_ROUTE = "/v1/classical/varahamihira_v1/profile"


def _settings(**overrides: object) -> RuntimeSettings:
    values: dict[str, object] = {
        "environment": "test",
        "log_level": "INFO",
        "allowed_hosts": ("testserver",),
        "cors_origins": (),
        "max_request_body_bytes": 1024,
        "request_timeout_seconds": 2.0,
        "docs_enabled": True,
        "usage_backend": "memory",
        "usage_required": True,
        "requests_per_minute": 60,
        "monthly_credit_limit": 0,
        "usage_rpc_timeout_seconds": 1.0,
    }
    values.update(overrides)
    return RuntimeSettings(**values)  # type: ignore[arg-type]


def _auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("JYOTHISYAM_API_KEY", VALID_KEY)


def _headers(request_id: str, consumer_id: str = CONSUMER_ID) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {VALID_KEY}",
        "X-Astro-Consumer-ID": consumer_id,
        "X-Request-ID": request_id,
    }


def test_missing_consumer_identity_is_rejected_after_service_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    client = TestClient(create_app(_settings(environment="staging", usage_required=False)))

    response = client.get(
        PROTECTED_ROUTE,
        headers={"Authorization": f"Bearer {VALID_KEY}"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "CONSUMER_ID_REQUIRED"
    assert response.headers["x-request-id"]


def test_invalid_consumer_identity_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    client = TestClient(create_app(_settings()))

    response = client.get(
        PROTECTED_ROUTE,
        headers={
            "Authorization": f"Bearer {VALID_KEY}",
            "X-Astro-Consumer-ID": "not-a-uuid",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "CONSUMER_ID_INVALID"


def test_per_minute_limit_returns_stable_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    client = TestClient(create_app(_settings(requests_per_minute=2)))

    first = client.get(PROTECTED_ROUTE, headers=_headers("rate-001"))
    second = client.get(PROTECTED_ROUTE, headers=_headers("rate-002"))
    limited = client.get(PROTECTED_ROUTE, headers=_headers("rate-003"))

    assert first.status_code == 200
    assert first.headers["x-ratelimit-limit"] == "2"
    assert first.headers["x-ratelimit-remaining"] == "1"
    assert first.headers["x-astro-credit-cost"] == "1"
    assert second.status_code == 200
    assert second.headers["x-ratelimit-remaining"] == "0"
    assert limited.status_code == 429
    assert limited.json()["code"] == "RATE_LIMIT_EXCEEDED"
    assert limited.headers["x-ratelimit-limit"] == "2"
    assert limited.headers["x-ratelimit-remaining"] == "0"
    assert int(limited.headers["retry-after"]) >= 1


def test_request_id_retries_are_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    client = TestClient(create_app(_settings(requests_per_minute=2)))

    original = client.get(PROTECTED_ROUTE, headers=_headers("same-request"))
    repeated = client.get(PROTECTED_ROUTE, headers=_headers("same-request"))
    second_unique = client.get(PROTECTED_ROUTE, headers=_headers("unique-002"))
    third_unique = client.get(PROTECTED_ROUTE, headers=_headers("unique-003"))

    assert original.status_code == 200
    assert repeated.status_code == 200
    assert second_unique.status_code == 200
    assert third_unique.status_code == 429


def test_failed_calculation_does_not_consume_monthly_credit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    application = create_app(
        _settings(requests_per_minute=10, monthly_credit_limit=1)
    )

    async def fail_after_admission() -> None:
        raise HTTPException(status_code=500, detail="simulated internal failure")

    application.add_api_route(
        "/test/fail",
        fail_after_admission,
        methods=["GET"],
        dependencies=[Depends(require_metered_access)],
    )
    client = TestClient(application, raise_server_exceptions=False)

    failed = client.get("/test/fail", headers=_headers("credit-failed"))
    successful = client.get(PROTECTED_ROUTE, headers=_headers("credit-success"))
    quota = client.get(PROTECTED_ROUTE, headers=_headers("credit-over"))

    assert failed.status_code == 500
    assert successful.status_code == 200
    assert quota.status_code == 429
    assert quota.json()["code"] == "MONTHLY_QUOTA_EXCEEDED"


def test_usage_counters_are_isolated_by_consumer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _auth(monkeypatch)
    client = TestClient(create_app(_settings(requests_per_minute=1)))

    first_consumer = client.get(PROTECTED_ROUTE, headers=_headers("one-001"))
    first_limited = client.get(PROTECTED_ROUTE, headers=_headers("one-002"))
    second_consumer = client.get(
        PROTECTED_ROUTE,
        headers=_headers("two-001", consumer_id=SECOND_CONSUMER_ID),
    )

    assert first_consumer.status_code == 200
    assert first_limited.status_code == 429
    assert second_consumer.status_code == 200


def test_production_memory_backend_is_not_ready() -> None:
    client = TestClient(
        create_app(
            _settings(
                environment="production",
                docs_enabled=False,
                usage_backend="memory",
                usage_required=True,
            )
        )
    )

    response = client.get("/health/usage")

    assert response.status_code == 503
    assert response.json()["backend"] == "memory"
    assert response.json()["durable"] is False
    assert response.json()["ready"] is False


def test_supabase_health_requires_server_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("JYOTHISYAM_SUPABASE_URL", raising=False)
    monkeypatch.delenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    client = TestClient(
        create_app(
            _settings(
                environment="production",
                docs_enabled=False,
                usage_backend="supabase",
                usage_required=True,
            )
        )
    )

    response = client.get("/health/usage")

    assert response.status_code == 503
    assert response.json()["configured"] is False
    assert "service" not in response.text.lower()


def test_supabase_health_exposes_no_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "supabase-service-role-secret-0123456789abcdef"
    monkeypatch.setenv(
        "JYOTHISYAM_SUPABASE_URL",
        "https://hdaugtypjpniesdgyral.supabase.co",
    )
    monkeypatch.setenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", secret)

    async def _ready_connectivity(settings: RuntimeSettings) -> UsageConnectivityStatus:
        del settings
        return UsageConnectivityStatus(
            ready=True,
            reachable=True,
            project_ref="hdaugtypjpniesdgyral",
            schema_version="api_usage_metering_safety_v1",
            latency_ms=1.0,
            issue=None,
        )

    monkeypatch.setattr(
        "app.api.routes.system.inspect_usage_connectivity",
        _ready_connectivity,
    )
    client = TestClient(
        create_app(
            _settings(
                environment="production",
                docs_enabled=False,
                usage_backend="supabase",
                usage_required=True,
            )
        )
    )

    response = client.get("/health/usage")

    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["durable"] is True
    assert secret not in response.text
