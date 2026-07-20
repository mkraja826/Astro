"""Compose transparent, unweighted strength factors from validated calculators."""

from uuid import uuid4

from app.engine.classical_ashtakavarga import calculate_varahamihira_ashtakavarga
from app.engine.classical_aspects import calculate_varahamihira_aspects
from app.engine.classical_conditions import calculate_varahamihira_conditions
from app.engine.classical_reference import PROFILE_ID, get_varahamihira_rashis
from app.engine.classical_relationships import calculate_varahamihira_relationships
from app.schemas.classical_ashtakavarga import AshtakavargaRequest
from app.schemas.classical_aspects import ClassicalAspectsRequest
from app.schemas.classical_conditions import ClassicalConditionsRequest, DignityState
from app.schemas.classical_relationships import (
    ClassicalRelationshipsRequest,
    CompoundRelationship,
)
from app.schemas.classical_strength import (
    CancellationEvaluation,
    CancellationPolicy,
    CancellationStatus,
    ClassicalStrengthRequest,
    ClassicalStrengthResponse,
    GrahaStrengthAssessment,
    SignLordRelationshipSnapshot,
    StrengthFactor,
    StrengthFactorCategory,
)

_STRENGTH_RULE_ID = "VM-BJ-C02-STRENGTH-FACTOR-FRAMEWORK-001"
_BINDU_RULE_ID = "VM-BJ-C09-STRENGTH-BINDU-CONTEXT-001"
_CANCELLATION_RULE_ID = "VM-BJ-C02-CANCELLATION-SOURCE-BOUNDARY-001"

_UNSUPPORTED_CANCELLATION_CONVENTIONS = [
    "neecha_bhanga_sign_lord_in_kendra",
    "neecha_bhanga_exaltation_lord_in_kendra",
    "neecha_bhanga_debilitated_planet_in_kendra",
    "neecha_bhanga_sign_exchange",
]


def _factor(
    factor_id: str,
    category: StrengthFactorCategory,
    value: str,
    reason: str,
    rule_ids: list[str],
) -> StrengthFactor:
    return StrengthFactor(
        factor_id=factor_id,
        category=category,
        value=value,
        reason=reason,
        rule_ids=rule_ids,
        numeric_weight=None,
    )


