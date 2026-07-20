"""Skyfield/JPL DE440s implementation of the sidereal positions contract."""

from __future__ import annotations

from functools import lru_cache
from math import acos, atan2, cos, degrees, pi, radians, sin
from typing import Any
from uuid import uuid4

import numpy as np
import skyfield
from skyfield.api import Star, load, load_file, wgs84
from skyfield.framelib import ecliptic_frame, true_equator_and_equinox_of_date

from app import __version__
from app.core.jpl_ephemeris import JPL_EPHEMERIS_MODEL, require_jpl_ephemeris
from app.engine.ephemeris_provider import PositionProvider
from app.schemas.positions import (
    Coordinates,
    EngineMetadata,
    NormalizedTime,
    PlanetPosition,
    PositionsRequest,
    PositionsResponse,
    ZodiacPosition,
)

_BODY_TARGETS = (
    ("sun", 10),
    ("moon", 301),
    ("mars", 4),
    ("mercury", 1),
    ("jupiter", 5),
    ("venus", 2),
    ("saturn", 6),
)
_EARTH_TARGET = 399
_NODE_DIFFERENCE_STEP_DAYS = 0.05
_AYANAMSHA_DIFFERENCE_STEP_DAYS = 0.5

# SIMBAD ICRS J2000 position and proper motion for alpha Virginis (Spica/Chitra).
_SPICA = Star(
    ra_hours=(13, 25, 11.57937),
    dec_degrees=(-11, 9, 40.7501),
    ra_mas_per_year=-42.35,
    dec_mas_per_year=-30.67,
    radial_km_per_s=-3.31,
)


@lru_cache(maxsize=1)
def _timescale() -> Any:
    """Use Skyfield's bundled leap-second and Delta-T tables without downloads."""

    return load.timescale(builtin=True)


@lru_cache(maxsize=4)
def _load_kernel(path: str) -> Any:
    """Open and cache a local SPK kernel."""

    return load_file(path)


def _signed_angular_difference(later: float, earlier: float) -> float:
    """Return the shortest signed angular difference in degrees."""

    return (later - earlier + 180.0) % 360.0 - 180.0


def _julian_day_utc(utc_datetime: Any) -> float:
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


def _spica_tropical_longitude(earth: Any, time: Any) -> float:
    apparent = earth.at(time).observe(_SPICA).apparent()
    _latitude, longitude, _distance = apparent.frame_latlon(ecliptic_frame)
    return float(longitude.degrees) % 360.0


def _lahiri_ayanamsha(earth: Any, time: Any) -> float:
    """Anchor Chitrapaksha so apparent Spica has sidereal longitude 180 degrees."""

    return (_spica_tropical_longitude(earth, time) - 180.0) % 360.0


def _lahiri_ayanamsha_rate(earth: Any, time: Any) -> float:
    step = _AYANAMSHA_DIFFERENCE_STEP_DAYS
    before = _lahiri_ayanamsha(earth, time - step)
    after = _lahiri_ayanamsha(earth, time + step)
    return _signed_angular_difference(after, before) / (2.0 * step)


def _true_obliquity_radians(time: Any) -> float:
    """Measure the angle between the true equatorial and ecliptic north poles."""

    equatorial_rotation = np.asarray(
        true_equator_and_equinox_of_date.rotation_at(time), dtype=float
    )
    ecliptic_rotation = np.asarray(ecliptic_frame.rotation_at(time), dtype=float)
    equatorial_pole = equatorial_rotation[2]
    ecliptic_pole = ecliptic_rotation[2]
    denominator = np.linalg.norm(equatorial_pole) * np.linalg.norm(ecliptic_pole)
    cosine = float(np.dot(equatorial_pole, ecliptic_pole) / denominator)
    return acos(max(-1.0, min(1.0, cosine)))


def _ascendant_from_sidereal_time(
    local_apparent_sidereal_hours: float,
    latitude_degrees: float,
    obliquity_radians: float,
) -> float:
    """Return the eastern intersection of the true ecliptic and local horizon."""

    theta = radians((local_apparent_sidereal_hours * 15.0) % 360.0)
    latitude = radians(latitude_degrees)
    coefficient_cosine = cos(latitude) * cos(theta)
    coefficient_sine = (
        cos(latitude) * sin(theta) * cos(obliquity_radians)
        + sin(latitude) * sin(obliquity_radians)
    )
    first = atan2(-coefficient_cosine, coefficient_sine) % (2.0 * pi)
    candidates = (first, (first + pi) % (2.0 * pi))

    for candidate in candidates:
        east_component = (
            -sin(theta) * cos(candidate)
            + cos(theta) * sin(candidate) * cos(obliquity_radians)
        )
        if east_component > 0.0:
            return degrees(candidate) % 360.0

    raise RuntimeError("Could not select the eastern ecliptic-horizon intersection")


