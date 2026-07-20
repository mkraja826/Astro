"""Sunrise-based South Indian Panchanga calculations."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from math import floor
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app import __version__
from app.core.ephemeris import configure_ephemeris, enforce_ephemeris_source
from app.engine.positions import (
    NAKSHATRAS,
    _calculate_body,
    _ephemeris_source,
    _julian_day_ut,
)
from app.schemas.panchanga import (
    KaranaElement,
    NakshatraElement,
    PanchangaElement,
    PanchangaRequest,
    PanchangaResponse,
    SolarTimes,
    TithiElement,
)
from app.schemas.positions import Coordinates, EngineMetadata

VARAS = (
    "Somavara",
    "Mangalavara",
    "Budhavara",
    "Guruvara",
    "Shukravara",
    "Shanivara",
    "Ravivara",
)

TITHIS = (
    "Shukla Pratipada",
    "Shukla Dwitiya",
    "Shukla Tritiya",
    "Shukla Chaturthi",
    "Shukla Panchami",
    "Shukla Shashthi",
    "Shukla Saptami",
    "Shukla Ashtami",
    "Shukla Navami",
    "Shukla Dashami",
    "Shukla Ekadashi",
    "Shukla Dwadashi",
    "Shukla Trayodashi",
    "Shukla Chaturdashi",
    "Purnima",
    "Krishna Pratipada",
    "Krishna Dwitiya",
    "Krishna Tritiya",
    "Krishna Chaturthi",
    "Krishna Panchami",
    "Krishna Shashthi",
    "Krishna Saptami",
    "Krishna Ashtami",
    "Krishna Navami",
    "Krishna Dashami",
    "Krishna Ekadashi",
    "Krishna Dwadashi",
    "Krishna Trayodashi",
    "Krishna Chaturdashi",
    "Amavasya",
)

YOGAS = (
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
)

MOVABLE_KARANAS = (
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Garaja",
    "Vanija",
    "Vishti",
)


class PanchangaTimeError(ValueError):
    """Raised when timezone or solar events cannot be resolved for a date."""


class SolarEventError(RuntimeError):
    """Raised when sunrise or sunset is unavailable at the requested location."""


def _timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise PanchangaTimeError(f"Unknown IANA timezone: {name}") from exc


def _julian_day_to_utc(julian_day: float) -> datetime:
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    return epoch + timedelta(days=julian_day - 2440587.5)


def _normalize_rise_trans_result(result: tuple[object, ...]) -> tuple[int, tuple[float, ...]]:
    if len(result) == 3:
        status_code, times, _message = result
    elif len(result) == 2:
        status_code, times = result
    else:
        raise SolarEventError("Unexpected Swiss Ephemeris rise_trans response")

    return int(status_code), tuple(float(value) for value in times)


def _solar_event(
    start_julian_day: float,
    request: PanchangaRequest,
    timezone: ZoneInfo,
    event_flag: int,
    label: str,
) -> tuple[datetime, datetime, float]:
    location = request.location
    geopos = (location.longitude, location.latitude, location.altitude_meters)
    hindu_rising = getattr(
        swe,
        "BIT_HINDU_RISING",
        swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION | swe.BIT_GEOCTR_NO_ECL_LAT,
    )
    result = swe.rise_trans(
        start_julian_day,
        swe.SUN,
        event_flag | hindu_rising,
        geopos,
        0.0,
        0.0,
        swe.FLG_SWIEPH,
    )
    status_code, times = _normalize_rise_trans_result(result)
    if status_code != 0 or not times:
        raise SolarEventError(f"{label} is unavailable for the requested date and location")

    julian_day = times[0]
    utc_datetime = _julian_day_to_utc(julian_day)
    local_datetime = utc_datetime.astimezone(timezone)
    if local_datetime.date() != location.local_date:
        raise SolarEventError(f"{label} is unavailable on the requested local date")

    return local_datetime, utc_datetime, julian_day


def _element(index: int, names: tuple[str, ...], progress: float) -> PanchangaElement:
    return PanchangaElement(
        index=index + 1,
        name=names[index],
        progress_percent=round(progress, 6),
    )


def _karana(half_tithi_index: int, progress: float) -> KaranaElement:
    if half_tithi_index == 0:
        name = "Kimstughna"
    elif half_tithi_index <= 56:
        name = MOVABLE_KARANAS[(half_tithi_index - 1) % len(MOVABLE_KARANAS)]
    elif half_tithi_index == 57:
        name = "Shakuni"
    elif half_tithi_index == 58:
        name = "Chatushpada"
    else:
        name = "Naga"

    return KaranaElement(
        index=half_tithi_index + 1,
        half_tithi_index=half_tithi_index + 1,
        name=name,
        progress_percent=round(progress, 6),
    )


def calculate_panchanga(request: PanchangaRequest) -> PanchangaResponse:
    """Calculate five limbs of Panchanga at Hindu sunrise for a local date."""

    location = request.location
    timezone = _timezone(location.timezone)
    local_midnight = datetime.combine(location.local_date, time.min, tzinfo=timezone)
    start_utc = local_midnight.astimezone(UTC)
    start_julian_day = _julian_day_ut(start_utc)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    settings = configure_ephemeris()
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    sunrise_local, sunrise_utc, sunrise_jd = _solar_event(
        start_julian_day,
        request,
        timezone,
        swe.CALC_RISE,
        "Sunrise",
    )
    sunset_local, sunset_utc, _sunset_jd = _solar_event(
        sunrise_jd + 1e-6,
        request,
        timezone,
        swe.CALC_SET,
        "Sunset",
    )

    sun_values, sun_flags = _calculate_body(sunrise_jd, swe.SUN, flags)
    moon_values, moon_flags = _calculate_body(sunrise_jd, swe.MOON, flags)
    sun_source = _ephemeris_source(sun_flags)
    moon_source = _ephemeris_source(moon_flags)
    enforce_ephemeris_source(sun_source, "sun", settings)
    enforce_ephemeris_source(moon_source, "moon", settings)

    sun_longitude = sun_values[0] % 360.0
    moon_longitude = moon_values[0] % 360.0
    tithi_angle = (moon_longitude - sun_longitude) % 360.0

    tithi_zero_index = min(floor(tithi_angle / 12.0), 29)
    tithi_progress = (tithi_angle % 12.0) / 12.0 * 100.0
    paksha = "Shukla" if tithi_zero_index < 15 else "Krishna"

    nakshatra_size = 360.0 / 27.0
    pada_size = nakshatra_size / 4.0
    nakshatra_zero_index = min(floor(moon_longitude / nakshatra_size), 26)
    nakshatra_progress = (moon_longitude % nakshatra_size) / nakshatra_size * 100.0
    pada = min(floor((moon_longitude % nakshatra_size) / pada_size) + 1, 4)

    yoga_longitude = (sun_longitude + moon_longitude) % 360.0
    yoga_zero_index = min(floor(yoga_longitude / nakshatra_size), 26)
    yoga_progress = (yoga_longitude % nakshatra_size) / nakshatra_size * 100.0

    half_tithi_index = min(floor(tithi_angle / 6.0), 59)
    karana_progress = (tithi_angle % 6.0) / 6.0 * 100.0
    ayanamsha = float(swe.get_ayanamsa_ut(sunrise_jd))

    return PanchangaResponse(
        request_id=f"req_{uuid4().hex}",
        calculation_profile=request.calculation_profile,
        local_date=location.local_date,
        timezone=location.timezone,
        coordinates=Coordinates(
            latitude=location.latitude,
            longitude=location.longitude,
            altitude_meters=location.altitude_meters,
        ),
        solar_times=SolarTimes(
            sunrise_local=sunrise_local,
            sunrise_utc=sunrise_utc,
            sunset_local=sunset_local,
            sunset_utc=sunset_utc,
            method="Swiss Ephemeris Hindu rising: disc center, no refraction",
        ),
        vara=PanchangaElement(
            index=location.local_date.weekday() + 1,
            name=VARAS[location.local_date.weekday()],
            progress_percent=0.0,
        ),
        tithi=TithiElement(
            index=tithi_zero_index + 1,
            name=TITHIS[tithi_zero_index],
            paksha=paksha,
            progress_percent=round(tithi_progress, 6),
        ),
        nakshatra=NakshatraElement(
            index=nakshatra_zero_index + 1,
            name=NAKSHATRAS[nakshatra_zero_index],
            pada=pada,
            progress_percent=round(nakshatra_progress, 6),
        ),
        yoga=_element(yoga_zero_index, YOGAS, yoga_progress),
        karana=_karana(half_tithi_index, karana_progress),
        evaluated_at_local=sunrise_local,
        evaluated_at_utc=sunrise_utc,
        ayanamsha_degrees=round(ayanamsha, 8),
        metadata=EngineMetadata(
            engine="jyothisyam-api",
            engine_version=__version__,
            swiss_ephemeris_version=str(swe.version),
            zodiac="sidereal",
            ayanamsha="lahiri",
            node_type="not_applicable",
            house_system="not_applicable",
            ephemeris_sources=sorted({sun_source, moon_source}),
        ),
    )
