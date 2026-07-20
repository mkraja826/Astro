"""Vimshottari Dasha calculations derived from the sidereal birth Moon."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import floor
from uuid import uuid4

import swisseph as swe

from app import __version__
from app.core.ephemeris import configure_ephemeris, enforce_ephemeris_source
from app.engine.positions import (
    _ENGINE_LOCK,
    NAKSHATRAS,
    _calculate_body,
    _ephemeris_source,
    _julian_day_ut,
    _normalize_birth_time,
)
from app.schemas.dasha import (
    AntardashaPeriod,
    DashaLord,
    DashaMoonPosition,
    MahadashaPeriod,
    VimshottariRequest,
    VimshottariResponse,
)
from app.schemas.positions import (
    Coordinates,
    EngineMetadata,
    NormalizedTime,
    PositionsRequest,
)

DASHA_LORDS = (
    DashaLord.KETU,
    DashaLord.VENUS,
    DashaLord.SUN,
    DashaLord.MOON,
    DashaLord.MARS,
    DashaLord.RAHU,
    DashaLord.JUPITER,
    DashaLord.SATURN,
    DashaLord.MERCURY,
)

DASHA_YEARS = (7.0, 20.0, 6.0, 10.0, 7.0, 18.0, 16.0, 19.0, 17.0)
VIMSHOTTARI_CYCLE_YEARS = sum(DASHA_YEARS)
DASHA_YEAR_DAYS = 365.25
_SECONDS_PER_DAY = 86_400.0


def _years_to_delta(years: float) -> timedelta:
    return timedelta(days=years * DASHA_YEAR_DAYS)


def _delta_to_years(delta: timedelta) -> float:
    return delta.total_seconds() / (_SECONDS_PER_DAY * DASHA_YEAR_DAYS)


def _build_antardashas(
    mahadasha_lord_index: int,
    mahadasha_duration_years: float,
    mahadasha_start: datetime,
    mahadasha_end: datetime,
    birth_utc: datetime,
) -> list[AntardashaPeriod]:
    """Build nine proportional and contiguous sub-periods for one Mahadasha."""

    antardashas: list[AntardashaPeriod] = []
    period_start = mahadasha_start

    for offset in range(len(DASHA_LORDS)):
        lord_index = (mahadasha_lord_index + offset) % len(DASHA_LORDS)
        duration_years = (
            mahadasha_duration_years
            * DASHA_YEARS[lord_index]
            / VIMSHOTTARI_CYCLE_YEARS
        )
        period_end = (
            mahadasha_end
            if offset == len(DASHA_LORDS) - 1
            else period_start + _years_to_delta(duration_years)
        )
        active_at_birth = period_start <= birth_utc < period_end
        elapsed_at_birth_years = None
        remaining_at_birth_years = None

        if active_at_birth:
            elapsed_at_birth_years = round(
                _delta_to_years(birth_utc - period_start),
                9,
            )
            remaining_at_birth_years = round(
                _delta_to_years(period_end - birth_utc),
                9,
            )

        antardashas.append(
            AntardashaPeriod(
                sequence_number=offset + 1,
                lord=DASHA_LORDS[lord_index],
                duration_years=round(duration_years, 9),
                start_utc=period_start,
                end_utc=period_end,
                active_at_birth=active_at_birth,
                elapsed_at_birth_years=elapsed_at_birth_years,
                remaining_at_birth_years=remaining_at_birth_years,
            )
        )
        period_start = period_end

    return antardashas


def calculate_vimshottari(request: VimshottariRequest) -> VimshottariResponse:
    """Return birth balance, Mahadashas and their Antardasha subdivisions."""

    positions_request = PositionsRequest(
        birth=request.birth,
        calculation_profile=request.calculation_profile,
    )
    fold, local_datetime, utc_datetime = _normalize_birth_time(positions_request)
    julian_day = _julian_day_ut(utc_datetime)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    with _ENGINE_LOCK:
        settings = configure_ephemeris()
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        moon_values, returned_flags = _calculate_body(julian_day, swe.MOON, flags)
        source = _ephemeris_source(returned_flags)
        enforce_ephemeris_source(source, "moon", settings)
        ayanamsha = float(swe.get_ayanamsa_ut(julian_day))

    moon_longitude = moon_values[0] % 360.0
    nakshatra_size = 360.0 / 27.0
    pada_size = nakshatra_size / 4.0
    nakshatra_zero_index = min(floor(moon_longitude / nakshatra_size), 26)
    progress_fraction = (moon_longitude % nakshatra_size) / nakshatra_size
    pada = min(floor((moon_longitude % nakshatra_size) / pada_size) + 1, 4)

    birth_lord_index = nakshatra_zero_index % len(DASHA_LORDS)
    birth_lord = DASHA_LORDS[birth_lord_index]
    birth_lord_years = DASHA_YEARS[birth_lord_index]
    elapsed_years = birth_lord_years * progress_fraction
    remaining_years = birth_lord_years - elapsed_years

    first_start = utc_datetime - _years_to_delta(elapsed_years)
    first_end = first_start + _years_to_delta(birth_lord_years)

    periods: list[MahadashaPeriod] = []
    period_start = first_start
    for offset in range(len(DASHA_LORDS)):
        lord_index = (birth_lord_index + offset) % len(DASHA_LORDS)
        duration_years = DASHA_YEARS[lord_index]
        period_end = (
            first_end
            if offset == 0
            else period_start + _years_to_delta(duration_years)
        )
        active_at_birth = offset == 0

        periods.append(
            MahadashaPeriod(
                sequence_number=offset + 1,
                lord=DASHA_LORDS[lord_index],
                duration_years=duration_years,
                start_utc=period_start,
                end_utc=period_end,
                active_at_birth=active_at_birth,
                elapsed_at_birth_years=(
                    round(elapsed_years, 9) if active_at_birth else None
                ),
                remaining_at_birth_years=(
                    round(remaining_years, 9) if active_at_birth else None
                ),
                antardashas=_build_antardashas(
                    lord_index,
                    duration_years,
                    period_start,
                    period_end,
                    utc_datetime,
                ),
            )
        )
        period_start = period_end

    return VimshottariResponse(
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
        moon=DashaMoonPosition(
            longitude=round(moon_longitude, 8),
            nakshatra_index=nakshatra_zero_index + 1,
            nakshatra=NAKSHATRAS[nakshatra_zero_index],
            pada=pada,
            progress_percent=round(progress_fraction * 100.0, 6),
        ),
        birth_lord=birth_lord,
        birth_balance_years=round(remaining_years, 9),
        cycle_years=VIMSHOTTARI_CYCLE_YEARS,
        year_length_days=DASHA_YEAR_DAYS,
        ayanamsha_degrees=round(ayanamsha, 8),
        mahadashas=periods,
        metadata=EngineMetadata(
            engine="jyothisyam-api",
            engine_version=__version__,
            swiss_ephemeris_version=str(swe.version),
            zodiac="sidereal",
            ayanamsha="lahiri",
            node_type="not_applicable",
            house_system="not_applicable",
            ephemeris_sources=[source],
        ),
    )
