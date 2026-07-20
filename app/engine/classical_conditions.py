"""Deterministic Varahamihira dignity and planetary-condition evaluation."""

from dataclasses import dataclass
from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_reference import (
    PROFILE_ID,
    get_varahamihira_grahas,
    get_varahamihira_rashis,
)
from app.engine.positions import SIGNS
from app.schemas.charts import ChartPoint, ChartRequest, ChartType
from app.schemas.classical import GrahaReference, NaturalTendency
from app.schemas.classical_conditions import (
    ClassicalConditionsRequest,
    ClassicalConditionsResponse,
    ConditionEvidence,
    DignityState,
    GrahaCondition,
    MercuryAssociationCondition,
    MercuryAssociationState,
    MoonPhaseCondition,
    MoonPhaseState,
    ResolvedTendency,
)

_DEEP_POINT_TOLERANCE_DEGREES = 1e-7
_CLASSICAL_GRAHAS = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)


@dataclass(frozen=True)
class DignityEvaluation:
    """Pure sign and deep-point dignity result for one Graha."""

    own_sign: bool
    in_exaltation_sign: bool
    at_deep_exaltation_point: bool
    in_debilitation_sign: bool
    at_deep_debilitation_point: bool
    dignity: DignityState


def evaluate_dignity(
    sign_id: str,
    degree_in_sign: float,
    reference: GrahaReference,
) -> DignityEvaluation:
    """Evaluate own-sign and exaltation/debilitation reference conditions."""

    own_sign = sign_id in reference.owned_signs
    in_exaltation_sign = sign_id == reference.exaltation_sign
    in_debilitation_sign = sign_id == reference.debilitation_sign
    at_deep_exaltation_point = in_exaltation_sign and (
        abs(degree_in_sign - reference.exaltation_degree)
        <= _DEEP_POINT_TOLERANCE_DEGREES
    )
    at_deep_debilitation_point = in_debilitation_sign and (
        abs(degree_in_sign - reference.debilitation_degree)
        <= _DEEP_POINT_TOLERANCE_DEGREES
    )

    if in_exaltation_sign:
        dignity = DignityState.EXALTATION_SIGN
    elif in_debilitation_sign:
        dignity = DignityState.DEBILITATION_SIGN
    elif own_sign:
        dignity = DignityState.OWN_SIGN
    else:
        dignity = DignityState.ORDINARY

    return DignityEvaluation(
        own_sign=own_sign,
        in_exaltation_sign=in_exaltation_sign,
        at_deep_exaltation_point=at_deep_exaltation_point,
        in_debilitation_sign=in_debilitation_sign,
        at_deep_debilitation_point=at_deep_debilitation_point,
        dignity=dignity,
    )


def _resolve_moon_phase(
    sun_longitude: float,
    moon_longitude: float,
) -> MoonPhaseCondition:
    elongation = (moon_longitude - sun_longitude) % 360.0
    near_new_moon = min(elongation, 360.0 - elongation) <= (
        _DEEP_POINT_TOLERANCE_DEGREES
    )
    near_full_moon = abs(elongation - 180.0) <= _DEEP_POINT_TOLERANCE_DEGREES

    if near_new_moon:
        phase = MoonPhaseState.NEW_MOON_BOUNDARY
        tendency = ResolvedTendency.CONDITIONAL
        reason = (
            "The Moon is at the exact new-Moon boundary, so no waxing/waning "
            "class is forced."
        )
    elif near_full_moon:
        phase = MoonPhaseState.FULL_MOON_BOUNDARY
        tendency = ResolvedTendency.BENEFIC
        reason = (
            "The Moon is at the exact full-Moon boundary and resolves on the "
            "waxing side."
        )
    elif elongation < 180.0:
        phase = MoonPhaseState.WAXING
        tendency = ResolvedTendency.BENEFIC
        reason = "The Moon is between conjunction with the Sun and full Moon."
    else:
        phase = MoonPhaseState.WANING
        tendency = ResolvedTendency.MALEFIC
        reason = "The Moon is between full Moon and the next conjunction with the Sun."

    return MoonPhaseCondition(
        elongation_degrees=round(elongation, 8),
        phase=phase,
        resolved_tendency=tendency,
        reason=reason,
        rule_ids=["VM-BJ-C02-MOON-PHASE-EVAL-001"],
    )


