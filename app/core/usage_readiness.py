"""Non-mutating connectivity readiness for the Astro usage backend."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from os import getenv
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from app.core.config import RuntimeSettings
from app.core.supabase_server_auth import supabase_server_headers
from app.core.usage_hardening import (
    ASTRO_SUPABASE_PROJECT_REF,
    inspect_usage_policy,
)

_EXPECTED_SCHEMA_VERSION = "api_usage_metering_safety_v1"


@dataclass(frozen=True)
class UsageConnectivityStatus:
    """Non-secret result of probing the durable usage backend."""

    ready: bool
    reachable: bool | None
    project_ref: str | None
    schema_version: str | None
    latency_ms: float | None
    issue: str | None


def _credentials() -> tuple[str, str]:
    return (
        getenv("JYOTHISYAM_SUPABASE_URL", "").strip(),
        getenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", "").strip(),
    )


def _decode_payload(raw: bytes) -> dict[str, Any] | None:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if isinstance(payload, list) and len(payload) == 1:
        payload = payload[0]
    return payload if isinstance(payload, dict) else None


def _probe_sync(
    base_url: str,
    server_credential: str,
    timeout_seconds: float,
) -> tuple[dict[str, Any] | None, float, str | None]:
    started = perf_counter()
    request = UrlRequest(
        f"{base_url.rstrip('/')}/rest/v1/rpc/api_usage_health_v1",
        data=b"{}",
        method="POST",
        headers=supabase_server_headers(server_credential),
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read()
    except HTTPError:
        return None, round((perf_counter() - started) * 1000, 3), "backend_http_error"
    except (URLError, TimeoutError):
        return None, round((perf_counter() - started) * 1000, 3), "backend_unreachable"
    payload = _decode_payload(raw)
    if payload is None:
        return None, round((perf_counter() - started) * 1000, 3), "invalid_backend_response"
    return payload, round((perf_counter() - started) * 1000, 3), None


async def inspect_usage_connectivity(settings: RuntimeSettings) -> UsageConnectivityStatus:
    """Probe the service-only health RPC without creating usage records."""

    policy = inspect_usage_policy(settings)
    if not policy.ready:
        return UsageConnectivityStatus(
            ready=False,
            reachable=False if settings.usage_backend == "supabase" else None,
            project_ref=None,
            schema_version=None,
            latency_ms=None,
            issue="configuration_not_ready",
        )
    if settings.usage_backend != "supabase":
        return UsageConnectivityStatus(
            ready=True,
            reachable=None,
            project_ref=None,
            schema_version=None,
            latency_ms=None,
            issue=None,
        )

    base_url, server_credential = _credentials()
    payload, latency_ms, issue = await asyncio.to_thread(
        _probe_sync,
        base_url,
        server_credential,
        settings.usage_rpc_timeout_seconds,
    )
    if payload is None:
        return UsageConnectivityStatus(
            ready=False,
            reachable=False,
            project_ref=None,
            schema_version=None,
            latency_ms=latency_ms,
            issue=issue,
        )

    project_ref = payload.get("project_ref")
    schema_version = payload.get("schema_version")
    backend_ready = payload.get("ready") is True
    if project_ref != ASTRO_SUPABASE_PROJECT_REF:
        issue = "project_mismatch"
    elif schema_version != _EXPECTED_SCHEMA_VERSION:
        issue = "schema_version_mismatch"
    elif not backend_ready:
        issue = "schema_not_ready"
    else:
        issue = None

    return UsageConnectivityStatus(
        ready=issue is None,
        reachable=True,
        project_ref=project_ref if isinstance(project_ref, str) else None,
        schema_version=schema_version if isinstance(schema_version, str) else None,
        latency_ms=latency_ms,
        issue=issue,
    )


__all__ = ["UsageConnectivityStatus", "inspect_usage_connectivity"]
