"""Centralized non-secret runtime configuration for the API service."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from os import getenv

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_VALID_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})
_DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "testserver")


@dataclass(frozen=True)
class RuntimeSettings:
    """Validated runtime policy used when constructing the FastAPI application."""

    environment: str
    log_level: str
    allowed_hosts: tuple[str, ...]
    cors_origins: tuple[str, ...]
    max_request_body_bytes: int
    request_timeout_seconds: float
    docs_enabled: bool

    @property
    def production(self) -> bool:
        """Return whether production-only fail-closed behavior applies."""

        return self.environment == "production"


def _is_true(value: str | None) -> bool:
    return value is not None and value.strip().lower() in _TRUE_VALUES


def _csv(value: str | None, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if value is None:
        return default
    items = tuple(dict.fromkeys(item.strip() for item in value.split(",") if item.strip()))
    return items


def _positive_int(name: str, default: int) -> int:
    raw = getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _positive_float(name: str, default: float) -> float:
    raw = getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be a number") from error
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _validate_hosts(hosts: tuple[str, ...]) -> tuple[str, ...]:
    if not hosts:
        raise ValueError("JYOTHISYAM_ALLOWED_HOSTS must contain at least one host")
    if "*" in hosts:
        raise ValueError("JYOTHISYAM_ALLOWED_HOSTS must not contain a wildcard")
    return hosts


def _validate_origins(origins: tuple[str, ...]) -> tuple[str, ...]:
    if "*" in origins:
        raise ValueError("JYOTHISYAM_CORS_ORIGINS must use an exact origin allowlist")
    invalid = [origin for origin in origins if not origin.startswith(("https://", "http://"))]
    if invalid:
        raise ValueError("JYOTHISYAM_CORS_ORIGINS entries must start with http:// or https://")
    return origins


@lru_cache(maxsize=1)
def load_runtime_settings() -> RuntimeSettings:
    """Load and validate process-level runtime settings exactly once."""

    environment = getenv("APP_ENV", "development").strip().lower()
    if environment not in {"development", "test", "staging", "production"}:
        raise ValueError("APP_ENV must be development, test, staging, or production")

    log_level = getenv("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in _VALID_LOG_LEVELS:
        raise ValueError("LOG_LEVEL must be CRITICAL, ERROR, WARNING, INFO, or DEBUG")

    allowed_hosts = _validate_hosts(
        _csv(getenv("JYOTHISYAM_ALLOWED_HOSTS"), _DEFAULT_ALLOWED_HOSTS)
    )
    cors_origins = _validate_origins(_csv(getenv("JYOTHISYAM_CORS_ORIGINS")))
    max_request_body_bytes = _positive_int("JYOTHISYAM_MAX_REQUEST_BODY_BYTES", 1_048_576)
    request_timeout_seconds = _positive_float("JYOTHISYAM_REQUEST_TIMEOUT_SECONDS", 30.0)

    docs_override = getenv("JYOTHISYAM_ENABLE_DOCS")
    docs_enabled = environment != "production"
    if docs_override is not None:
        docs_enabled = _is_true(docs_override)
    if environment == "production" and docs_enabled:
        raise ValueError("JYOTHISYAM_ENABLE_DOCS must remain disabled in production")

    return RuntimeSettings(
        environment=environment,
        log_level=log_level,
        allowed_hosts=allowed_hosts,
        cors_origins=cors_origins,
        max_request_body_bytes=max_request_body_bytes,
        request_timeout_seconds=request_timeout_seconds,
        docs_enabled=docs_enabled,
    )
