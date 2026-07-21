"""Focused tests for host, CORS, request identity, size, timeout, and safe failures."""

import asyncio

from fastapi import Request
from fastapi.testclient import TestClient

from app.core.config import RuntimeSettings
from app.main import create_app


def _settings(**overrides: object) -> RuntimeSettings:
    values: dict[str, object] = {
        "environment": "test",
        "log_level": "INFO",
        "allowed_hosts": ("testserver",),
        "cors_origins": (),
        "max_request_body_bytes": 1024,
        "request_timeout_seconds": 1.0,
        "docs_enabled": True,
    }
    values.update(overrides)
    return RuntimeSettings(**values)  # type: ignore[arg-type]


def test_request_id_is_preserved_and_returned() -> None:
    client = TestClient(create_app(_settings()))

    response = client.get("/health", headers={"X-Request-ID": "runtime-test-001"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "runtime-test-001"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_invalid_request_id_is_replaced() -> None:
    client = TestClient(create_app(_settings()))

    response = client.get("/health", headers={"X-Request-ID": "invalid request id"})

    assert response.status_code == 200
    generated = response.headers["x-request-id"]
    assert len(generated) == 32
    assert generated != "invalid request id"


def test_untrusted_host_is_rejected() -> None:
    client = TestClient(create_app(_settings(allowed_hosts=("api.example.com",))))

    response = client.get("/health")

    assert response.status_code == 400
    assert response.headers["x-request-id"]


def test_exact_cors_origin_is_allowed() -> None:
    client = TestClient(
        create_app(_settings(cors_origins=("https://horos.example",)))
    )

    response = client.get(
        "/health",
        headers={"Origin": "https://horos.example"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://horos.example"
    assert "x-request-id" in response.headers["access-control-expose-headers"].lower()


def test_request_body_limit_rejects_oversized_payload() -> None:
    application = create_app(_settings(max_request_body_bytes=8))

    async def echo(request: Request) -> dict[str, int]:
        return {"size": len(await request.body())}

    application.add_api_route("/test/echo", echo, methods=["POST"])
    client = TestClient(application)

    response = client.post("/test/echo", content=b"123456789")

    assert response.status_code == 413
    assert response.json()["code"] == "REQUEST_BODY_TOO_LARGE"
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_request_timeout_returns_stable_504() -> None:
    application = create_app(_settings(request_timeout_seconds=0.01))

    async def slow() -> dict[str, bool]:
        await asyncio.sleep(0.05)
        return {"completed": True}

    application.add_api_route("/test/slow", slow, methods=["GET"])
    client = TestClient(application)

    response = client.get("/test/slow")

    assert response.status_code == 504
    assert response.json()["code"] == "REQUEST_TIMEOUT"
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_unexpected_exception_returns_generic_response() -> None:
    application = create_app(_settings())

    async def explode() -> None:
        raise RuntimeError("sensitive birth details must never reach the client")

    application.add_api_route("/test/explode", explode, methods=["GET"])
    client = TestClient(application, raise_server_exceptions=False)

    response = client.get("/test/explode")

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_SERVER_ERROR"
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert "sensitive birth details" not in response.text


def test_production_disables_interactive_documentation() -> None:
    application = create_app(
        _settings(environment="production", docs_enabled=False)
    )
    client = TestClient(application)

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/").json()["documentation"] == "disabled"


def test_runtime_health_reports_non_secret_limits() -> None:
    client = TestClient(
        create_app(
            _settings(
                cors_origins=("https://horos.example",),
                max_request_body_bytes=2048,
                request_timeout_seconds=12.5,
            )
        )
    )

    response = client.get("/health/runtime")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "ready": True,
        "environment": "test",
        "docs_enabled": True,
        "allowed_host_count": 1,
        "cors_origin_count": 1,
        "max_request_body_bytes": 2048,
        "request_timeout_seconds": 12.5,
    }
