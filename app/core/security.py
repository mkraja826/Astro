"""Service-to-service bearer authentication for calculation routes."""

from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from os import getenv
from typing import Annotated

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

API_KEY_MIN_LENGTH = 32
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="AstroServiceKey",
    description="Opaque service key used by the Horos Supabase Edge Function.",
)


@dataclass(frozen=True)
class ApiSecurityStatus:
    """Non-secret security readiness information for deployment probes."""

    status: str
    ready: bool
    protection_enabled: bool
    required: bool
    configured: bool
    valid_length: bool
    scheme: str = "bearer"
    minimum_key_length: int = API_KEY_MIN_LENGTH


class ApiSecurityError(Exception):
    """Stable authentication failure translated to a JSON API response."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def _is_true(value: str | None) -> bool:
    return value is not None and value.strip().lower() in _TRUE_VALUES


def _configured_key() -> str:
    return getenv("JYOTHISYAM_API_KEY", "").strip()


def inspect_api_security() -> ApiSecurityStatus:
    """Report whether the calculation-route authentication policy is ready."""

    required = _is_true(getenv("JYOTHISYAM_REQUIRE_API_KEY"))
    key = _configured_key()
    configured = bool(key)
    valid_length = len(key) >= API_KEY_MIN_LENGTH
    protection_enabled = required or configured
    ready = not protection_enabled or (configured and valid_length)
    return ApiSecurityStatus(
        status="ready" if ready else "degraded",
        ready=ready,
        protection_enabled=protection_enabled,
        required=required,
        configured=configured,
        valid_length=valid_length,
    )


def require_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
) -> None:
    """Require the configured bearer key when calculation protection is enabled."""

    status = inspect_api_security()
    if not status.protection_enabled:
        return
    if not status.ready:
        raise ApiSecurityError(
            status_code=503,
            code="API_AUTH_NOT_CONFIGURED",
            message=(
                "Calculation API authentication is required but no valid service key is configured."
            ),
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiSecurityError(
            status_code=401,
            code="API_KEY_REQUIRED",
            message="A bearer API key is required for calculation routes.",
        )
    if not compare_digest(credentials.credentials.strip(), _configured_key()):
        raise ApiSecurityError(
            status_code=403,
            code="API_KEY_INVALID",
            message="The supplied API key is not valid.",
        )