def _tropical_ascendant(request: PositionsRequest, time: Any) -> float:
    location = wgs84.latlon(
        request.birth.latitude,
        request.birth.longitude,
        elevation_m=request.birth.altitude_meters,
    )
    local_sidereal_hours = float(location.lst_hours_at(time))
    return _ascendant_from_sidereal_time(
        local_sidereal_hours,
        request.birth.latitude,
        _true_obliquity_radians(time),
    )


def _osculating_node_longitude(kernel: Any, time: Any) -> float:
    """Derive the instantaneous ascending node from the lunar state vector."""

    moon_geocentric = (kernel[301] - kernel[_EARTH_TARGET]).at(time)
    position, velocity = moon_geocentric.frame_xyz_and_velocity(ecliptic_frame)
    radius = np.asarray(position.au, dtype=float)
    motion = np.asarray(velocity.au_per_d, dtype=float)
    angular_momentum = np.cross(radius, motion)
    node = np.cross(np.array([0.0, 0.0, 1.0]), angular_momentum)
    if float(np.linalg.norm(node[:2])) == 0.0:
        raise RuntimeError("Lunar ascending node is undefined for this state vector")
    return degrees(atan2(float(node[1]), float(node[0]))) % 360.0


def _osculating_node_rate(kernel: Any, time: Any) -> float:
    step = _NODE_DIFFERENCE_STEP_DAYS
    before = _osculating_node_longitude(kernel, time - step)
    after = _osculating_node_longitude(kernel, time + step)
    return _signed_angular_difference(after, before) / (2.0 * step)


class SkyfieldJplProvider(PositionProvider):
    """Calculate a complete positions response from local JPL DE440s data."""

    provider_id = "skyfield_jpl_de440s"

    def calculate(self, request: PositionsRequest) -> PositionsResponse:
        from app.engine.positions import _normalize_birth_time, _zodiac_position

        settings = require_jpl_ephemeris()
        fold, local_datetime, utc_datetime = _normalize_birth_time(request)
        time = _timescale().from_datetime(utc_datetime)
        kernel = _load_kernel(str(settings.data_path))
        earth = kernel[_EARTH_TARGET]
        ayanamsha = _lahiri_ayanamsha(earth, time)
        ayanamsha_rate = _lahiri_ayanamsha_rate(earth, time)
        tropical_ascendant = _tropical_ascendant(request, time)
        sidereal_ascendant = (tropical_ascendant - ayanamsha) % 360.0
        ascendant_sign_index = int(sidereal_ascendant // 30.0) + 1
        ascendant = ZodiacPosition(
            **_zodiac_position(sidereal_ascendant, ascendant_sign_index)
        )

        observer = earth.at(time)
        planets: list[PlanetPosition] = []
        for body_name, target_id in _BODY_TARGETS:
            apparent = observer.observe(kernel[target_id]).apparent()
            (
                latitude,
                longitude,
                distance,
                _latitude_rate,
                longitude_rate,
                _radial_rate,
            ) = apparent.frame_latlon_and_rates(ecliptic_frame)
            tropical_longitude = float(longitude.degrees) % 360.0
            sidereal_longitude = (tropical_longitude - ayanamsha) % 360.0
            speed = float(longitude_rate.degrees.per_day) - ayanamsha_rate
            planets.append(
                PlanetPosition(
                    body=body_name,
                    latitude=round(float(latitude.degrees), 8),
                    distance_au=round(float(distance.au), 10),
                    speed_longitude=round(speed, 10),
                    retrograde=speed < 0.0,
                    **_zodiac_position(sidereal_longitude, ascendant_sign_index),
                )
            )

        tropical_rahu = _osculating_node_longitude(kernel, time)
        sidereal_rahu = (tropical_rahu - ayanamsha) % 360.0
        node_speed = _osculating_node_rate(kernel, time) - ayanamsha_rate
        planets.append(
            PlanetPosition(
                body="rahu",
                latitude=0.0,
                distance_au=None,
                speed_longitude=round(node_speed, 10),
                retrograde=node_speed < 0.0,
                **_zodiac_position(sidereal_rahu, ascendant_sign_index),
            )
        )
        planets.append(
            PlanetPosition(
                body="ketu",
                latitude=0.0,
                distance_au=None,
                speed_longitude=round(node_speed, 10),
                retrograde=node_speed < 0.0,
                **_zodiac_position(sidereal_rahu + 180.0, ascendant_sign_index),
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
                julian_day_ut=round(_julian_day_utc(utc_datetime), 9),
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
                astronomical_provider="skyfield_jpl",
                provider_version=str(skyfield.__version__),
                ephemeris_model=JPL_EPHEMERIS_MODEL,
                swiss_ephemeris_version=None,
                zodiac="sidereal",
                ayanamsha="lahiri_chitrapaksha_spica_apparent_v1",
                node_type="true_osculating",
                house_system="whole_sign",
                ephemeris_sources=["jpl_de440s"],
            ),
        )
