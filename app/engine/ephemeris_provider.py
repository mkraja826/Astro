"""Provider contract for versioned astronomical position engines."""

from __future__ import annotations

from typing import Protocol

from app.schemas.positions import PositionsRequest, PositionsResponse


class PositionProvider(Protocol):
    """Calculates one complete sidereal positions response for a profile."""

    provider_id: str

    def calculate(self, request: PositionsRequest) -> PositionsResponse:
        """Calculate positions for the provider's immutable profile."""
        ...
