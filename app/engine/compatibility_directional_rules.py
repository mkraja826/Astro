"""Role-aware Varna, Vashya, and Gana convention evaluators.

The tables in this module are a frozen product convention. They return raw
Ashtakoota component facts and never make marriage-outcome claims.
"""

from __future__ import annotations

from app.engine.compatibility_rules import (
    COMPATIBILITY_CONVENTION_PROFILE,
    DIRECTIONAL_COMPONENTS,
    evaluate_direction_independent_components,
)
from app.schemas.compatibility import (
    ASHTAKOOTA_MAXIMUM_POINTS,
    ASHTAKOOTA_TOTAL_POINTS,
    AshtakootaComponent,
    AshtakootaComponentFact,
    CompatibilityNatalFacts,
    ComponentEvaluationStatus,
    TraditionalCompatibilityRole,
)

DIRECTIONAL_RULE_PROFILE = "saravali_maitreya_directional_tables_v1"

_VARNA_NAMES = ("shudra", "vaishya", "kshatriya", "brahmin")
_VARNA_RANK_BY_SIGN = (
    2,
    0,
    1,
    3,
    2,
    0,
    1,
    3,
    2,
    0,
    1,
    3,
)

_VASHYA_NAMES = ("quadruped", "human", "jalachara", "leo", "scorpio")
_VASHYA_POINTS = (
    (2.0, 0.0, 0.0, 0.5, 0.0),
    (1.0, 2.0, 1.0, 0.5, 1.0),
    (0.5, 1.0, 2.0, 1.0, 1.0),
    (0.0, 0.0, 0.0, 2.0, 0.0),
    (1.0, 1.0, 1.0, 0.0, 2.0),
)

_GANA_NAMES = ("deva", "manushya", "rakshasa")
_GANA_BY_NAKSHATRA = (
    0,
    1,
    2,
    1,
    0,
    1,
    0,
    0,
    2,
    2,
    1,
    1,
    0,
    2,
    0,
    2,
    0,
    2,
    2,
    1,
    1,
    0,
    2,
    2,
    1,
    1,
    0,
)
_GANA_POINTS = (
    (6.0, 6.0, 0.0),
    (5.0, 6.0, 0.0),
    (1.0, 0.0, 6.0),
)


def _fact(
    component: AshtakootaComponent,
    points: float,
    rule_id: str,
    *notes: str,
) -> AshtakootaComponentFact:
    return AshtakootaComponentFact(
        component=component,
        status=ComponentEvaluationStatus.EVALUATED,
        achieved_points=points,
        maximum_points=ASHTAKOOTA_MAXIMUM_POINTS[component],
        rule_ids=[rule_id],
        source_kind="convention",
        calculation_notes=[
            f"Convention profile: {COMPATIBILITY_CONVENTION_PROFILE}.",
            f"Directional rule profile: {DIRECTIONAL_RULE_PROFILE}.",
            *notes,
        ],
    )


def _abstained_fact(component: AshtakootaComponent) -> AshtakootaComponentFact:
    return AshtakootaComponentFact(
        component=component,
        status=ComponentEvaluationStatus.ABSTAINED,
        achieved_points=None,
        maximum_points=ASHTAKOOTA_MAXIMUM_POINTS[component],
        rule_ids=[f"ASTRO-CONV-ASHTAKOOTA-{component.value.upper()}-ROLE-ABSTAIN-001"],
        source_kind="convention",
        abstention_reason=(
            "Traditional bride/groom roles were not supplied; this directional "
            "component cannot be evaluated safely."
        ),
        calculation_notes=[
            f"Convention profile: {COMPATIBILITY_CONVENTION_PROFILE}.",
            "No directional points are imputed when roles are absent.",
        ],
    )


def _bride_and_groom(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    subject_role: TraditionalCompatibilityRole,
    partner_role: TraditionalCompatibilityRole,
) -> tuple[CompatibilityNatalFacts, CompatibilityNatalFacts]:
    roles = {subject_role, partner_role}
    required = {
        TraditionalCompatibilityRole.BRIDE,
        TraditionalCompatibilityRole.GROOM,
    }
    if roles != required:
        raise ValueError("directional Kootas require one bride role and one groom role")
    if subject_role is TraditionalCompatibilityRole.BRIDE:
        return subject, partner
    return partner, subject


def _vashya_category(sign_index: int, degree_in_sign: float) -> int:
    if sign_index in {3, 6, 7, 11}:
        return 1
    if sign_index in {1, 2}:
        return 0
    if sign_index in {4, 12}:
        return 2
    if sign_index == 5:
        return 3
    if sign_index == 8:
        return 4
    if sign_index == 9:
        return 1 if degree_in_sign < 15.0 else 0
    if sign_index == 10:
        return 0 if degree_in_sign < 15.0 else 2
    raise ValueError("moon sign index must be between 1 and 12")


