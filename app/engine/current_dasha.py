"""Efficient active-period lookup for nested Vimshottari Dasha timelines."""

from __future__ import annotations

from datetime import UTC, datetime
from math import floor
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app import __version__
from app.core.ephemeris import configure_ephemeris, enforce_ephemeris_source
from app.engine.dasha import (
    DASHA_LORDS,
    DASHA_YEAR_DAYS,
    DASHA_YEARS,
    VIMSHOTTARI_CYCLE_YEARS,
    _delta_to_years,
    _years_to_delta,
)
from app.engine.positions import (
    _ENGINE_LOCK,
    NAKSHATRAS,
    _calculate_body,
    _ephemeris_source,
    _julian_day_ut,
    _normalize_birth_time,
)
from app.schemas.dasha import (
    ActiveDashaPeriod,
    CurrentVimshottariRequest,
    CurrentVimshottariResponse,
    DashaMoonPosition,
    DashaQueryTime,
)
from app.schemas.positions import (
    Coordinates,
    EngineMetadata,
    NormalizedTime,
    PositionsRequest,
)


class DashaQueryError(ValueError):
    """Raised when the requested active-period instant cannot be resolved."""


def _normalize_query_time(query: DashaQueryTime) -> tuple[int, datetime, datetime]:
    """Resolve a local civil query time without silently guessing DST folds."""

    try:
        timezone = ZoneInfo(query.timezone)
    except ZoneInfoNotFoundError as exc:
        raise DashaQueryError(f"Unknown IANA timezone: {query.timezone}") from exc

    candidates: list[tuple[int, datetime, datetime]] = []
    for fold in (0, 1):
        local = query.local_datetime.replace(tzinfo=timezone, fold=fold)
        utc = local.astimezone(UTC)
        round_trip = utc.astimezone(timezone)
        if round_trip.replace(tzinfo=None) == query.local_datetime:
            candidates.append((fold, local, utc))

    unique_instants = {candidate[2] for candidate in candidates}
    if not unique_instants:
        raise DashaQueryError(
            "The supplied query time does not exist in this timezone due to a clock change"
        )

    if len(unique_instants) > 1:
        if query.fold is None:
            raise DashaQueryError(
                "The supplied query time is ambiguous; set fold to 0 or 1"
            )
        selected = next((item for item in candidates if item[0] == query.fold), None)
        if selected is None:
            raise DashaQueryError("The requested fold is not valid for this query time")
    else:
        selected = candidates[0]

    return selected


def _select_active_period(
    start_lord_index: int,
    parent_duration_years: float,
    parent_start: datetime,
    parent_end: datetime,
    target_utc: datetime,
) -> tuple[ActiveDashaPeriod, int]:
    """Select one active child without constructing sibling response objects."""

    period_start = parent_start
    for offset in range(len(DASHA_LORDS)):
        lord_index = (start_lord_index + offset) % len(DASHA_LORDS)
        duration_years = (
            parent_duration_years
            * DASHA_YEARS[lord_index]
            / VIMSHOTTARI_CYCLE_YEARS
        )
        period_end = (
            parent_end
            if offset == len(DASHA_LORDS) - 1
            else period_start + _years_to_delta(duration_years)
        )

        if period_start <= target_utc < period_end:
            elapsed_years = _delta_to_years(target_utc - period_start)
            remaining_years = _delta_to_years(period_end - target_utc)
            total_seconds = (period_end - period_start).total_seconds()
            progress_percent = (
                (target_utc - period_start).total_seconds() / total_seconds * 100.0
            )
            return (
                ActiveDashaPeriod(
                    sequence_number=offset + 1,
                    lord=DASHA_LORDS[lord_index],
                    duration_years=round(duration_years, 15),
                    start_utc=period_start,
                    end_utc=period_end,
                    elapsed_as_of_years=round(elapsed_years, 12),
                    remaining_as_of_years=round(remaining_years, 12),
                    progress_percent=round(progress_percent, 9),
                ),
                lord_index,
            )

        period_start = period_end

    raise DashaQueryError("The requested instant is outside the selected parent period")


