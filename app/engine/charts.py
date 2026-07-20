"""D1 Rasi and D9 Navamsa chart calculations."""

from uuid import uuid4

from app.engine.positions import SIGNS, calculate_positions
from app.schemas.charts import (
    ChartPoint,
    ChartRequest,
    ChartResponse,
    ChartType,
    SouthIndianSignCell,
)
from app.schemas.positions import PositionsRequest

SOUTH_INDIAN_GRID = {
    1: (1, 2),
    2: (1, 3),
    3: (1, 4),
    4: (2, 4),
    5: (3, 4),
    6: (4, 4),
    7: (4, 3),
    8: (4, 2),
    9: (4, 1),
    10: (3, 1),
    11: (2, 1),
    12: (1, 1),
}


def _chart_longitude(source_longitude: float, division: int) -> float:
    """Map a sidereal longitude into the requested equal-division chart."""

    if division == 1:
        return source_longitude % 360.0
    if division == 9:
        # Parashari Navamsa: each 3°20′ segment advances one zodiac sign.
        return (source_longitude * 9.0) % 360.0
    raise ValueError(f"Unsupported chart division: {division}")


def _chart_point(
    *,
    name: str,
    kind: str,
    source_longitude: float,
    division: int,
    ascendant_sign_index: int,
    retrograde: bool | None,
) -> ChartPoint:
    chart_longitude = _chart_longitude(source_longitude, division)
    sign_index = int(chart_longitude // 30.0) + 1

    return ChartPoint(
        name=name,
        kind=kind,
        source_longitude=round(source_longitude % 360.0, 8),
        chart_longitude=round(chart_longitude, 8),
        sign_index=sign_index,
        sign=SIGNS[sign_index - 1],
        degree_in_sign=round(chart_longitude % 30.0, 8),
        house=((sign_index - ascendant_sign_index) % 12) + 1,
        retrograde=retrograde,
    )


def calculate_chart(request: ChartRequest, chart_type: ChartType) -> ChartResponse:
    """Calculate a D1 Rasi or D9 Navamsa chart from Lahiri positions."""

    division = 1 if chart_type == ChartType.D1_RASI else 9
    positions = calculate_positions(
        PositionsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )

    ascendant_chart_longitude = _chart_longitude(
        positions.ascendant.longitude,
        division,
    )
    ascendant_sign_index = int(ascendant_chart_longitude // 30.0) + 1
    ascendant = _chart_point(
        name="ascendant",
        kind="ascendant",
        source_longitude=positions.ascendant.longitude,
        division=division,
        ascendant_sign_index=ascendant_sign_index,
        retrograde=None,
    )

    points: list[ChartPoint] = []
    for planet in positions.planets:
        kind = "node" if planet.body in {"rahu", "ketu"} else "planet"
        points.append(
            _chart_point(
                name=planet.body,
                kind=kind,
                source_longitude=planet.longitude,
                division=division,
                ascendant_sign_index=ascendant_sign_index,
                retrograde=planet.retrograde,
            )
        )

    occupants: dict[int, list[str]] = {index: [] for index in range(1, 13)}
    occupants[ascendant.sign_index].append(ascendant.name)
    for point in points:
        occupants[point.sign_index].append(point.name)

    signs = [
        SouthIndianSignCell(
            sign_index=sign_index,
            sign=SIGNS[sign_index - 1],
            grid_row=SOUTH_INDIAN_GRID[sign_index][0],
            grid_column=SOUTH_INDIAN_GRID[sign_index][1],
            house_from_lagna=((sign_index - ascendant_sign_index) % 12) + 1,
            occupants=occupants[sign_index],
        )
        for sign_index in range(1, 13)
    ]

    return ChartResponse(
        request_id=f"req_{uuid4().hex}",
        chart_type=chart_type,
        division=division,
        calculation_profile=request.calculation_profile,
        time=positions.time,
        coordinates=positions.coordinates,
        ayanamsha_degrees=positions.ayanamsha_degrees,
        ascendant=ascendant,
        points=points,
        signs=signs,
        metadata=positions.metadata.model_copy(
            update={"house_system": "whole_sign_divisional"}
        ),
    )
