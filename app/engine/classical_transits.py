"""Evaluate raw Chapter 9 transit balances without domain prediction."""

from uuid import uuid4

from app.engine.classical_ashtakavarga import calculate_varahamihira_ashtakavarga
from app.engine.classical_reference import PROFILE_ID
from app.engine.transits import calculate_transit_snapshot
from app.schemas.classical_ashtakavarga import AshtakavargaRequest
from app.schemas.classical_transits import (
    ClassicalTransitEvaluationRequest,
    ClassicalTransitEvaluationResponse,
    ClassicalTransitFactor,
    TransitPolarity,
)

_TRANSIT_BALANCE_RULE_ID = "VM-BJ-C09-TRANSIT-BAV-BALANCE-001"


def calculate_varahamihira_transit_evaluation(
    request: ClassicalTransitEvaluationRequest,
) -> ClassicalTransitEvaluationResponse:
    """Evaluate benefic-dot versus complementary-line balance at one instant."""

    snapshot = calculate_transit_snapshot(request)
    ashtakavarga = calculate_varahamihira_ashtakavarga(
        AshtakavargaRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    relation_by_body = {item.body: item for item in snapshot.relations}
    bav_by_body = {
        record.graha: record for record in ashtakavarga.bhinnashtakavargas
    }

    factors: list[ClassicalTransitFactor] = []
    for point in snapshot.transit.planets:
        bav = bav_by_body.get(point.body)
        if bav is None:
            continue
        relation = relation_by_body[point.body]
        bindus = bav.bindus_by_sign[point.sign_index - 1]
        rekhas = 8 - bindus
        net_eighths = bindus - rekhas
        polarity = (
            TransitPolarity.SUPPORTING
            if net_eighths > 0
            else TransitPolarity.CHALLENGING
            if net_eighths < 0
            else TransitPolarity.CONTEXTUAL
        )
        factors.append(
            ClassicalTransitFactor(
                body=point.body,
                transit_sign_index=point.sign_index,
                house_from_natal_ascendant=(
                    relation.whole_sign_house_from_natal_ascendant
                ),
                house_from_natal_moon=relation.whole_sign_house_from_natal_moon,
                bindus=bindus,
                rekhas=rekhas,
                net_eighths=net_eighths,
                normalized_balance=round(net_eighths / 8.0, 6),
                polarity=polarity,
                rule_ids=[*bav.rule_ids, _TRANSIT_BALANCE_RULE_ID],
                reason=(
                    f"{point.body.title()} transits a sign containing {bindus}/8 "
                    f"benefic dots and {rekhas}/8 complementary lines in its natal "
                    "Bhinnashtakavarga. The direction follows their arithmetic balance."
                ),
            )
        )

    return ClassicalTransitEvaluationResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        snapshot=snapshot,
        factors=factors,
        interpretation_applied=True,
        domain_prediction_applied=False,
        timing_window_applied=False,
        excluded_points=["rahu", "ketu"],
        caveats=[
            "Only the seven classical Grahas have Chapter 9 Bhinnashtakavarga tables.",
            "A balance is planet-specific and is not yet a life-domain forecast.",
            "No Upachaya override, reduction, Dasha combination, or event claim is applied.",
        ],
    )
