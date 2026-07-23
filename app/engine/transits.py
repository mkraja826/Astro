"""Compose raw JPL-backed natal and transit positions without interpretation."""

from uuid import uuid4

from app.engine.positions import calculate_positions
from app.schemas.positions import BirthInput, PositionsRequest
from app.schemas.transits import (
    TransitReferenceRelation,
    TransitSnapshotRequest,
    TransitSnapshotResponse,
)


def _whole_sign_distance(source_sign: int, target_sign: int) -> int:
    """Return the inclusive whole-sign distance from source to target."""

    return ((target_sign - source_sign) % 12) + 1


def calculate_transit_snapshot(
    request: TransitSnapshotRequest,
) -> TransitSnapshotResponse:
    """Calculate one immutable transit instant and natal reference geometry."""

    natal = calculate_positions(
        PositionsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    transit = calculate_positions(
        PositionsRequest(
            birth=BirthInput(
                local_datetime=request.as_of.local_datetime,
                timezone=request.as_of.timezone,
                latitude=request.birth.latitude,
                longitude=request.birth.longitude,
                altitude_meters=request.birth.altitude_meters,
                fold=request.as_of.fold,
            ),
            calculation_profile=request.calculation_profile,
        )
    )

    natal_by_body = {point.body: point for point in natal.planets}
    natal_moon_sign = natal_by_body["moon"].sign_index
    natal_ascendant_sign = natal.ascendant.sign_index
    relations = [
        TransitReferenceRelation(
            body=point.body,
            natal_sign_index=natal_by_body[point.body].sign_index,
            transit_sign_index=point.sign_index,
            whole_sign_distance_from_natal_position=_whole_sign_distance(
                natal_by_body[point.body].sign_index,
                point.sign_index,
            ),
            whole_sign_house_from_natal_ascendant=_whole_sign_distance(
                natal_ascendant_sign,
                point.sign_index,
            ),
            whole_sign_house_from_natal_moon=_whole_sign_distance(
                natal_moon_sign,
                point.sign_index,
            ),
        )
        for point in transit.planets
    ]

    return TransitSnapshotResponse(
        request_id=f"req_{uuid4().hex}",
        calculation_profile=request.calculation_profile,
        natal=natal,
        transit=transit,
        relations=relations,
        interpretation_applied=False,
        timing_window_applied=False,
        caveats=[
            "This response contains astronomical positions and whole-sign geometry only.",
            "No transit is classified as favourable, adverse, strong, weak, or event-producing.",
            "No daily, weekly, monthly, or exact clock-time window is inferred.",
        ],
    )
