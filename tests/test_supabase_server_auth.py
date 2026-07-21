"""Tests for legacy and opaque Supabase server credential handling."""

from __future__ import annotations

import json
from typing import Any

from app.core.astro_supabase_usage import AstroSupabaseUsageBackend
from app.core.supabase_server_auth import supabase_server_headers
from app.core.usage_readiness import _probe_sync

SECRET_KEY = "sb_secret_jyothisyam_staging_0123456789abcdef"
LEGACY_KEY = "eyJheader.eyJservice-role-payload.signature"


class _Response:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_secret_key_is_never_sent_as_bearer() -> None:
    headers = supabase_server_headers(SECRET_KEY)

    assert headers["apikey"] == SECRET_KEY
    assert "Authorization" not in headers


def test_legacy_service_role_key_keeps_bearer_header() -> None:
    headers = supabase_server_headers(LEGACY_KEY)

    assert headers["apikey"] == LEGACY_KEY
    assert headers["Authorization"] == f"Bearer {LEGACY_KEY}"


def test_usage_backend_uses_secret_key_header_policy(monkeypatch: Any) -> None:
    captured_headers: dict[str, str] = {}

    def _urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        captured_headers.update(dict(request.header_items()))
        return _Response({"allowed": True, "limit": 60, "remaining": 59})

    monkeypatch.setattr("app.core.astro_supabase_usage.urlopen", _urlopen)
    backend = AstroSupabaseUsageBackend(
        base_url="https://hdaugtypjpniesdgyral.supabase.co",
        server_credential=SECRET_KEY,
        timeout_seconds=1.0,
    )

    payload = backend._rpc_sync("api_usage_admit_v1", {})

    assert payload["allowed"] is True
    assert captured_headers["Apikey"] == SECRET_KEY
    assert "Authorization" not in captured_headers


def test_readiness_probe_uses_secret_key_header_policy(monkeypatch: Any) -> None:
    captured_headers: dict[str, str] = {}

    def _urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        captured_headers.update(dict(request.header_items()))
        return _Response(
            {
                "ready": True,
                "project_ref": "hdaugtypjpniesdgyral",
                "schema_version": "api_usage_metering_safety_v1",
            }
        )

    monkeypatch.setattr("app.core.usage_readiness.urlopen", _urlopen)

    payload, _, issue = _probe_sync(
        "https://hdaugtypjpniesdgyral.supabase.co",
        SECRET_KEY,
        1.0,
    )

    assert issue is None
    assert payload is not None and payload["ready"] is True
    assert captured_headers["Apikey"] == SECRET_KEY
    assert "Authorization" not in captured_headers
