"""Swiss Ephemeris-backed sidereal position calculations."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app import __version__
from app.schemas.positions import (
    Coordinates,
    EngineMetadata,
    NormalizedTime,
    PlanetPosition,
    PositionsRequest,
    PositionsResponse,
    ZodiacPosition,
)

_ENGINE_LOCK = RLock()

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

PLANETS = (
    ("sun", swe.SUN),
    ("moon", swe.MOON),
    ("mars", swe.MARS),
    ("mercury", swe.MERCURY),
    ("jupiter", swe.JUPITER),
    ("venus", swe.VENUS),
    ("saturn", swe.SATURN),
    ("rahu", swe.TRUE_NODE),
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
    hour = (
        utc_datetime.hour
        + utc_datetime.minute / 60
        + utc_datetime.second / 3600
        + utc_datetime.microsecond / 3_600_000_000
    )
    return float(
        swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            hour,
            swe.GREG_CAL,
        )
    )


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


def _ephemeris_source(returned_flags: int) -> str:
    if returned_flags & swe.FLG_JPLEPH:
        return "jpl"
    if returned_flags & swe.FLG_SWIEPH:
        return "swiss"
    if returned_flags & swe.FLG_MOSEPH:
        return "moshier"
    return "unknown"


def _calculate_body(
    julian_day: float,
    body_id: int,
    flags: int,
) -> tuple[tuple[float, ...], int]:
    """Normalize Swiss Ephemeris binding return formats.

    The maintained ``pysweph`` binding returns ``(values, flags, message)``.
    Older compatible bindings return ``(values, flags)``. The diagnostic message
    is intentionally not used as a calculation result; the returned flags remain
    the source of truth for the ephemeris actually used.
    """

    result = swe.calc_ut(julian_day, body_id, flags)
    if len(result) == 3:
        values, returned_flags, _message = result
    elif len(result) == 2:
        values, returned_flags = result
    else:
        raise RuntimeError("Unexpected Swiss Ephemeris calc_ut response")

    return tuple(float(value) for value in values), int(returned_flags)


def calculate_positions(request: PositionsRequest) -> PositionsResponse:
    """Calculate Lahiri sidereal positions for the supported South Indian profile."""

    fold, local_datetime, utc_datetime = _normalize_birth_time(request)
    julian_day = _julian_day_ut(utc_datetime)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    with _ENGINE_LOCK:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsha = float(swe.get_ayanamsa_ut(julian_day))
        _, ascendant_points = swe.houses_ex(
            julian_day,
            request.birth.latitude,
            request.birth.longitude,
            b"W",
            swe.FLG_SIDEREAL,
        )
        ascendant_longitude = float(ascendant_points[0]) % 360.0
        ascendant_sign_index = int(ascendant_longitude // 30.0) + 1
        ascendant = ZodiacPosition(
            **_zodiac_position(ascendant_longitude, ascendant_sign_index)
        )

        planets: list[PlanetPosition] = []
        ephemeris_sources: set[str] = set()
        rahu_values: tuple[float, ...] | None = None

        for body_name, body_id in PLANETS:
            values, returned_flags = _calculate_body(julian_day, body_id, flags)
            ephemeris_sources.add(_ephemeris_source(returned_flags))

            if body_name == "rahu":
                rahu_values = values

            planets.append(
                PlanetPosition(
                    body=body_name,
                    latitude=round(values[1], 8),
                    distance_au=round(values[2], 10),
                    speed_longitude=round(values[3], 10),
                    retrograde=values[3] < 0,
                    **_zodiac_position(values[0], ascendant_sign_index),
                )
            )

        if rahu_values is None:
            raise RuntimeError("Rahu calculation was not produced")

        planets.append(
            PlanetPosition(
                body="ketu",
                latitude=round(-rahu_values[1], 8),
                distance_au=None,
                speed_longitude=round(rahu_values[3], 10),
                retrograde=rahu_values[3] < 0,
                **_zodiac_position(rahu_values[0] + 180.0, ascendant_sign_index),
            )
        )

    return PositionsResponse(
        request_id=f"req_{uuid4().hex}",
        calculation_profile=request.calculation_profile,
        time=NormalizedTime(
            local_datetime=local_datetime,
            utc_datetime=utc_datetime,
            timezone=request.birth.timezone,
            fold=fold,
            julian_day_ut=round(julian_day, 9),
        ),
        coordinates=Coordinates(
            latitude=request.birth.latitude,
            longitude=request.birth.longitude,
            altitude_meters=request.birth.altitude_meters,
        ),
        ayanamsha_degrees=round(ayanamsha, 8),
        ascendant=ascendant,
        planets=planets,
        metadata=EngineMetadata(
            engine="jyothisyam-api",
            engine_version=__version__,
            swiss_ephemeris_version=str(swe.version),
            zodiac="sidereal",
            ayanamsha="lahiri",
            node_type="true",
            house_system="whole_sign",
            ephemeris_sources=sorted(ephemeris_sources),
        ),
    )
