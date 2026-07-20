"""Vimshottari Dasha calculations derived from the sidereal birth Moon."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import floor
from uuid import uuid4

from app.engine.positions import NAKSHATRAS, calculate_positions
from app.schemas.dasha import (
    AntardashaPeriod,
    DashaDepth,
    DashaLord,
    DashaMoonPosition,
    MahadashaPeriod,
    PratyantardashaPeriod,
    SookshmaDashaPeriod,
    VimshottariRequest,
    VimshottariResponse,
)
from app.schemas.positions import PositionsRequest

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


def _birth_balance(
    period_start: datetime,
    period_end: datetime,
    birth_utc: datetime,
) -> tuple[bool, float | None, float | None]:
    active_at_birth = period_start <= birth_utc < period_end
    if not active_at_birth:
        return False, None, None

    return (
        True,
        round(_delta_to_years(birth_utc - period_start), 9),
        round(_delta_to_years(period_end - birth_utc), 9),
    )


def _build_sookshmadashas(
    pratyantardasha_lord_index: int,
    pratyantardasha_duration_years: float,
    pratyantardasha_start: datetime,
    pratyantardasha_end: datetime,
    birth_utc: datetime,
) -> list[SookshmaDashaPeriod]:
    """Build nine proportional fourth-level periods for one Pratyantardasha."""

    periods: list[SookshmaDashaPeriod] = []
    period_start = pratyantardasha_start

    for offset in range(len(DASHA_LORDS)):
        lord_index = (pratyantardasha_lord_index + offset) % len(DASHA_LORDS)
        duration_years = (
            pratyantardasha_duration_years
            * DASHA_YEARS[lord_index]
            / VIMSHOTTARI_CYCLE_YEARS
        )
        period_end = (
            pratyantardasha_end
            if offset == len(DASHA_LORDS) - 1
            else period_start + _years_to_delta(duration_years)
        )
        active_at_birth, elapsed_years, remaining_years = _birth_balance(
            period_start,
            period_end,
            birth_utc,
        )

        periods.append(
            SookshmaDashaPeriod(
                sequence_number=offset + 1,
                lord=DASHA_LORDS[lord_index],
                duration_years=round(duration_years, 15),
                start_utc=period_start,
                end_utc=period_end,
                active_at_birth=active_at_birth,
                elapsed_at_birth_years=elapsed_years,
                remaining_at_birth_years=remaining_years,
            )
        )
        period_start = period_end

    return periods


def _build_pratyantardashas(
    antardasha_lord_index: int,
    antardasha_duration_years: float,
    antardasha_start: datetime,
    antardasha_end: datetime,
    birth_utc: datetime,
    include_sookshma: bool,
) -> list[PratyantardashaPeriod]:
    """Build nine proportional third-level periods for one Antardasha."""

    periods: list[PratyantardashaPeriod] = []
    period_start = antardasha_start

    for offset in range(len(DASHA_LORDS)):
        lord_index = (antardasha_lord_index + offset) % len(DASHA_LORDS)
        duration_years = (
            antardasha_duration_years
            * DASHA_YEARS[lord_index]
            / VIMSHOTTARI_CYCLE_YEARS
        )
        period_end = (
            antardasha_end
            if offset == len(DASHA_LORDS) - 1
            else period_start + _years_to_delta(duration_years)
        )
        active_at_birth, elapsed_years, remaining_years = _birth_balance(
            period_start,
            period_end,
            birth_utc,
        )

        periods.append(
            PratyantardashaPeriod(
                sequence_number=offset + 1,
                lord=DASHA_LORDS[lord_index],
                duration_years=round(duration_years, 12),
                start_utc=period_start,
                end_utc=period_end,
                active_at_birth=active_at_birth,
                elapsed_at_birth_years=elapsed_years,
                remaining_at_birth_years=remaining_years,
                sookshmadashas=(
                    _build_sookshmadashas(
                        lord_index,
                        duration_years,
                        period_start,
                        period_end,
                        birth_utc,
                    )
                    if include_sookshma
                    else None
                ),
            )
        )
        period_start = period_end

    return periods


def _build_antardashas(
    mahadasha_lord_index: int,
    mahadasha_duration_years: float,
    mahadasha_start: datetime,
    mahadasha_end: datetime,
    birth_utc: datetime,
    include_sookshma: bool,
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
        active_at_birth, elapsed_years, remaining_years = _birth_balance(
            period_start,
            period_end,
            birth_utc,
        )

        antardashas.append(
            AntardashaPeriod(
                sequence_number=offset + 1,
                lord=DASHA_LORDS[lord_index],
                duration_years=round(duration_years, 9),
                start_utc=period_start,
                end_utc=period_end,
                active_at_birth=active_at_birth,
                elapsed_at_birth_years=elapsed_years,
                remaining_at_birth_years=remaining_years,
                pratyantardashas=_build_pratyantardashas(
                    lord_index,
                    duration_years,
                    period_start,
                    period_end,
                    birth_utc,
                    include_sookshma,
                ),
            )
        )
        period_start = period_end

    return antardashas


def calculate_vimshottari(request: VimshottariRequest) -> VimshottariResponse:
    """Return Vimshottari timelines through the requested subdivision depth."""

    positions = calculate_positions(
        PositionsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    birth_utc = positions.time.utc_datetime
    moon = next(planet for planet in positions.planets if planet.body == "moon")
    moon_longitude = moon.longitude
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

    first_start = birth_utc - _years_to_delta(elapsed_years)
    first_end = first_start + _years_to_delta(birth_lord_years)
    include_sookshma = request.depth == DashaDepth.SOOKSHMA

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
                    birth_utc,
                    include_sookshma,
                ),
            )
        )
        period_start = period_end

    metadata = positions.metadata.model_copy(
        update={
            "node_type": "not_applicable",
            "house_system": "not_applicable",
        }
    )

    return VimshottariResponse(
        request_id=f"req_{uuid4().hex}",
        calculation_profile=request.calculation_profile,
        time=positions.time,
        coordinates=positions.coordinates,
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
        ayanamsha_degrees=positions.ayanamsha_degrees,
        mahadashas=periods,
        metadata=metadata,
    )
