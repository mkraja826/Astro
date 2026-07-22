"""Astro-project safety boundary for durable usage metering."""

from __future__ import annotations

from os import getenv
from typing import Annotated
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import Depends, Header, Request

from app.core.astro_supabase_usage import AstroSupabaseUsageBackend
from app.core.config import RuntimeSettings
from app.core.runtime_guard import request_id_from_scope
from app.core.security import require_api_key
from app.core.usage import (
    DisabledUsageBackend,
    MemoryUsageBackend,
    UsageAdmission,
    UsageBackend,
    UsageBackendError,
    UsageFinalizeMiddleware,
    UsagePolicyError,
    UsagePolicyStatus,
)

ASTRO_SUPABASE_PROJECT_REF = "hdaugtypjpniesdgyral"
_CONSUMER_HEADER = "X-Astro-Consumer-ID"
_LOCAL_CONSUMER_ID = "00000000-0000-0000-0000-000000000000"


def _supabase_credentials() -> tuple[str, str]:
    """Load only Jyothisyam-specific secrets, never generic project credentials."""

    base_url = getenv("JYOTHISYAM_SUPABASE_URL", "").strip()
    server_credential = getenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return base_url, server_credential


def _is_astro_project_url(base_url: str) -> bool:
    """Require the exact hosted Astro Supabase project URL."""

    try:
        parsed = urlsplit(base_url.rstrip("/"))
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname == f"{ASTRO_SUPABASE_PROJECT_REF}.supabase.co"
        and port is None
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
        and parsed.username is None
        and parsed.password is None
    )


def inspect_usage_policy(settings: RuntimeSettings) -> UsagePolicyStatus:
    """Report whether metering is safe and bound to the Astro project."""

    base_url, server_credential = _supabase_credentials()
    if settings.usage_backend == "disabled":
        configured = True
        durable = False
        ready = not settings.usage_required
    elif settings.usage_backend == "memory":
        configured = True
        durable = False
        ready = not settings.usage_required or settings.environment in {"development", "test"}
    else:
        configured = _is_astro_project_url(base_url) and len(server_credential) >= 32
        durable = True
        ready = configured
    return UsagePolicyStatus(
        status="ready" if ready else "degraded",
        ready=ready,
        backend=settings.usage_backend,
        required=settings.usage_required,
        durable=durable,
        configured=configured,
        requests_per_minute=settings.requests_per_minute,
        monthly_credit_limit=settings.monthly_credit_limit,
    )


def build_usage_backend(settings: RuntimeSettings) -> UsageBackend:
    """Construct the configured backend without generic Supabase fallbacks."""

    if settings.usage_backend == "disabled":
        return DisabledUsageBackend()
    if settings.usage_backend == "memory":
        return MemoryUsageBackend()
    base_url, server_credential = _supabase_credentials()
    return AstroSupabaseUsageBackend(
        base_url=base_url,
        server_credential=server_credential,
        timeout_seconds=settings.usage_rpc_timeout_seconds,
    )


def _consumer_id(value: str | None, settings: RuntimeSettings) -> str:
    if value is None or not value.strip():
        if settings.environment in {"development", "test"}:
            return _LOCAL_CONSUMER_ID
        raise UsagePolicyError(
            400,
            "CONSUMER_ID_REQUIRED",
            f"The {_CONSUMER_HEADER} header is required for calculation routes.",
        )
    try:
        return str(UUID(value.strip()))
    except ValueError as error:
        raise UsagePolicyError(
            400,
            "CONSUMER_ID_INVALID",
            f"The {_CONSUMER_HEADER} header must contain a valid UUID.",
        ) from error


def _rejection_error(admission: UsageAdmission) -> UsagePolicyError:
    code = admission.reason or "RATE_LIMIT_EXCEEDED"
    headers = {
        "X-RateLimit-Limit": str(admission.limit),
        "X-RateLimit-Remaining": str(admission.remaining),
    }
    if code == "REQUEST_ID_REUSED":
        return UsagePolicyError(
            409,
            code,
            "The request ID has already been used. Send a new X-Request-ID.",
            headers=headers,
        )
    headers["Retry-After"] = str(admission.retry_after_seconds)
    message = (
        "The monthly calculation quota has been reached."
        if code == "MONTHLY_QUOTA_EXCEEDED"
        else "The calculation request rate limit has been exceeded."
    )
    return UsagePolicyError(429, code, message, headers=headers)


async def require_metered_access(
    request: Request,
    _: Annotated[None, Depends(require_api_key)],
    consumer_header: Annotated[str | None, Header(alias=_CONSUMER_HEADER)] = None,
) -> None:
    """Authenticate, identify the consumer, and atomically admit the request."""

    settings: RuntimeSettings = request.app.state.runtime_settings
    status = inspect_usage_policy(settings)
    if not status.ready:
        raise UsagePolicyError(
            503,
            "USAGE_BACKEND_NOT_READY",
            "Rate limiting and usage metering are not ready.",
        )
    consumer_id = _consumer_id(consumer_header, settings)
    route = request.scope.get("route")
    route_key = getattr(route, "path", request.url.path)
    request_id = request_id_from_scope(request.scope)
    backend: UsageBackend = request.app.state.usage_backend
    try:
        admission = await backend.admit(
            request_id=request_id,
            consumer_id=consumer_id,
            route_key=route_key,
            credit_cost=1,
            requests_per_minute=settings.requests_per_minute,
            monthly_credit_limit=settings.monthly_credit_limit,
        )
    except UsageBackendError as error:
        raise UsagePolicyError(
            503,
            "USAGE_BACKEND_UNAVAILABLE",
            "Rate limiting and usage metering are temporarily unavailable.",
        ) from error
    if not admission.allowed:
        raise _rejection_error(admission)
    request.scope.setdefault("state", {})["usage_admission"] = admission


__all__ = [
    "ASTRO_SUPABASE_PROJECT_REF",
    "UsageFinalizeMiddleware",
    "build_usage_backend",
    "inspect_usage_policy",
    "require_metered_access",
]
