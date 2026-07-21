#!/usr/bin/env python3
"""Run non-secret staging readiness and authenticated API smoke checks."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

ASTRO_PROJECT_REF = "hdaugtypjpniesdgyral"
PROFILE_PATH = "/v1/classical/varahamihira_v1/profile"


@dataclass(frozen=True)
class Result:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict[str, object]:
        payload = json.loads(self.body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise RuntimeError("Expected a JSON object")
        return payload


def _request(base_url: str, path: str, headers: dict[str, str] | None = None) -> Result:
    request = Request(urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/")), headers=headers or {})
    try:
        with urlopen(request, timeout=15) as response:
            return Result(
                status=response.status,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=response.read(),
            )
    except HTTPError as error:
        return Result(
            status=error.code,
            headers={key.lower(): value for key, value in error.headers.items()},
            body=error.read(),
        )
    except URLError as error:
        raise RuntimeError("The staging service is unreachable") from error


def _expect_status(result: Result, expected: int, label: str) -> None:
    if result.status != expected:
        raise RuntimeError(f"{label}: expected HTTP {expected}, got {result.status}")


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("ASTRO_STAGING_BASE_URL", "").strip(),
        help="HTTPS base URL of the staging API",
    )
    parser.add_argument(
        "--allow-http",
        action="store_true",
        help="Permit HTTP for local testing only",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    if not base_url:
        raise RuntimeError("Provide --base-url or ASTRO_STAGING_BASE_URL")
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" and not args.allow_http:
        raise RuntimeError("Staging smoke tests require HTTPS")
    if not parsed.hostname:
        raise RuntimeError("The staging base URL is invalid")

    api_key = _required_env("ASTRO_STAGING_API_KEY")
    consumer_id = str(UUID(_required_env("ASTRO_STAGING_CONSUMER_ID")))

    health = _request(base_url, "/health")
    _expect_status(health, 200, "liveness")

    readiness = _request(base_url, "/health/ready")
    _expect_status(readiness, 200, "readiness")
    readiness_payload = readiness.json()
    usage = readiness_payload.get("usage")
    if readiness_payload.get("ready") is not True or not isinstance(usage, dict):
        raise RuntimeError("The service did not report complete readiness")
    if usage.get("reachable") is not True:
        raise RuntimeError("The Astro usage backend is not reachable")
    if usage.get("project_ref") != ASTRO_PROJECT_REF:
        raise RuntimeError("The staging service is not bound to the Astro Supabase project")

    _expect_status(_request(base_url, "/docs"), 404, "production docs")
    _expect_status(_request(base_url, PROFILE_PATH), 401, "unauthenticated request")

    auth_header = {"Authorization": f"Bearer {api_key}"}
    missing_consumer = _request(base_url, PROFILE_PATH, auth_header)
    _expect_status(missing_consumer, 400, "missing consumer")
    if missing_consumer.json().get("code") != "CONSUMER_ID_REQUIRED":
        raise RuntimeError("Missing-consumer response did not use the stable error code")

    request_id = f"staging-smoke-{uuid4().hex}"
    headers = {
        **auth_header,
        "X-Astro-Consumer-ID": consumer_id,
        "X-Request-ID": request_id,
    }
    admitted = _request(base_url, PROFILE_PATH, headers)
    _expect_status(admitted, 200, "authenticated metered request")
    if admitted.headers.get("x-astro-credit-cost") != "1":
        raise RuntimeError("The response did not include the unit credit header")
    if not admitted.headers.get("x-ratelimit-limit"):
        raise RuntimeError("The response did not include rate-limit headers")

    duplicate = _request(base_url, PROFILE_PATH, headers)
    _expect_status(duplicate, 409, "duplicate request ID")
    if duplicate.json().get("code") != "REQUEST_ID_REUSED":
        raise RuntimeError("Duplicate request IDs are not protected by the stable error code")

    print("Staging smoke checks passed.")
    print(f"Service host: {parsed.hostname}")
    print(f"Request ID: {request_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
