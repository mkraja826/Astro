"""Apply a transparent API weighting convention to raw classical strength facts."""

from uuid import uuid4

from app.engine.classical_reference import PROFILE_ID
from app.engine.classical_strength import calculate_varahamihira_strength
from app.schemas.classical_conditions import DignityState
from app.schemas.classical_relationships import CompoundRelationship
from app.schemas.classical_strength import (
    ClassicalStrengthRequest,
    ClassicalStrengthResponse,
    GrahaStrengthAssessment,
)
from app.schemas.classical_weighting import (
    ClassicalWeightedStrengthRequest,
    ClassicalWeightedStrengthResponse,
    CompactStrengthSnapshot,
    WeightedGrahaStrength,
    WeightingComponent,
    WeightingProfileId,
    WeightingProfileResponse,
    WeightingSourceStatus,
)

WEIGHTING_PROFILE_ID = WeightingProfileId.TRANSPARENT_STRENGTH_WEIGHTING_V1
WEIGHTING_VERSION = "1.0.0"

DIGNITY_WEIGHTS = {
    DignityState.EXALTATION_SIGN.value: 4.0,
    DignityState.OWN_SIGN.value: 3.0,
    DignityState.ORDINARY.value: 0.0,
    DignityState.DEBILITATION_SIGN.value: -4.0,
}
DEEP_DIGNITY_WEIGHTS = {
    "deep_exaltation": 1.0,
    "none": 0.0,
    "deep_debilitation": -1.0,
}
VARGOTTAMA_WEIGHT = 2.0
RELATIONSHIP_WEIGHTS = {
    CompoundRelationship.GREAT_FRIEND.value: 2.0,
    CompoundRelationship.FRIEND.value: 1.0,
    CompoundRelationship.NEUTRAL.value: 0.0,
    CompoundRelationship.ENEMY.value: -1.0,
    CompoundRelationship.GREAT_ENEMY.value: -2.0,
    "self": 0.0,
}

_GOLDEN_FIXTURE_IDS = [
    "exalted_vargottama_friendly",
    "debilitated_hostile",
    "own_sign_neutral_context",
]
_GRAHA_ORDER = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _rule_ids(assessment: GrahaStrengthAssessment, factor_id: str) -> list[str]:
    for factor in assessment.factors:
        if factor.factor_id == factor_id:
            return list(factor.rule_ids)
    return []


def _dignity_factor_id(assessment: GrahaStrengthAssessment) -> str:
    return {
        DignityState.EXALTATION_SIGN: "dignity_exaltation_sign",
        DignityState.OWN_SIGN: "dignity_own_sign",
        DignityState.ORDINARY: "dignity_ordinary",
        DignityState.DEBILITATION_SIGN: "dignity_debilitation_sign",
    }[assessment.dignity]


def _component(
    component_id: str,
    raw_value: str,
    contribution: float,
    formula: str,
    rule_ids: list[str],
    reason: str,
) -> WeightingComponent:
    return WeightingComponent(
        component_id=component_id,
        raw_value=raw_value,
        contribution=round(contribution, 6),
        formula=formula,
        classical_rule_ids=rule_ids,
        convention_profile=WEIGHTING_PROFILE_ID,
        reason=reason,
    )


