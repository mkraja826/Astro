"""Tests for centralized non-secret runtime configuration."""

import pytest

from app.core.config import load_runtime_settings

_RUNTIME_ENV_NAMES = (
    "APP_ENV",
    "LOG_LEVEL",
    "JYOTHISYAM_ALLOWED_HOSTS",
    "JYOTHISYAM_CORS_ORIGINS",
    "JYOTHISYAM_MAX_REQUEST_BODY_BYTES",
    "JYOTHISYAM_REQUEST_TIMEOUT_SECONDS",
    "JYOTHISYAM_ENABLE_DOCS",
)


def _clear_runtime_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _RUNTIME_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    load_runtime_settings.cache_clear()


def test_development_defaults_are_safe_for_local_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_runtime_env(monkeypatch)

    settings = load_runtime_settings()

    assert settings.environment == "development"
    assert settings.docs_enabled is True
    assert settings.allowed_hosts == ("localhost", "127.0.0.1", "testserver")
    assert settings.cors_origins == ()
    assert settings.max_request_body_bytes == 1_048_576
    assert settings.request_timeout_seconds == 30.0


def test_production_disables_docs_and_parses_exact_allowlists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JYOTHISYAM_ALLOWED_HOSTS", "api.example.com,api.internal")
    monkeypatch.setenv("JYOTHISYAM_CORS_ORIGINS", "https://horos.example")
    monkeypatch.setenv("JYOTHISYAM_ENABLE_DOCS", "false")

    settings = load_runtime_settings()

    assert settings.production is True
    assert settings.docs_enabled is False
    assert settings.allowed_hosts == ("api.example.com", "api.internal")
    assert settings.cors_origins == ("https://horos.example",)


def test_wildcard_host_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_ALLOWED_HOSTS", "*")

    with pytest.raises(ValueError, match="must not contain a wildcard"):
        load_runtime_settings()


def test_wildcard_cors_origin_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv("JYOTHISYAM_CORS_ORIGINS", "*")

    with pytest.raises(ValueError, match="exact origin allowlist"):
        load_runtime_settings()


def test_production_cannot_enable_interactive_docs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JYOTHISYAM_ENABLE_DOCS", "true")

    with pytest.raises(ValueError, match="must remain disabled in production"):
        load_runtime_settings()
