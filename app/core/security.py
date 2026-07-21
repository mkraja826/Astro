"""Service-to-service bearer authentication for calculation routes."""

from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from os import getenv

API_KEY_MIN_LENGTH = 32
PROTECTED_PREFIX = "/v1"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


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


@dataclass(frozen=True)
class ApiSecurityRejection:
    """HTTP-safe rejection returned before a protected route is evaluated."""

    status_code: int
    code: str
    message: str


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


def authorize_api_request(
    path: str,
    method: str,
    authorization: str | None,
) -> ApiSecurityRejection | None:
    """Authorize one request, protecting every current and future ``/v1`` route."""

    if method.upper() == "OPTIONS":
        return None
    if path != PROTECTED_PREFIX and not path.startswith(f"{PROTECTED_PREFIX}/"):
        return None

    status = inspect_api_security()
    if not status.protection_enabled:
        return None
    if not status.ready:
        return ApiSecurityRejection(
            status_code=503,
            code="API_AUTH_NOT_CONFIGURED",
            message=(
                "Calculation API authentication is required but no valid service key is configured."
            ),
        )

    scheme, separator, supplied = (authorization or "").partition(" ")
    if not separator or scheme.lower() != "bearer" or not supplied.strip():
        return ApiSecurityRejection(
            status_code=401,
            code="API_KEY_REQUIRED",
            message="A bearer API key is required for calculation routes.",
        )

    if not compare_digest(supplied.strip(), _configured_key()):
        return ApiSecurityRejection(
            status_code=403,
            code="API_KEY_INVALID",
            message="The supplied API key is not valid.",
        )
    return None