def weight_assessment(
    assessment: GrahaStrengthAssessment,
) -> tuple[list[WeightingComponent], float, list[str]]:
    """Return component contributions, total score, and score-neutral factor IDs."""

    dignity_value = assessment.dignity.value
    dignity_contribution = DIGNITY_WEIGHTS[dignity_value]
    dignity_factor_id = _dignity_factor_id(assessment)

    if assessment.at_deep_exaltation_point:
        deep_value = "deep_exaltation"
        deep_factor_id = "deep_exaltation_point"
    elif assessment.at_deep_debilitation_point:
        deep_value = "deep_debilitation"
        deep_factor_id = "deep_debilitation_point"
    else:
        deep_value = "none"
        deep_factor_id = ""
    deep_contribution = DEEP_DIGNITY_WEIGHTS[deep_value]

    relationship = assessment.sign_lord_relationship
    relationship_value = (
        "self"
        if relationship.self_relationship
        else relationship.compound_relationship.value
    )
    relationship_contribution = RELATIONSHIP_WEIGHTS[relationship_value]

    bav = assessment.bhinnashtakavarga_bindus_in_occupied_sign
    bav_contribution = (bav - 4) * 0.5
    sav = assessment.sarvashtakavarga_bindus_in_occupied_sign
    sav_contribution = _clamp((sav - 28) / 7, -2.0, 2.0)

    components = [
        _component(
            "dignity",
            dignity_value,
            dignity_contribution,
            "lookup(dignity_weights, dignity)",
            _rule_ids(assessment, dignity_factor_id),
            "Dignity receives a fixed convention contribution.",
        ),
        _component(
            "deep_dignity",
            deep_value,
            deep_contribution,
            "lookup(deep_dignity_weights, deep_dignity)",
            _rule_ids(assessment, deep_factor_id) if deep_factor_id else [],
            "Only the exact registered deep point receives this adjustment.",
        ),
        _component(
            "vargottama",
            str(assessment.vargottama).lower(),
            VARGOTTAMA_WEIGHT if assessment.vargottama else 0.0,
            "2.0 if vargottama else 0.0",
            _rule_ids(assessment, "vargottama"),
            "Vargottama receives a fixed convention contribution.",
        ),
        _component(
            "occupied_sign_lord_relationship",
            relationship_value,
            relationship_contribution,
            "lookup(relationship_weights, compound_relationship)",
            list(relationship.rule_ids),
            "The directional relationship to the occupied-sign lord is weighted.",
        ),
        _component(
            "bhinnashtakavarga",
            str(bav),
            bav_contribution,
            "(bindus - 4) * 0.5",
            _rule_ids(assessment, "bhinnashtakavarga_raw"),
            "Four bindus is the convention midpoint; each bindu changes 0.5.",
        ),
        _component(
            "sarvashtakavarga",
            str(sav),
            sav_contribution,
            "clamp((bindus - 28) / 7, -2.0, 2.0)",
            _rule_ids(assessment, "sarvashtakavarga_raw"),
            "Twenty-eight bindus is the convention midpoint with a capped adjustment.",
        ),
    ]

    weighted_factor_ids = {
        dignity_factor_id,
        "occupied_sign_lord_relationship",
        "bhinnashtakavarga_raw",
        "sarvashtakavarga_raw",
    }
    if deep_factor_id:
        weighted_factor_ids.add(deep_factor_id)
    if assessment.vargottama:
        weighted_factor_ids.add("vargottama")

    neutral_context = [
        factor.factor_id
        for factor in assessment.factors
        if factor.factor_id not in weighted_factor_ids
    ]
    total = round(sum(component.contribution for component in components), 6)
    return components, total, neutral_context


def apply_controlled_weighting(
    raw_strength: ClassicalStrengthResponse,
) -> list[WeightedGrahaStrength]:
    """Apply the immutable convention and assign deterministic competition ranks."""

    interim: list[tuple[GrahaStrengthAssessment, list[WeightingComponent], float, list[str]]] = []
    for assessment in raw_strength.grahas:
        components, total, neutral_context = weight_assessment(assessment)
        interim.append((assessment, components, total, neutral_context))

    order_index = {graha: index for index, graha in enumerate(_GRAHA_ORDER)}
    sorted_items = sorted(interim, key=lambda item: (-item[2], order_index[item[0].graha]))
    rank_by_graha: dict[str, int] = {}
    previous_score: float | None = None
    previous_rank = 0
    for index, (assessment, _, total, _) in enumerate(sorted_items, start=1):
        if previous_score is None or total != previous_score:
            previous_rank = index
            previous_score = total
        rank_by_graha[assessment.graha] = previous_rank

    scores = {assessment.graha: total for assessment, _, total, _ in interim}
    results = []
    for assessment, components, total, neutral_context in interim:
        tied_with = sorted(
            graha for graha, score in scores.items() if graha != assessment.graha and score == total
        )
        results.append(
            WeightedGrahaStrength(
                graha=assessment.graha,
                total_score=total,
                rank=rank_by_graha[assessment.graha],
                tied_with=tied_with,
                components=components,
                neutral_context_factor_ids=neutral_context,
                cancellation_adjustment=0.0,
                cancellation_applied=False,
            )
        )
    return results