def _resolve_mercury_association(
    d1_points: dict[str, ChartPoint],
    sign_ids: dict[str, str],
    resolved_tendencies: dict[str, ResolvedTendency],
) -> MercuryAssociationCondition:
    mercury_sign_index = d1_points["mercury"].sign_index
    associated = [
        name
        for name in _CLASSICAL_GRAHAS
        if name != "mercury" and d1_points[name].sign_index == mercury_sign_index
    ]
    benefic = [
        name
        for name in associated
        if resolved_tendencies[name] == ResolvedTendency.BENEFIC
    ]
    malefic = [
        name
        for name in associated
        if resolved_tendencies[name] == ResolvedTendency.MALEFIC
    ]
    conditional = [
        name
        for name in associated
        if resolved_tendencies[name] == ResolvedTendency.CONDITIONAL
    ]

    if not associated:
        state = MercuryAssociationState.UNASSOCIATED
        tendency = ResolvedTendency.CONDITIONAL
        reason = (
            "No same-sign classical Graha association was found; Mercury "
            "remains conditional."
        )
    elif benefic and not malefic and not conditional:
        state = MercuryAssociationState.BENEFIC_ONLY
        tendency = ResolvedTendency.BENEFIC
        reason = "Mercury is associated only with Grahas resolved as benefic."
    elif malefic and not benefic and not conditional:
        state = MercuryAssociationState.MALEFIC_ONLY
        tendency = ResolvedTendency.MALEFIC
        reason = "Mercury is associated only with Grahas resolved as malefic."
    elif benefic and malefic:
        state = MercuryAssociationState.MIXED
        tendency = ResolvedTendency.CONDITIONAL
        reason = "Mercury has both benefic and malefic same-sign associations."
    else:
        state = MercuryAssociationState.CONDITIONAL
        tendency = ResolvedTendency.CONDITIONAL
        reason = "At least one same-sign association remains conditional or mixed."

    return MercuryAssociationCondition(
        d1_sign=sign_ids["mercury"],
        associated_grahas=associated,
        benefic_associations=benefic,
        malefic_associations=malefic,
        conditional_associations=conditional,
        state=state,
        resolved_tendency=tendency,
        reason=reason,
        rule_ids=["VM-BJ-C02-MERCURY-ASSOC-EVAL-001"],
    )


def _fixed_tendency(reference: GrahaReference) -> ResolvedTendency:
    if reference.natural_tendency == NaturalTendency.BENEFIC:
        return ResolvedTendency.BENEFIC
    if reference.natural_tendency == NaturalTendency.MALEFIC:
        return ResolvedTendency.MALEFIC
    return ResolvedTendency.CONDITIONAL


def _tendency_reason(
    name: str,
    reference: GrahaReference,
    moon_phase: MoonPhaseCondition,
    mercury_association: MercuryAssociationCondition,
) -> str:
    if name == "moon":
        return moon_phase.reason
    if name == "mercury":
        return mercury_association.reason
    return (
        f"{reference.english_name} has a fixed "
        f"{reference.natural_tendency.value} reference tendency."
    )


def _tendency_rule(name: str) -> str:
    if name == "moon":
        return "VM-BJ-C02-MOON-PHASE-EVAL-001"
    if name == "mercury":
        return "VM-BJ-C02-MERCURY-ASSOC-EVAL-001"
    return "VM-BJ-C02-ATTRIBUTES-001"


def _build_evidence(
    reference: GrahaReference,
    point: ChartPoint,
    sign_id: str,
    d9_sign_id: str,
    dignity: DignityEvaluation,
    vargottama: bool,
    tendency_rule: str,
    tendency_reason: str,
) -> list[ConditionEvidence]:
    return [
        ConditionEvidence(
            rule_id="VM-BJ-C01-OWN-SIGN-EVAL-001",
            condition="own_sign",
            applies=dignity.own_sign,
            reason=(
                f"{reference.english_name} occupies {point.sign}; owned signs are "
                f"{', '.join(reference.owned_signs)}."
            ),
        ),
        ConditionEvidence(
            rule_id="VM-BJ-C02-DIGNITY-EVAL-001",
            condition="exaltation_sign",
            applies=dignity.in_exaltation_sign,
            reason=(
                f"D1 sign is {sign_id}; registered exaltation sign is "
                f"{reference.exaltation_sign}."
            ),
        ),
        ConditionEvidence(
            rule_id="VM-BJ-C02-DIGNITY-EVAL-001",
            condition="deep_exaltation_point",
            applies=dignity.at_deep_exaltation_point,
            reason=(
                f"D1 degree is {point.degree_in_sign}; registered deep exaltation "
                f"degree is {reference.exaltation_degree}."
            ),
        ),
        ConditionEvidence(
            rule_id="VM-BJ-C02-DIGNITY-EVAL-001",
            condition="debilitation_sign",
            applies=dignity.in_debilitation_sign,
            reason=(
                f"D1 sign is {sign_id}; registered debilitation sign is "
                f"{reference.debilitation_sign}."
            ),
        ),
        ConditionEvidence(
            rule_id="VM-BJ-C02-DIGNITY-EVAL-001",
            condition="deep_debilitation_point",
            applies=dignity.at_deep_debilitation_point,
            reason=(
                f"D1 degree is {point.degree_in_sign}; registered deep debilitation "
                f"degree is {reference.debilitation_degree}."
            ),
        ),
        ConditionEvidence(
            rule_id="VM-BJ-C01-VARGOTTAMA-EVAL-001",
            condition="vargottama",
            applies=vargottama,
            reason=f"D1 sign is {sign_id}; D9 sign is {d9_sign_id}.",
        ),
        ConditionEvidence(
            rule_id=tendency_rule,
            condition="resolved_tendency",
            applies=True,
            reason=tendency_reason,
        ),
    ]