def evaluate_varna(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    *,
    subject_role: TraditionalCompatibilityRole,
    partner_role: TraditionalCompatibilityRole,
) -> AshtakootaComponentFact:
    """Score one point when the groom Varna rank is at least the bride rank."""

    bride, groom = _bride_and_groom(
        subject,
        partner,
        subject_role,
        partner_role,
    )
    bride_rank = _VARNA_RANK_BY_SIGN[bride.moon_sign_index - 1]
    groom_rank = _VARNA_RANK_BY_SIGN[groom.moon_sign_index - 1]
    points = 1.0 if groom_rank >= bride_rank else 0.0
    return _fact(
        AshtakootaComponent.VARNA,
        points,
        "ASTRO-CONV-ASHTAKOOTA-VARNA-001",
        f"Bride Varna: {_VARNA_NAMES[bride_rank]}.",
        f"Groom Varna: {_VARNA_NAMES[groom_rank]}.",
        "The Moon-sign Varna hierarchy is applied directionally.",
    )


def evaluate_vashya(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    *,
    subject_role: TraditionalCompatibilityRole,
    partner_role: TraditionalCompatibilityRole,
) -> AshtakootaComponentFact:
    """Apply the directional bride-row/groom-column Vashya matrix."""

    bride, groom = _bride_and_groom(
        subject,
        partner,
        subject_role,
        partner_role,
    )
    bride_category = _vashya_category(
        bride.moon_sign_index,
        bride.moon_degree_in_sign,
    )
    groom_category = _vashya_category(
        groom.moon_sign_index,
        groom.moon_degree_in_sign,
    )
    points = _VASHYA_POINTS[bride_category][groom_category]
    return _fact(
        AshtakootaComponent.VASHYA,
        points,
        "ASTRO-CONV-ASHTAKOOTA-VASHYA-001",
        f"Bride Vashya: {_VASHYA_NAMES[bride_category]}.",
        f"Groom Vashya: {_VASHYA_NAMES[groom_category]}.",
        "Sagittarius and Capricorn are split at 15 degrees.",
    )


def evaluate_gana(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    *,
    subject_role: TraditionalCompatibilityRole,
    partner_role: TraditionalCompatibilityRole,
) -> AshtakootaComponentFact:
    """Apply the directional bride-row/groom-column Gana matrix."""

    bride, groom = _bride_and_groom(
        subject,
        partner,
        subject_role,
        partner_role,
    )
    bride_gana = _GANA_BY_NAKSHATRA[bride.moon_nakshatra_index - 1]
    groom_gana = _GANA_BY_NAKSHATRA[groom.moon_nakshatra_index - 1]
    points = _GANA_POINTS[bride_gana][groom_gana]
    return _fact(
        AshtakootaComponent.GANA,
        points,
        "ASTRO-CONV-ASHTAKOOTA-GANA-001",
        f"Bride Gana: {_GANA_NAMES[bride_gana]}.",
        f"Groom Gana: {_GANA_NAMES[groom_gana]}.",
        "The matrix is directional and no cancellation rule is applied.",
    )


def evaluate_directional_components(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    *,
    subject_role: TraditionalCompatibilityRole,
    partner_role: TraditionalCompatibilityRole,
) -> tuple[AshtakootaComponentFact, ...]:
    """Evaluate the three directional Kootas."""

    return (
        evaluate_varna(
            subject,
            partner,
            subject_role=subject_role,
            partner_role=partner_role,
        ),
        evaluate_vashya(
            subject,
            partner,
            subject_role=subject_role,
            partner_role=partner_role,
        ),
        evaluate_gana(
            subject,
            partner,
            subject_role=subject_role,
            partner_role=partner_role,
        ),
    )


def evaluate_ashtakoota_components(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
    *,
    subject_role: TraditionalCompatibilityRole = TraditionalCompatibilityRole.UNSPECIFIED,
    partner_role: TraditionalCompatibilityRole = TraditionalCompatibilityRole.UNSPECIFIED,
) -> tuple[AshtakootaComponentFact, ...]:
    """Return all eight facts, abstaining for directional Kootas when roles are absent."""

    released = {
        item.component: item
        for item in evaluate_direction_independent_components(subject, partner)
    }
    roles_supplied = (
        {subject_role, partner_role}
        == {
            TraditionalCompatibilityRole.BRIDE,
            TraditionalCompatibilityRole.GROOM,
        }
    )
    if roles_supplied:
        released.update(
            {
                item.component: item
                for item in evaluate_directional_components(
                    subject,
                    partner,
                    subject_role=subject_role,
                    partner_role=partner_role,
                )
            }
        )
    return tuple(
        released.get(component) or _abstained_fact(component)
        for component in AshtakootaComponent
    )


def summarize_ashtakoota_coverage(
    components: tuple[AshtakootaComponentFact, ...],
) -> tuple[float, int, bool]:
    """Return achieved points, evaluated maximum, and completeness."""

    evaluated = [
        item for item in components if item.status is ComponentEvaluationStatus.EVALUATED
    ]
    achieved = sum(item.achieved_points or 0.0 for item in evaluated)
    evaluated_maximum = sum(item.maximum_points for item in evaluated)
    return (
        achieved,
        evaluated_maximum,
        evaluated_maximum == ASHTAKOOTA_TOTAL_POINTS,
    )
