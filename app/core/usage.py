"""Shared rate limiting and usage metering for authenticated calculation routes."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from os import getenv
from threading import Lock
from typing import Annotated, Any, Protocol
from urllib.error import URLError
from urllib.request import Request as UrlRequest, urlopen
from uuid import UUID

from fastapi import Depends, Header, Request
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import RuntimeSettings
from app.core.runtime_guard import request_id_from_scope
from app.core.security import require_api_key

_CONSUMER_HEADER = "X-Astro-Consumer-ID"
_LOCAL_CONSUMER_ID = "00000000-0000-0000-0000-000000000000"
_LOGGER = logging.getLogger("jyothisyam.usage")


@dataclass(frozen=True)
class UsagePolicyStatus:
    """Non-secret deployment readiness for rate limiting and metering."""

    status: str
    ready: bool
    backend: str
    required: bool
    durable: bool
    configured: bool
    requests_per_minute: int
    monthly_credit_limit: int
    consumer_header: str = _CONSUMER_HEADER


@dataclass(frozen=True)
class UsageAdmission:
    """Admission result attached to the request for response finalization."""

    allowed: bool
    request_id: str
    consumer_id: str
    route_key: str
    credit_cost: int
    limit: int
    remaining: int
    retry_after_seconds: int
    reason: str | None = None


class UsagePolicyError(Exception):
    """Stable rate-limit or metering failure translated by the API layer."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers or {}


class UsageBackendError(RuntimeError):
    """Raised when a durable metering backend cannot complete an operation."""


class UsageBackend(Protocol):
    """Backend contract for atomic admission and idempotent finalization."""

    async def admit(
        self,
        *,
        request_id: str,
        consumer_id: str,
        route_key: str,
        credit_cost: int,
        requests_per_minute: int,
        monthly_credit_limit: int,
    ) -> UsageAdmission: ...

    async def finalize(self, *, request_id: str, response_status: int) -> None: ...


class DisabledUsageBackend:
    """No-op backend used only when usage enforcement is explicitly disabled."""

    async def admit(
        self,
        *,
        request_id: str,
        consumer_id: str,
        route_key: str,
        credit_cost: int,
        requests_per_minute: int,
        monthly_credit_limit: int,
    ) -> UsageAdmission:
        del monthly_credit_limit
        return UsageAdmission(
            allowed=True,
            request_id=request_id,
            consumer_id=consumer_id,
            route_key=route_key,
            credit_cost=credit_cost,
            limit=requests_per_minute,
            remaining=requests_per_minute,
            retry_after_seconds=0,
        )

    async def finalize(self, *, request_id: str, response_status: int) -> None:
        del request_id, response_status


