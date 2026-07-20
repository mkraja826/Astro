"""Sunrise-based South Indian Panchanga calculations using Skyfield/JPL."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from math import floor
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import skyfield
from skyfield import almanac
from skyfield.api import wgs84
from skyfield.framelib import ecliptic_frame

from app import __version__
from app.core.jpl_ephemeris import JPL_EPHEMERIS_MODEL, require_jpl_ephemeris
from app.engine.positions import NAKSHATRAS
from app.engine.skyfield_jpl import _lahiri_ayanamsha, _load_kernel, _timescale
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
    """Raised when a timezone or requested local date cannot be resolved."""


class SolarEventError(RuntimeError):
    """Raised when geometric sunrise or sunset is unavailable at the location."""


def _timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise PanchangaTimeError(f"Unknown IANA timezone: {name}") from exc


def _utc_datetime(event_time: Any) -> datetime:
    value = event_time.utc_datetime()
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _select_local_event(
    times: Any,
    real_crossings: Any,
    timezone: ZoneInfo,
    requested_date: Any,
    label: str,
) -> tuple[datetime, datetime, Any]:
    for event_time, real_crossing in zip(times, real_crossings, strict=True):
        if not bool(real_crossing):
            continue
        utc_datetime = _utc_datetime(event_time)
        local_datetime = utc_datetime.astimezone(timezone)
        if local_datetime.date() == requested_date:
            return local_datetime, utc_datetime, event_time

    raise SolarEventError(
        f"{label} is unavailable on the requested local date at this location"
    )


def _solar_times(
    request: PanchangaRequest,
    timezone: ZoneInfo,
    kernel: Any,
) -> tuple[datetime, datetime, datetime, datetime, Any]:
    location = request.location
    local_midnight = datetime.combine(location.local_date, time.min, tzinfo=timezone)
    next_midnight = datetime.combine(
        location.local_date + timedelta(days=1),
        time.min,
        tzinfo=timezone,
    )
    timescale = _timescale()
    start = timescale.from_datetime(local_midnight.astimezone(UTC))
    end = timescale.from_datetime(next_midnight.astimezone(UTC))
    observer = kernel[399] + wgs84.latlon(
        location.latitude,
        location.longitude,
        elevation_m=location.altitude_meters,
    )
    sun = kernel[10]

    rising_times, rising_crossings = almanac.find_risings(
        observer,
        sun,
        start,
        end,
        horizon_degrees=0.0,
    )
    setting_times, setting_crossings = almanac.find_settings(
        observer,
        sun,
        start,
        end,
        horizon_degrees=0.0,
    )

    sunrise_local, sunrise_utc, sunrise_time = _select_local_event(
        rising_times,
        rising_crossings,
        timezone,
        location.local_date,
        "Sunrise",
    )
    sunset_local, sunset_utc, _sunset_time = _select_local_event(
        setting_times,
        setting_crossings,
        timezone,
        location.local_date,
        "Sunset",
    )
    return sunrise_local, sunrise_utc, sunset_local, sunset_utc, sunrise_time


def _sidereal_longitude(earth: Any, target: Any, event_time: Any, ayanamsha: float) -> float:
    apparent = earth.at(event_time).observe(target).apparent()
    _latitude, longitude, _distance = apparent.frame_latlon(ecliptic_frame)
    return (float(longitude.degrees) - ayanamsha) % 360.0


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
    """Calculate five limbs of Panchanga at geometric local sunrise."""

    location = request.location
    timezone = _timezone(location.timezone)
    settings = require_jpl_ephemeris()
    kernel = _load_kernel(str(settings.data_path))
    sunrise_local, sunrise_utc, sunset_local, sunset_utc, sunrise_time = _solar_times(
        request,
        timezone,
        kernel,
    )

    earth = kernel[399]
    ayanamsha = _lahiri_ayanamsha(earth, sunrise_time)
    sun_longitude = _sidereal_longitude(earth, kernel[10], sunrise_time, ayanamsha)
    moon_longitude = _sidereal_longitude(earth, kernel[301], sunrise_time, ayanamsha)
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
            method=(
                "Skyfield/JPL geometric solar-center horizon crossing: "
                "0 degrees, no refraction"
            ),
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
            astronomical_provider="skyfield_jpl",
            provider_version=str(skyfield.__version__),
            ephemeris_model=JPL_EPHEMERIS_MODEL,
            swiss_ephemeris_version=None,
            zodiac="sidereal",
            ayanamsha="lahiri_chitrapaksha_spica_apparent_v1",
            node_type="not_applicable",
            house_system="not_applicable",
            ephemeris_sources=["jpl_de440s"],
        ),
    )
