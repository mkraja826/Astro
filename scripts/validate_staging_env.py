#!/usr/bin/env python3
"""Validate staging configuration without printing secret values."""

from __future__ import annotations

from app.core.config import load_runtime_settings
from app.core.security import inspect_api_security
from app.core.usage_hardening import inspect_usage_policy

_LOCAL_HOSTS = {"localhost", "127.0.0.1", "testserver"}


def main() -> int:
    load_runtime_settings.cache_clear()
    settings = load_runtime_settings()
    security = inspect_api_security()
    usage = inspect_usage_policy(settings)
    errors: list[str] = []

    if settings.environment != "staging":
        errors.append("APP_ENV_NOT_STAGING")
    if settings.docs_enabled:
        errors.append("INTERACTIVE_DOCS_ENABLED")
    if not any(host not in _LOCAL_HOSTS for host in settings.allowed_hosts):
        errors.append("PUBLIC_ALLOWED_HOST_MISSING")
    if not security.required:
        errors.append("API_KEY_NOT_REQUIRED")
    if not security.ready:
        errors.append("API_KEY_NOT_READY")
    if settings.usage_backend != "supabase":
        errors.append("DURABLE_USAGE_BACKEND_NOT_SELECTED")
    if not settings.usage_required:
        errors.append("USAGE_GUARD_NOT_REQUIRED")
    if not usage.ready or not usage.durable or not usage.configured:
        errors.append("ASTRO_USAGE_BACKEND_NOT_READY")

    if errors:
        for code in errors:
            print(f"ERROR {code}")
        return 1

    print("Staging configuration is valid.")
    print(f"Allowed hosts: {len(settings.allowed_hosts)}")
    print(f"CORS origins: {len(settings.cors_origins)}")
    print(f"Requests per minute: {settings.requests_per_minute}")
    print(f"Monthly credit limit: {settings.monthly_credit_limit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
