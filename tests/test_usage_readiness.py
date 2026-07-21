"""Tests for non-mutating durable usage-backend readiness."""

import asyncio
from urllib.error import URLError

import pytest

from app.core.config import RuntimeSettings
from app.core.usage_readiness import inspect_usage_connectivity

ASTRO_URL = "https://hdaugtypjpniesdgyral.supabase.co"
SERVICE_KEY = "astro-service-role-key-0123456789abcdef"


def _settings(**overrides: object) -> RuntimeSettings:
    values: dict[str, object] = {
        "environment": "production",
        "log_level": "INFO",
        "allowed_hosts": ("api.example.com",),
        "cors_origins": (),
        "max_request_body_bytes": 1_048_576,
        "request_timeout_seconds": 30.0,
        "docs_enabled": False,
        "usage_backend": "supabase",
        "usage_required": True,
        "requests_per_minute": 60,
        "monthly_credit_limit": 0,
        "usage_rpc_timeout_seconds": 1.0,
    }
    values.update(overrides)
    return RuntimeSettings(**values)  # type: ignore[arg-type]


class _Response:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def _set_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JYOTHISYAM_SUPABASE_URL", ASTRO_URL)
    monkeypatch.setenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", SERVICE_KEY)


def test_memory_backend_requires_no_network() -> None:
    status = asyncio.run(
        inspect_usage_connectivity(
            _settings(
                environment="test",
                usage_backend="memory",
                usage_required=False,
                docs_enabled=True,
            )
        )
    )

    assert status.ready is True
    assert status.reachable is None
    assert status.project_ref is None
    assert status.issue is None


def test_unconfigured_supabase_backend_is_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JYOTHISYAM_SUPABASE_URL", raising=False)
    monkeypatch.delenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", raising=False)

    status = asyncio.run(inspect_usage_connectivity(_settings()))

    assert status.ready is False
    assert status.reachable is False
    assert status.issue == "configuration_not_ready"


def test_exact_astro_health_response_is_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_credentials(monkeypatch)
    body = (
        b'{"ready":true,"project_ref":"hdaugtypjpniesdgyral",'
        b'"schema_version":"api_usage_metering_safety_v1"}'
    )
    monkeypatch.setattr(
        "app.core.usage_readiness.urlopen",
        lambda request, timeout: _Response(body),
    )

    status = asyncio.run(inspect_usage_connectivity(_settings()))

    assert status.ready is True
    assert status.reachable is True
    assert status.project_ref == "hdaugtypjpniesdgyral"
    assert status.schema_version == "api_usage_metering_safety_v1"
    assert status.latency_ms is not None
    assert status.issue is None


def test_wrong_project_response_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_credentials(monkeypatch)
    body = (
        b'{"ready":true,"project_ref":"wrong-project",'
        b'"schema_version":"api_usage_metering_safety_v1"}'
    )
    monkeypatch.setattr(
        "app.core.usage_readiness.urlopen",
        lambda request, timeout: _Response(body),
    )

    status = asyncio.run(inspect_usage_connectivity(_settings()))

    assert status.ready is False
    assert status.reachable is True
    assert status.issue == "project_mismatch"


def test_unreachable_backend_is_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_credentials(monkeypatch)

    def _raise(*args: object, **kwargs: object) -> None:
        raise URLError("offline")

    monkeypatch.setattr("app.core.usage_readiness.urlopen", _raise)

    status = asyncio.run(inspect_usage_connectivity(_settings()))

    assert status.ready is False
    assert status.reachable is False
    assert status.issue == "backend_unreachable"