class MemoryUsageBackend:
    """Process-local backend for deterministic tests and local development only."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._windows: dict[tuple[str, int], int] = {}
        self._months: dict[tuple[str, str], dict[str, int]] = {}
        self._events: dict[str, dict[str, Any]] = {}

    async def admit(
        self,
        *,
        request_id: str,
        consumer_id: str,
        route_key: str,
        credit_cost: int,
        requests_per_minute: int,
        monthly_credit_limit: int,
    ) -> UsageAdmission:
        now = datetime.now(UTC)
        minute_epoch = int(now.timestamp()) // 60
        retry_after = 60 - (int(now.timestamp()) % 60)
        month_key = now.strftime("%Y-%m-01")
        with self._lock:
            existing = self._events.get(request_id)
            if existing is not None:
                return existing["admission"]

            stale_before = minute_epoch - 2
            self._windows = {
                key: count for key, count in self._windows.items() if key[1] >= stale_before
            }
            window_key = (consumer_id, minute_epoch)
            current_count = self._windows.get(window_key, 0)
            if current_count >= requests_per_minute:
                return UsageAdmission(
                    allowed=False,
                    request_id=request_id,
                    consumer_id=consumer_id,
                    route_key=route_key,
                    credit_cost=credit_cost,
                    limit=requests_per_minute,
                    remaining=0,
                    retry_after_seconds=retry_after,
                    reason="RATE_LIMIT_EXCEEDED",
                )

            month = self._months.setdefault(
                (consumer_id, month_key), {"used": 0, "reserved": 0}
            )
            if monthly_credit_limit > 0:
                projected = month["used"] + month["reserved"] + credit_cost
                if projected > monthly_credit_limit:
                    return UsageAdmission(
                        allowed=False,
                        request_id=request_id,
                        consumer_id=consumer_id,
                        route_key=route_key,
                        credit_cost=credit_cost,
                        limit=requests_per_minute,
                        remaining=max(requests_per_minute - current_count, 0),
                        retry_after_seconds=retry_after,
                        reason="MONTHLY_QUOTA_EXCEEDED",
                    )

            self._windows[window_key] = current_count + 1
            month["reserved"] += credit_cost
            admission = UsageAdmission(
                allowed=True,
                request_id=request_id,
                consumer_id=consumer_id,
                route_key=route_key,
                credit_cost=credit_cost,
                limit=requests_per_minute,
                remaining=max(requests_per_minute - current_count - 1, 0),
                retry_after_seconds=retry_after,
            )
            self._events[request_id] = {
                "admission": admission,
                "month_key": month_key,
                "finalized": False,
            }
            return admission

    async def finalize(self, *, request_id: str, response_status: int) -> None:
        with self._lock:
            event = self._events.get(request_id)
            if event is None or event["finalized"]:
                return
            admission: UsageAdmission = event["admission"]
            month = self._months[(admission.consumer_id, event["month_key"])]
            month["reserved"] = max(month["reserved"] - admission.credit_cost, 0)
            if 200 <= response_status < 400:
                month["used"] += admission.credit_cost
            event["response_status"] = response_status
            event["finalized"] = True


class SupabaseUsageBackend:
    """Durable backend using security-definer RPCs in the Astro Supabase project."""

    def __init__(self, *, base_url: str, service_role_key: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.service_role_key = service_role_key
        self.timeout_seconds = timeout_seconds

    def _rpc_sync(self, function_name: str, payload: dict[str, Any]) -> Any:
        request = UrlRequest(
            f"{self.base_url}/rest/v1/rpc/{function_name}",
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers={
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except (URLError, TimeoutError) as error:
            raise UsageBackendError("The usage backend request failed") from error
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise UsageBackendError("The usage backend returned an invalid response") from error
        if isinstance(decoded, list) and len(decoded) == 1:
            return decoded[0]
        return decoded

    async def admit(
        self,
        *,
        request_id: str,
        consumer_id: str,
        route_key: str,
        credit_cost: int,
        requests_per_minute: int,
        monthly_credit_limit: int,
    ) -> UsageAdmission:
        payload = await asyncio.to_thread(
            self._rpc_sync,
            "api_usage_admit_v1",
            {
                "p_request_id": request_id,
                "p_consumer_id": consumer_id,
                "p_route_key": route_key,
                "p_credit_cost": credit_cost,
                "p_requests_per_minute": requests_per_minute,
                "p_monthly_credit_limit": monthly_credit_limit,
            },
        )
        if not isinstance(payload, dict):
            raise UsageBackendError("The usage admission response was not an object")
        return UsageAdmission(
            allowed=bool(payload.get("allowed")),
            request_id=request_id,
            consumer_id=consumer_id,
            route_key=route_key,
            credit_cost=credit_cost,
            limit=int(payload.get("limit", requests_per_minute)),
            remaining=int(payload.get("remaining", 0)),
            retry_after_seconds=int(payload.get("retry_after_seconds", 60)),
            reason=payload.get("reason"),
        )

    async def finalize(self, *, request_id: str, response_status: int) -> None:
        await asyncio.to_thread(
            self._rpc_sync,
            "api_usage_finalize_v1",
            {"p_request_id": request_id, "p_response_status": response_status},
        )


def _supabase_credentials() -> tuple[str, str]:
    base_url = (
        getenv("JYOTHISYAM_SUPABASE_URL") or getenv("SUPABASE_URL") or ""
    ).strip()
    service_role_key = (
        getenv("JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY")
        or getenv("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    return base_url, service_role_key


def inspect_usage_policy(settings: RuntimeSettings) -> UsagePolicyStatus:
    """Report whether the configured usage backend is safe for this environment."""

    base_url, service_role_key = _supabase_credentials()
    if settings.usage_backend == "disabled":
        configured = True
        durable = False
        ready = not settings.usage_required
    elif settings.usage_backend == "memory":
        configured = True
        durable = False
        ready = not settings.usage_required or settings.environment in {"development", "test"}
    else:
        configured = base_url.startswith("https://") and len(service_role_key) >= 32
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
    """Construct the configured backend without making network calls at startup."""

    if settings.usage_backend == "disabled":
        return DisabledUsageBackend()
    if settings.usage_backend == "memory":
        return MemoryUsageBackend()
    base_url, service_role_key = _supabase_credentials()
    return SupabaseUsageBackend(
        base_url=base_url,
        service_role_key=service_role_key,
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


async def require_metered_access(
    request: Request,
    _: Annotated[None, Depends(require_api_key)],
    consumer_header: Annotated[str | None, Header(alias=_CONSUMER_HEADER)] = None,
) -> None:
    """Authenticate, identify the trusted consumer, and atomically admit the request."""

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
        code = admission.reason or "RATE_LIMIT_EXCEEDED"
        message = (
            "The monthly calculation quota has been reached."
            if code == "MONTHLY_QUOTA_EXCEEDED"
            else "The calculation request rate limit has been exceeded."
        )
        raise UsagePolicyError(
            429,
            code,
            message,
            headers={
                "Retry-After": str(admission.retry_after_seconds),
                "X-RateLimit-Limit": str(admission.limit),
                "X-RateLimit-Remaining": str(admission.remaining),
            },
        )
    request.scope.setdefault("state", {})["usage_admission"] = admission


class UsageFinalizeMiddleware:
    """Finalize billable usage after a route has produced its response status."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        finalized = False

        async def send_with_usage(message: Message) -> None:
            nonlocal finalized
            if message["type"] == "http.response.start":
                admission = (scope.get("state") or {}).get("usage_admission")
                if isinstance(admission, UsageAdmission):
                    response_headers = MutableHeaders(scope=message)
                    response_headers["x-ratelimit-limit"] = str(admission.limit)
                    response_headers["x-ratelimit-remaining"] = str(admission.remaining)
                    response_headers["x-astro-credit-cost"] = str(admission.credit_cost)
                    if not finalized:
                        backend: UsageBackend = scope["app"].state.usage_backend
                        try:
                            await backend.finalize(
                                request_id=admission.request_id,
                                response_status=int(message["status"]),
                            )
                        except UsageBackendError:
                            _LOGGER.error(
                                "Usage finalization failed request_id=%s path=%s",
                                admission.request_id,
                                scope.get("path"),
                            )
                        finalized = True
            await send(message)

        await self.app(scope, receive, send_with_usage)