def _dignity_factors(condition: object) -> list[StrengthFactor]:
    factors: list[StrengthFactor] = []
    dignity = condition.dignity
    if dignity == DignityState.EXALTATION_SIGN:
        factors.append(
            _factor(
                "dignity_exaltation_sign",
                StrengthFactorCategory.SUPPORTING,
                condition.d1_sign,
                f"{condition.graha} occupies its registered exaltation sign.",
                ["VM-BJ-C02-DIGNITY-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    elif dignity == DignityState.OWN_SIGN:
        factors.append(
            _factor(
                "dignity_own_sign",
                StrengthFactorCategory.SUPPORTING,
                condition.d1_sign,
                f"{condition.graha} occupies a sign it owns.",
                ["VM-BJ-C01-OWN-SIGN-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    elif dignity == DignityState.DEBILITATION_SIGN:
        factors.append(
            _factor(
                "dignity_debilitation_sign",
                StrengthFactorCategory.CHALLENGING,
                condition.d1_sign,
                f"{condition.graha} occupies its registered debilitation sign.",
                ["VM-BJ-C02-DIGNITY-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    else:
        factors.append(
            _factor(
                "dignity_ordinary",
                StrengthFactorCategory.CONTEXTUAL,
                condition.d1_sign,
                f"{condition.graha} has no exaltation, debilitation, or own-sign flag.",
                ["VM-BJ-C02-DIGNITY-EVAL-001", _STRENGTH_RULE_ID],
            )
        )

    if condition.at_deep_exaltation_point:
        factors.append(
            _factor(
                "deep_exaltation_point",
                StrengthFactorCategory.SUPPORTING,
                "true",
                f"{condition.graha} is at its registered deep-exaltation degree.",
                ["VM-BJ-C02-DIGNITY-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    if condition.at_deep_debilitation_point:
        factors.append(
            _factor(
                "deep_debilitation_point",
                StrengthFactorCategory.CHALLENGING,
                "true",
                f"{condition.graha} is at its registered deep-debilitation degree.",
                ["VM-BJ-C02-DIGNITY-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    if condition.vargottama:
        factors.append(
            _factor(
                "vargottama",
                StrengthFactorCategory.SUPPORTING,
                "true",
                f"{condition.graha} occupies the same sign in D1 and D9.",
                ["VM-BJ-C01-VARGOTTAMA-EVAL-001", _STRENGTH_RULE_ID],
            )
        )
    if condition.retrograde:
        factors.append(
            _factor(
                "retrograde",
                StrengthFactorCategory.CONTEXTUAL,
                "true",
                (
                    f"{condition.graha} is retrograde; this framework records the fact "
                    "without assigning a strength direction or weight."
                ),
                [_STRENGTH_RULE_ID],
            )
        )
    factors.append(
        _factor(
            "resolved_tendency",
            StrengthFactorCategory.CONTEXTUAL,
            condition.resolved_tendency.value,
            condition.tendency_reason,
            [_STRENGTH_RULE_ID],
        )
    )
    return factors


def _relationship_factor(
    graha: str,
    sign_lord: str,
    relationship: object | None,
) -> tuple[SignLordRelationshipSnapshot, StrengthFactor]:
    if graha == sign_lord:
        snapshot = SignLordRelationshipSnapshot(
            sign_lord=sign_lord,
            self_relationship=True,
            rule_ids=[_STRENGTH_RULE_ID],
        )
        factor = _factor(
            "occupied_sign_lord_relationship",
            StrengthFactorCategory.CONTEXTUAL,
            "self",
            f"{graha} is the lord of its occupied sign; no self-relationship is created.",
            [_STRENGTH_RULE_ID],
        )
        return snapshot, factor

    if relationship is None:
        raise RuntimeError("Missing directed relationship to occupied sign lord")

    compound = relationship.compound_relationship
    if compound in {CompoundRelationship.GREAT_FRIEND, CompoundRelationship.FRIEND}:
        category = StrengthFactorCategory.SUPPORTING
    elif compound in {CompoundRelationship.GREAT_ENEMY, CompoundRelationship.ENEMY}:
        category = StrengthFactorCategory.CHALLENGING
    else:
        category = StrengthFactorCategory.CONTEXTUAL

    snapshot = SignLordRelationshipSnapshot(
        sign_lord=sign_lord,
        natural_relationship=relationship.natural_relationship,
        temporary_relationship=relationship.temporary_relationship,
        compound_relationship=compound,
        self_relationship=False,
        rule_ids=list(relationship.rule_ids),
    )
    factor = _factor(
        "occupied_sign_lord_relationship",
        category,
        compound.value,
        (
            f"The directional compound relationship from {graha} to occupied-sign "
            f"lord {sign_lord} is {compound.value}."
        ),
        [*relationship.rule_ids, _STRENGTH_RULE_ID],
    )
    return snapshot, factor


def _cancellation(condition: object) -> CancellationEvaluation:
    if not condition.in_debilitation_sign:
        return CancellationEvaluation(
            candidate_id="debilitation_cancellation",
            status=CancellationStatus.NOT_APPLICABLE,
            applicable=False,
            cancellation_applied=False,
            reason=f"{condition.graha} is not in its registered debilitation sign.",
            unsupported_conventions=[],
        )

    return CancellationEvaluation(
        candidate_id="debilitation_cancellation",
        status=CancellationStatus.UNSUPPORTED_BY_PROFILE,
        applicable=True,
        cancellation_applied=False,
        source_rule_id=None,
        reason=(
            "The current varahamihira_v1 registry contains no verse-level "
            "debilitation-cancellation rule. Later or cross-text conventions are not "
            "imported silently."
        ),
        unsupported_conventions=list(_UNSUPPORTED_CANCELLATION_CONVENTIONS),
    )


def calculate_varahamihira_strength(
    request: ClassicalStrengthRequest,
) -> ClassicalStrengthResponse:
    """Return unweighted strength factors and explicit cancellation boundaries."""

    conditions = calculate_varahamihira_conditions(
        ClassicalConditionsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    relationships = calculate_varahamihira_relationships(
        ClassicalRelationshipsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    aspects = calculate_varahamihira_aspects(
        ClassicalAspectsRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    ashtakavarga = calculate_varahamihira_ashtakavarga(
        AshtakavargaRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )

    rashis = {rashi.index: rashi for rashi in get_varahamihira_rashis().rashis}
    directed = {
        (item.source_graha, item.target_graha): item
        for item in relationships.directed_relationships
    }
    house_by_sign = {house.sign_index: house for house in aspects.houses}
    bav_by_graha = {
        record.graha: record for record in ashtakavarga.bhinnashtakavargas
    }
    sav_by_sign = {
        record.sign_index: record
        for record in ashtakavarga.sarvashtakavarga.signs
    }

    assessments: list[GrahaStrengthAssessment] = []
    for condition in conditions.grahas:
        rashi = rashis[condition.d1_sign_index]
        sign_lord = rashi.lord
        relationship = directed.get((condition.graha, sign_lord))
        relationship_snapshot, relationship_factor = _relationship_factor(
            condition.graha,
            sign_lord,
            relationship,
        )
        house = house_by_sign[condition.d1_sign_index]
        conjunctions = sorted(
            {
                graha
                for pair in house.conjunction_pairs
                if condition.graha in pair
                for graha in pair
                if graha != condition.graha
            }
        )
        bav = bav_by_graha[condition.graha]
        bav_bindus = bav.bindus_by_sign[condition.d1_sign_index - 1]
        sav_bindus = sav_by_sign[
            condition.d1_sign_index
        ].sarvashtakavarga_bindus
        full_aspects = len(house.full_aspect_sources)

        factors = _dignity_factors(condition)
        factors.append(relationship_factor)
        factors.extend(
            [
                _factor(
                    "bhinnashtakavarga_raw",
                    StrengthFactorCategory.CONTEXTUAL,
                    str(bav_bindus),
                    (
                        f"{condition.graha}'s raw Bhinnashtakavarga gives "
                        f"{bav_bindus} bindus to {condition.d1_sign}."
                    ),
                    [*bav.rule_ids, _BINDU_RULE_ID],
                ),
                _factor(
                    "sarvashtakavarga_raw",
                    StrengthFactorCategory.CONTEXTUAL,
                    str(sav_bindus),
                    (
                        f"The occupied sign {condition.d1_sign} has {sav_bindus} raw "
                        "Sarvashtakavarga bindus."
                    ),
                    [_BINDU_RULE_ID],
                ),
                _factor(
                    "aspects_received_raw",
                    StrengthFactorCategory.CONTEXTUAL,
                    str(round(house.total_aspect_weight, 8)),
                    (
                        f"The occupied sign receives {len(house.aspects_received)} aspect "
                        f"rays with total fractional weight {house.total_aspect_weight}."
                    ),
                    [*house.rule_ids, _STRENGTH_RULE_ID],
                ),
                _factor(
                    "conjunctions_raw",
                    StrengthFactorCategory.CONTEXTUAL,
                    ",".join(conjunctions) if conjunctions else "none",
                    (
                        f"Same-sign classical co-occupants for {condition.graha} are "
                        f"{', '.join(conjunctions) if conjunctions else 'none'}."
                    ),
                    [*house.rule_ids, _STRENGTH_RULE_ID],
                ),
            ]
        )

        assessments.append(
            GrahaStrengthAssessment(
                graha=condition.graha,
                source_longitude=condition.source_longitude,
                d1_sign_index=condition.d1_sign_index,
                d1_sign=condition.d1_sign,
                d1_degree_in_sign=condition.d1_degree_in_sign,
                d1_house=condition.d1_house,
                dignity=condition.dignity,
                own_sign=condition.own_sign,
                in_exaltation_sign=condition.in_exaltation_sign,
                at_deep_exaltation_point=condition.at_deep_exaltation_point,
                in_debilitation_sign=condition.in_debilitation_sign,
                at_deep_debilitation_point=condition.at_deep_debilitation_point,
                vargottama=condition.vargottama,
                retrograde=condition.retrograde,
                resolved_tendency=condition.resolved_tendency,
                occupied_sign_lord=sign_lord,
                sign_lord_relationship=relationship_snapshot,
                bhinnashtakavarga_bindus_in_occupied_sign=bav_bindus,
                sarvashtakavarga_bindus_in_occupied_sign=sav_bindus,
                full_aspects_received=full_aspects,
                total_fractional_aspect_weight_received=round(
                    house.total_aspect_weight,
                    8,
                ),
                conjunctions=conjunctions,
                factors=factors,
                cancellation=_cancellation(condition),
            )
        )

    return ClassicalStrengthResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=conditions.time,
        coordinates=conditions.coordinates,
        ayanamsha_degrees=conditions.ayanamsha_degrees,
        grahas=assessments,
        cancellation_policy=CancellationPolicy(
            policy_id="varahamihira_v1_source_strict_cancellation_policy",
            confirmed_rule_count=0,
            cancellation_rules_enabled=False,
            supported_rule_ids=[],
            unsupported_conventions=list(_UNSUPPORTED_CANCELLATION_CONVENTIONS),
            reason=(
                "No verse-level cancellation formula is registered in varahamihira_v1. "
                "A future cross-text profile may add separately versioned rules."
            ),
        ),
        excluded_points=["rahu", "ketu"],
        weights_applied=False,
        ranking_applied=False,
        cancellations_applied=False,
        metadata=conditions.metadata,
        caveats=[
            "Factor categories are evidence buckets and are not numerical scores.",
            "Raw Ashtakavarga values are returned without thresholds or reductions.",
            "Aspect totals are descriptive and do not classify benefic or malefic effect.",
            "Later Neecha Bhanga conventions are not imported into varahamihira_v1.",
            "No strongest-planet ranking, prediction, health, or longevity result is produced.",
        ],
    )
