"""Side-by-side comparison of Swiss and Skyfield/JPL position profiles."""

from uuid import uuid4

from app.engine.positions import calculate_positions
from app.schemas.positions import CalculationProfile, PositionsRequest
from app.schemas.provider_comparison import (
    ProviderComparisonRequest,
    ProviderComparisonResponse,
    ProviderPointComparison,
    ScalarAngularComparison,
)

_SWISS_PROFILE = CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
_SKYFIELD_PROFILE = (
    CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_SKYFIELD_DE440S_V1
)


def _signed_angular_difference(later: float, earlier: float) -> float:
    return (later - earlier + 180.0) % 360.0 - 180.0


def _angular_comparison(
    swiss_value: float,
    skyfield_value: float,
    tolerance: float,
) -> ScalarAngularComparison:
    signed_difference = _signed_angular_difference(skyfield_value, swiss_value)
    absolute_difference = abs(signed_difference)
    return ScalarAngularComparison(
        swiss_value=round(swiss_value, 8),
        skyfield_value=round(skyfield_value, 8),
        signed_difference_degrees=round(signed_difference, 8),
        absolute_difference_degrees=round(absolute_difference, 8),
        tolerance_degrees=tolerance,
        matched=absolute_difference <= tolerance,
    )


def compare_position_providers(
    request: ProviderComparisonRequest,
) -> ProviderComparisonResponse:
    """Calculate both immutable profiles and report every migration difference."""

    swiss = calculate_positions(
        PositionsRequest(birth=request.birth, calculation_profile=_SWISS_PROFILE)
    )
    skyfield = calculate_positions(
        PositionsRequest(birth=request.birth, calculation_profile=_SKYFIELD_PROFILE)
    )

    skyfield_by_body = {planet.body: planet for planet in skyfield.planets}
    point_comparisons: list[ProviderPointComparison] = []
    for swiss_planet in swiss.planets:
        skyfield_planet = skyfield_by_body[swiss_planet.body]
        point_comparisons.append(
            ProviderPointComparison(
                body=swiss_planet.body,
                longitude=_angular_comparison(
                    swiss_planet.longitude,
                    skyfield_planet.longitude,
                    request.longitude_tolerance_degrees,
                ),
                swiss_sign_index=swiss_planet.sign_index,
                skyfield_sign_index=skyfield_planet.sign_index,
                sign_matched=swiss_planet.sign_index == skyfield_planet.sign_index,
                swiss_retrograde=swiss_planet.retrograde,
                skyfield_retrograde=skyfield_planet.retrograde,
                retrograde_matched=(
                    swiss_planet.retrograde == skyfield_planet.retrograde
                ),
            )
        )

    ayanamsha = _angular_comparison(
        swiss.ayanamsha_degrees,
        skyfield.ayanamsha_degrees,
        request.ayanamsha_tolerance_degrees,
    )
    ascendant = _angular_comparison(
        swiss.ascendant.longitude,
        skyfield.ascendant.longitude,
        request.ascendant_tolerance_degrees,
    )
    longitude_matches = sum(item.longitude.matched for item in point_comparisons)
    sign_matches = sum(item.sign_matched for item in point_comparisons)
    retrograde_matches = sum(item.retrograde_matched for item in point_comparisons)
    passed = (
        ayanamsha.matched
        and ascendant.matched
        and longitude_matches == len(point_comparisons)
        and sign_matches == len(point_comparisons)
        and retrograde_matches == len(point_comparisons)
    )

    return ProviderComparisonResponse(
        request_id=f"cmp_{uuid4().hex}",
        swiss_profile=_SWISS_PROFILE,
        skyfield_profile=_SKYFIELD_PROFILE,
        swiss_metadata=swiss.metadata,
        skyfield_metadata=skyfield.metadata,
        ayanamsha=ayanamsha,
        ascendant=ascendant,
        points=point_comparisons,
        compared_point_count=len(point_comparisons),
        longitude_match_count=longitude_matches,
        sign_match_count=sign_matches,
        retrograde_match_count=retrograde_matches,
        passed=passed,
        production_default_changed=False,
        caveats=[
            "This endpoint reports differences and never changes the active default profile.",
            "Outer planets use JPL planetary barycenters where DE440s provides them.",
            "Rahu is an osculating lunar ascending node derived from the JPL lunar state.",
            "Panchanga sunrise and sunset have not yet been migrated to Skyfield.",
        ],
    )