def calculate_current_vimshottari(
    request: CurrentVimshottariRequest,
) -> CurrentVimshottariResponse:
    """Return only the active four-level Vimshottari chain at one instant."""

    positions_request = PositionsRequest(
        birth=request.birth,
        calculation_profile=request.calculation_profile,
    )
    birth_fold, birth_local, birth_utc = _normalize_birth_time(positions_request)
    query_fold, query_local, query_utc = _normalize_query_time(request.as_of)
    birth_julian_day = _julian_day_ut(birth_utc)
    query_julian_day = _julian_day_ut(query_utc)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    with _ENGINE_LOCK:
        settings = configure_ephemeris()
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        moon_values, returned_flags = _calculate_body(
            birth_julian_day,
            swe.MOON,
            flags,
        )
        source = _ephemeris_source(returned_flags)
        enforce_ephemeris_source(source, "moon", settings)
        ayanamsha = float(swe.get_ayanamsa_ut(birth_julian_day))

    moon_longitude = moon_values[0] % 360.0
    nakshatra_size = 360.0 / 27.0
    pada_size = nakshatra_size / 4.0
    nakshatra_zero_index = min(floor(moon_longitude / nakshatra_size), 26)
    progress_fraction = (moon_longitude % nakshatra_size) / nakshatra_size
    pada = min(floor((moon_longitude % nakshatra_size) / pada_size) + 1, 4)

    birth_lord_index = nakshatra_zero_index % len(DASHA_LORDS)
    birth_lord = DASHA_LORDS[birth_lord_index]
    birth_lord_years = DASHA_YEARS[birth_lord_index]
    elapsed_at_birth_years = birth_lord_years * progress_fraction
    remaining_at_birth_years = birth_lord_years - elapsed_at_birth_years

    cycle_start = birth_utc - _years_to_delta(elapsed_at_birth_years)
    cycle_end = cycle_start + _years_to_delta(VIMSHOTTARI_CYCLE_YEARS)

    if query_utc < birth_utc:
        raise DashaQueryError("The requested instant must be at or after the birth time")
    if query_utc >= cycle_end:
        raise DashaQueryError(
            "The requested instant is outside the first 120-year Vimshottari cycle"
        )

    mahadasha, mahadasha_lord_index = _select_active_period(
        birth_lord_index,
        VIMSHOTTARI_CYCLE_YEARS,
        cycle_start,
        cycle_end,
        query_utc,
    )
    antardasha, antardasha_lord_index = _select_active_period(
        mahadasha_lord_index,
        mahadasha.duration_years,
        mahadasha.start_utc,
        mahadasha.end_utc,
        query_utc,
    )
    pratyantardasha, pratyantardasha_lord_index = _select_active_period(
        antardasha_lord_index,
        antardasha.duration_years,
        antardasha.start_utc,
        antardasha.end_utc,
        query_utc,
    )
    sookshma, _ = _select_active_period(
        pratyantardasha_lord_index,
        pratyantardasha.duration_years,
        pratyantardasha.start_utc,
        pratyantardasha.end_utc,
        query_utc,
    )

    return CurrentVimshottariResponse(
        request_id=f"req_{uuid4().hex}",
        calculation_profile=request.calculation_profile,
        birth_time=NormalizedTime(
            local_datetime=birth_local,
            utc_datetime=birth_utc,
            timezone=request.birth.timezone,
            fold=birth_fold,
            julian_day_ut=round(birth_julian_day, 9),
        ),
        query_time=NormalizedTime(
            local_datetime=query_local,
            utc_datetime=query_utc,
            timezone=request.as_of.timezone,
            fold=query_fold,
            julian_day_ut=round(query_julian_day, 9),
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
        birth_balance_years=round(remaining_at_birth_years, 9),
        year_length_days=DASHA_YEAR_DAYS,
        cycle_start_utc=cycle_start,
        cycle_end_utc=cycle_end,
        ayanamsha_degrees=round(ayanamsha, 8),
        mahadasha=mahadasha,
        antardasha=antardasha,
        pratyantardasha=pratyantardasha,
        sookshma=sookshma,
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