def calculate_varahamihira_conditions(
    request: ClassicalConditionsRequest,
) -> ClassicalConditionsResponse:
    """Evaluate D1/D9 dignity and non-predictive planetary conditions."""

    d1 = calculate_chart(
        ChartRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        ),
        ChartType.D1_RASI,
    )
    references = get_varahamihira_grahas().grahas
    reference_by_name = {reference.canonical_id: reference for reference in references}
    rashi_by_english = {
        rashi.english_name.lower(): rashi.canonical_id
        for rashi in get_varahamihira_rashis().rashis
    }
    d1_points = {
        point.name: point
        for point in d1.points
        if point.name in reference_by_name
    }
    sign_ids = {
        name: rashi_by_english[point.sign.lower()]
        for name, point in d1_points.items()
    }

    moon_phase = _resolve_moon_phase(
        d1_points["sun"].source_longitude,
        d1_points["moon"].source_longitude,
    )
    resolved_tendencies = {
        reference.canonical_id: _fixed_tendency(reference)
        for reference in references
        if reference.canonical_id != "mercury"
    }
    resolved_tendencies["moon"] = moon_phase.resolved_tendency
    mercury_association = _resolve_mercury_association(
        d1_points,
        sign_ids,
        resolved_tendencies,
    )
    resolved_tendencies["mercury"] = mercury_association.resolved_tendency

    d9_ascendant_longitude = (d1.ascendant.source_longitude * 9.0) % 360.0
    d9_ascendant_sign_index = int(d9_ascendant_longitude // 30.0) + 1
    conditions: list[GrahaCondition] = []

    for name in _CLASSICAL_GRAHAS:
        point = d1_points[name]
        reference = reference_by_name[name]
        sign_id = sign_ids[name]
        dignity = evaluate_dignity(sign_id, point.degree_in_sign, reference)
        d9_longitude = (point.source_longitude * 9.0) % 360.0
        d9_sign_index = int(d9_longitude // 30.0) + 1
        d9_sign_name = SIGNS[d9_sign_index - 1]
        d9_sign_id = rashi_by_english[d9_sign_name.lower()]
        vargottama = sign_id == d9_sign_id
        tendency_reason = _tendency_reason(
            name,
            reference,
            moon_phase,
            mercury_association,
        )
        associations = (
            mercury_association.associated_grahas if name == "mercury" else []
        )
        evidence = _build_evidence(
            reference,
            point,
            sign_id,
            d9_sign_id,
            dignity,
            vargottama,
            _tendency_rule(name),
            tendency_reason,
        )

        conditions.append(
            GrahaCondition(
                graha=name,
                source_longitude=point.source_longitude,
                d1_sign_index=point.sign_index,
                d1_sign=sign_id,
                d1_degree_in_sign=point.degree_in_sign,
                d1_house=point.house,
                d9_longitude=round(d9_longitude, 8),
                d9_sign_index=d9_sign_index,
                d9_sign=d9_sign_id,
                d9_degree_in_sign=round(d9_longitude % 30.0, 8),
                d9_house=((d9_sign_index - d9_ascendant_sign_index) % 12) + 1,
                retrograde=bool(point.retrograde),
                own_sign=dignity.own_sign,
                in_exaltation_sign=dignity.in_exaltation_sign,
                at_deep_exaltation_point=dignity.at_deep_exaltation_point,
                in_debilitation_sign=dignity.in_debilitation_sign,
                at_deep_debilitation_point=dignity.at_deep_debilitation_point,
                dignity=dignity.dignity,
                vargottama=vargottama,
                natural_tendency_reference=reference.natural_tendency,
                resolved_tendency=resolved_tendencies[name],
                tendency_reason=tendency_reason,
                associations=associations,
                evidence=evidence,
            )
        )

    return ClassicalConditionsResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=d1.time,
        coordinates=d1.coordinates,
        ayanamsha_degrees=d1.ayanamsha_degrees,
        moon_phase=moon_phase,
        mercury_association=mercury_association,
        grahas=conditions,
        excluded_points=["rahu", "ketu"],
        metadata=d1.metadata,
        caveats=[
            "This endpoint reports deterministic conditions, not predictions.",
            "Sign-level dignity is distinct from the exact deep dignity degree.",
            "Mercury uses same-sign association among the seven classical Grahas.",
            "Rahu and Ketu are excluded from the Chapter 2 condition pass.",
        ],
    )
