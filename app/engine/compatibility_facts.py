"""Assemble anonymous dual-chart compatibility calculation facts."""

from __future__ import annotations

from uuid import uuid4

from app.engine.compatibility_contract import compatibility_request_fingerprints
from app.engine.compatibility_directional_rules import (
    evaluate_ashtakoota_components,
    summarize_ashtakoota_coverage,
)
from app.engine.positions import calculate_positions
from app.schemas.compatibility import (
    COMPATIBILITY_FACTS_VERSION,
    COMPATIBILITY_PROFILE,
    CompatibilityFactsResponse,
    CompatibilityNatalFacts,
    DualChartCompatibilityRequest,
)
from app.schemas.positions import PositionsRequest, PositionsResponse

COMPATIBILITY_ASSEMBLER_RULE_ID = "ASTRO-COMPATIBILITY-FACTS-ASSEMBLER-001"


def _natal_facts(
    positions: PositionsResponse,
    chart_fingerprint: str,
) -> CompatibilityNatalFacts:
    moon = next((item for item in positions.planets if item.body == "moon"), None)
    if moon is None:
        raise ValueError("positions response is missing the Moon")

    planet_sign_indices = {
        item.body: item.sign_index
        for item in positions.planets
        if item.body not in {"rahu", "ketu"}
    }
    return CompatibilityNatalFacts(
        chart_fingerprint=chart_fingerprint,
        ascendant_sign_index=positions.ascendant.sign_index,
        moon_sign_index=moon.sign_index,
        moon_degree_in_sign=moon.degree_in_sign,
        moon_nakshatra_index=moon.nakshatra_index,
        moon_nakshatra=moon.nakshatra,
        moon_pada=moon.pada,
        planet_sign_indices=planet_sign_indices,
    )


def _validate_matching_provenance(
    subject: PositionsResponse,
    partner: PositionsResponse,
) -> None:
    if subject.calculation_profile is not partner.calculation_profile:
        raise ValueError("dual-chart calculations used different calculation profiles")
    if subject.metadata.model_dump(mode="json") != partner.metadata.model_dump(mode="json"):
        raise ValueError("dual-chart calculations used different engine provenance")


def calculate_compatibility_facts(
    request: DualChartCompatibilityRequest,
) -> CompatibilityFactsResponse:
    """Calculate both natal charts and return non-interpretive compatibility facts."""

    subject_positions = calculate_positions(
        PositionsRequest(
            birth=request.subject_birth,
            calculation_profile=request.calculation_profile,
        )
    )
    partner_positions = calculate_positions(
        PositionsRequest(
            birth=request.partner_birth,
            calculation_profile=request.calculation_profile,
        )
    )
    _validate_matching_provenance(subject_positions, partner_positions)

    subject_fingerprint, partner_fingerprint, pair_fingerprint = (
        compatibility_request_fingerprints(request)
    )
    subject = _natal_facts(subject_positions, subject_fingerprint)
    partner = _natal_facts(partner_positions, partner_fingerprint)
    components = evaluate_ashtakoota_components(
        subject,
        partner,
        subject_role=request.subject_role,
        partner_role=request.partner_role,
    )
    achieved_points, evaluated_maximum, complete = summarize_ashtakoota_coverage(
        components
    )

    caveats = [
        "These are traditional calculation facts, not a probability or marriage outcome.",
        "Manglik/Kuja factors are not included in this assembler version.",
    ]
    if not complete:
        caveats.append(
            "Directional components abstained because explicit bride/groom roles were absent."
        )

    rule_ids = [COMPATIBILITY_ASSEMBLER_RULE_ID]
    for component in components:
        rule_ids.extend(component.rule_ids)

    return CompatibilityFactsResponse(
        request_id=f"compat_{uuid4().hex}",
        facts_version=COMPATIBILITY_FACTS_VERSION,
        calculation_profile=request.calculation_profile,
        compatibility_profile=COMPATIBILITY_PROFILE,
        subject_fingerprint=subject_fingerprint,
        partner_fingerprint=partner_fingerprint,
        pair_fingerprint=pair_fingerprint,
        subject=subject,
        partner=partner,
        ashtakoota_components=list(components),
        total_achieved_points=achieved_points,
        evaluated_maximum_points=evaluated_maximum,
        complete_36_point_evaluation=complete,
        subject_manglik_factors=[],
        partner_manglik_factors=[],
        rule_ids=list(dict.fromkeys(rule_ids)),
        metadata=subject_positions.metadata,
        caveats=caveats,
    )