def compact_strength_snapshot(
    graha: str,
    weighted_lookup: dict[str, WeightedGrahaStrength],
) -> CompactStrengthSnapshot:
    """Return an embeddable summary while preserving the seven-Graha boundary."""

    result = weighted_lookup.get(graha)
    if result is None:
        return CompactStrengthSnapshot(
            graha=graha,
            available=False,
            tied_with=[],
            reason="Controlled weighting is available only for the seven classical Grahas.",
        )
    return CompactStrengthSnapshot(
        graha=graha,
        available=True,
        weighting_profile=WEIGHTING_PROFILE_ID,
        total_score=result.total_score,
        rank=result.rank,
        tied_with=list(result.tied_with),
        reason=(
            "This is a transparent API convention score, not a classical textual strength."
        ),
    )


def get_weighting_profile() -> WeightingProfileResponse:
    """Return immutable metadata for the controlled weighting convention."""

    return WeightingProfileResponse(
        weighting_profile=WEIGHTING_PROFILE_ID,
        version=WEIGHTING_VERSION,
        source_status=WeightingSourceStatus.API_CONVENTION_NOT_TEXTUAL_RULE,
        classical_profile_dependency=PROFILE_ID,
        calculation_profile_dependency="south_indian_drik_lahiri_v1",
        dignity_weights=dict(DIGNITY_WEIGHTS),
        deep_dignity_weights=dict(DEEP_DIGNITY_WEIGHTS),
        vargottama_weight=VARGOTTAMA_WEIGHT,
        relationship_weights=dict(RELATIONSHIP_WEIGHTS),
        bhinnashtakavarga_formula="(bindus - 4) * 0.5",
        sarvashtakavarga_formula="clamp((bindus - 28) / 7, -2.0, 2.0)",
        score_neutral_factors=[
            "retrograde",
            "resolved_tendency",
            "aspects_received_raw",
            "conjunctions_raw",
            "cancellation",
        ],
        cancellation_adjustment_enabled=False,
        golden_fixture_ids=list(_GOLDEN_FIXTURE_IDS),
        golden_fixture_count=len(_GOLDEN_FIXTURE_IDS),
        external_reference_validation_complete=False,
        caveats=[
            "Weights are an API convention and are not attributed to Brihat Jataka.",
            "Scores compare only the seven classical Grahas within one natal chart.",
            "No cancellation adjustment is applied.",
            "External multi-software golden-chart validation remains incomplete.",
            "No event, profession, health, relationship, or longevity result is predicted.",
        ],
    )


def calculate_varahamihira_weighted_strength(
    request: ClassicalWeightedStrengthRequest,
) -> ClassicalWeightedStrengthResponse:
    """Return raw strength evidence plus the selected controlled convention."""

    raw = calculate_varahamihira_strength(
        ClassicalStrengthRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    weighted = apply_controlled_weighting(raw)
    highest = [item.graha for item in weighted if item.rank == 1]
    return ClassicalWeightedStrengthResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        weighting_profile=request.weighting_profile,
        weighting_version=WEIGHTING_VERSION,
        calculation_profile=request.calculation_profile,
        time=raw.time,
        coordinates=raw.coordinates,
        ayanamsha_degrees=raw.ayanamsha_degrees,
        raw_strength=raw,
        weighted_grahas=weighted,
        highest_ranked_grahas=highest,
        excluded_points=["rahu", "ketu"],
        weights_applied=True,
        ranking_applied=True,
        cancellations_applied=False,
        prediction_applied=False,
        metadata=raw.metadata,
        caveats=[
            "Scores are convention outputs, not quotations or universal classical facts.",
            "Raw factors remain embedded and should be shown beside every score.",
            "Rahu and Ketu are not ranked by this seven-Graha convention.",
            "Cancellations and predictive outcomes are not applied.",
            "External golden-chart validation is still incomplete.",
        ],
    )
