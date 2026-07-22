"""Supabase server credential header policy."""

from __future__ import annotations


def supabase_server_headers(server_credential: str) -> dict[str, str]:
    """Return Data API headers for legacy JWTs or opaque secret credentials."""

    credential = server_credential.strip()
    headers = {
        "apikey": credential,
        "Content-Type": "application/json",
    }
    if not credential.startswith("sb_secret_"):
        headers["Authorization"] = f"Bearer {credential}"
    return headers


__all__ = ["supabase_server_headers"]
