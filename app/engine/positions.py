"""Sidereal position calculations backed exclusively by Skyfield/JPL."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.schemas.positions import PositionsRequest, PositionsResponse

SIGNS = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

NAKSHATRAS = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)


class BirthTimeError(ValueError):
    """Raised when a supplied local civil time cannot be resolved safely."""


def _normalize_birth_time(request: PositionsRequest) -> tuple[int, datetime, datetime]:
    birth = request.birth

    try:
        timezone = ZoneInfo(birth.timezone)
    except ZoneInfoNotFoundError as exc:
        raise BirthTimeError(f"Unknown IANA timezone: {birth.timezone}") from exc

    candidates: list[tuple[int, datetime, datetime]] = []
    for fold in (0, 1):
        local = birth.local_datetime.replace(tzinfo=timezone, fold=fold)
        utc = local.astimezone(UTC)
        round_trip = utc.astimezone(timezone)
        if round_trip.replace(tzinfo=None) == birth.local_datetime:
            candidates.append((fold, local, utc))

    unique_instants = {candidate[2] for candidate in candidates}
    if not unique_instants:
        raise BirthTimeError(
            "The supplied local time does not exist in this timezone due to a clock change"
        )

    if len(unique_instants) > 1:
        if birth.fold is None:
            raise BirthTimeError(
                "The supplied local time is ambiguous; set fold to 0 or 1"
            )
        selected = next((item for item in candidates if item[0] == birth.fold), None)
        if selected is None:
            raise BirthTimeError("The requested fold is not valid for this local time")
    else:
        selected = candidates[0]

    return selected


def _julian_day_ut(utc_datetime: datetime) -> float:
    """Convert a proleptic Gregorian UTC datetime to a Julian day number."""

    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    julian_day_number = (
        day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )
    day_fraction = (
        utc_datetime.hour
        + utc_datetime.minute / 60.0
        + utc_datetime.second / 3600.0
        + utc_datetime.microsecond / 3_600_000_000.0
    ) / 24.0
    return float(julian_day_number) - 0.5 + day_fraction


def _zodiac_position(longitude: float, ascendant_sign_index: int) -> dict[str, object]:
    normalized = longitude % 360.0
    sign_zero_index = int(normalized // 30.0)
    nakshatra_size = 360.0 / 27.0
    pada_size = nakshatra_size / 4.0
    nakshatra_zero_index = min(int(normalized // nakshatra_size), 26)
    pada = min(int((normalized % nakshatra_size) // pada_size) + 1, 4)
    sign_index = sign_zero_index + 1

    return {
        "longitude": round(normalized, 8),
        "sign_index": sign_index,
        "sign": SIGNS[sign_zero_index],
        "degree_in_sign": round(normalized % 30.0, 8),
        "nakshatra_index": nakshatra_zero_index + 1,
        "nakshatra": NAKSHATRAS[nakshatra_zero_index],
        "pada": pada,
        "whole_sign_house": ((sign_index - ascendant_sign_index) % 12) + 1,
    }


def calculate_positions(request: PositionsRequest) -> PositionsResponse:
    """Calculate every accepted profile through the production JPL provider."""

    from app.engine.skyfield_jpl import SkyfieldJplProvider

    return SkyfieldJplProvider().calculate(request)
