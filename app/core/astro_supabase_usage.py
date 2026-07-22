"""Durable Astro usage backend for Supabase Data API RPCs."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from app.core.supabase_server_auth import supabase_server_headers
from app.core.usage import UsageAdmission, UsageBackendError


class AstroSupabaseUsageBackend:
    """Call Astro's service-only usage metering RPCs."""

    def __init__(self, *, base_url: str, server_credential: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.server_credential = server_credential.strip()
        self.timeout_seconds = timeout_seconds

    def _rpc_sync(self, function_name: str, payload: dict[str, Any]) -> Any:
        request = UrlRequest(
            f"{self.base_url}/rest/v1/rpc/{function_name}",
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers=supabase_server_headers(self.server_credential),
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


__all__ = ["AstroSupabaseUsageBackend"]
