"""Independent deterministic Jyotisha classifications for feasibility only."""

from __future__ import annotations

from decimal import ROUND_FLOOR, Decimal

type Number = Decimal | float | int | str
FULL_CIRCLE = Decimal(360)
SIGN_WIDTH = Decimal(30)
NAVAMSA_OR_PADA_WIDTH = Decimal(10) / Decimal(3)
NAKSHATRA_WIDTH = Decimal(40) / Decimal(3)


def normalized(longitude: Number) -> Decimal:
    """Normalize a longitude to the half-open interval [0, 360)."""

    value = Decimal(str(longitude)) % FULL_CIRCLE
    return value + FULL_CIRCLE if value < 0 else value


def floor_index(value: Decimal, width: Decimal) -> int:
    """Return the zero-based half-open bin index for an exact Decimal value."""

    return int((value / width).to_integral_value(rounding=ROUND_FLOOR))


def d1_sign_index(longitude: Number) -> int:
    """Return the zero-based D1 sign index."""

    return floor_index(normalized(longitude), SIGN_WIDTH)


def d9_sign_index(longitude: Number) -> int:
    """Return the zero-based Navamsa sign index."""

    return floor_index(normalized(longitude), NAVAMSA_OR_PADA_WIDTH) % 12


def nakshatra_index(longitude: Number) -> int:
    """Return the zero-based nakshatra index."""

    return floor_index(normalized(longitude), NAKSHATRA_WIDTH)


def pada(longitude: Number) -> int:
    """Return the one-based pada within the current nakshatra."""

    within_nakshatra = normalized(longitude) % NAKSHATRA_WIDTH
    return floor_index(within_nakshatra, NAVAMSA_OR_PADA_WIDTH) + 1
