"""ASGI runtime guards for request identity, limits, timeouts, and safe access logs."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from time import perf_counter
from typing import Any
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")
_ACCESS_LOGGER = logging.getLogger("jyothisyam.access")


class RequestBodyTooLargeError(Exception):
    """Raised internally when a streamed request exceeds the configured byte limit."""


class InvalidContentLengthError(Exception):
    """Raised internally when Content-Length is malformed."""


def request_id_from_scope(scope: Scope) -> str:
    """Return the request identifier stored by the runtime middleware."""

    state = scope.get("state") or {}
    value = state.get("request_id")
    return value if isinstance(value, str) and value else uuid4().hex


def _choose_request_id(headers: Headers) -> str:
    supplied = headers.get("x-request-id", "").strip()
    if supplied and _REQUEST_ID_PATTERN.fullmatch(supplied):
        return supplied
    return uuid4().hex


def _error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "request_id": request_id},
    )


class RuntimeGuardMiddleware:
    """Apply fail-closed request limits without logging bodies or query strings."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        max_request_body_bytes: int,
        request_timeout_seconds: float,
    ) -> None:
        self.app = app
        self.max_request_body_bytes = max_request_body_bytes
        self.request_timeout_seconds = request_timeout_seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = perf_counter()
        headers = Headers(scope=scope)
        request_id = _choose_request_id(headers)
        scope.setdefault("state", {})["request_id"] = request_id
        response_started = False
        status_code = 500
        received_bytes = 0

        async def send_with_runtime_headers(message: Message) -> None:
            nonlocal response_started, status_code
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                response_headers = MutableHeaders(scope=message)
                response_headers["x-request-id"] = request_id
                response_headers["x-content-type-options"] = "nosniff"
            await send(message)

        async def limited_receive() -> Message:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_request_body_bytes:
                    raise RequestBodyTooLargeError
            return message

        try:
            raw_content_length = headers.get("content-length")
            if raw_content_length:
                try:
                    content_length = int(raw_content_length)
                except ValueError as error:
                    raise InvalidContentLengthError from error
                if content_length < 0:
                    raise InvalidContentLengthError
                if content_length > self.max_request_body_bytes:
                    raise RequestBodyTooLargeError

            await asyncio.wait_for(
                self.app(scope, limited_receive, send_with_runtime_headers),
                timeout=self.request_timeout_seconds,
            )
        except InvalidContentLengthError:
            if response_started:
                raise
            await _error_response(
                400,
                "INVALID_CONTENT_LENGTH",
                "The Content-Length header is not valid.",
                request_id,
            )(scope, receive, send_with_runtime_headers)
        except RequestBodyTooLargeError:
            if response_started:
                raise
            await _error_response(
                413,
                "REQUEST_BODY_TOO_LARGE",
                "The request body exceeds the configured maximum size.",
                request_id,
            )(scope, receive, send_with_runtime_headers)
        except TimeoutError:
            if response_started:
                raise
            await _error_response(
                504,
                "REQUEST_TIMEOUT",
                "The request exceeded the configured processing timeout.",
                request_id,
            )(scope, receive, send_with_runtime_headers)
        finally:
            duration_ms = round((perf_counter() - started_at) * 1000, 3)
            event: dict[str, Any] = {
                "event": "http_request",
                "request_id": request_id,
                "method": scope.get("method"),
                "path": scope.get("path"),
                "status_code": status_code,
                "duration_ms": duration_ms,
                "request_body_bytes": received_bytes,
            }
            _ACCESS_LOGGER.info(json.dumps(event, separators=(",", ":"), sort_keys=True))
