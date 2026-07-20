"""Compose active Vimshottari timing with deterministic Varahamihira context."""

from collections import Counter
from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_ashtakavarga import calculate_varahamihira_ashtakavarga
from app.engine.classical_aspects import calculate_varahamihira_aspects
from app.engine.classical_career import calculate_varahamihira_career
from app.engine.classical_conditions import calculate_varahamihira_conditions
from app.engine.classical_reference import PROFILE_ID, get_varahamihira_rashis
from app.engine.classical_relationships import (
    CLASSICAL_GRAHAS,
    COMPOUND_RULE_ID,
    NATURAL_RULE_ID,
    TEMPORARY_RULE_ID,
    evaluate_relationship,
)
from app.engine.current_dasha import calculate_current_vimshottari
from app.schemas.charts import ChartRequest, ChartType
from app.schemas.classical_ashtakavarga import AshtakavargaRequest
from app.schemas.classical_aspects import AspectRay, ClassicalAspectsRequest
from app.schemas.classical_career import ClassicalCareerRequest
from app.schemas.classical_conditions import ClassicalConditionsRequest
from app.schemas.classical_dasha import (
    ClassicalDashaRequest,
    ClassicalDashaResponse,
    DashaAspectFact,
    DashaConjunctionFact,
    DashaEvidence,
    DashaEvidenceCategory,
    DashaInterpretationLevel,
    DashaLevelRelationship,
    DashaLordInterpretation,
)
from app.schemas.dasha import ActiveDashaPeriod, CurrentVimshottariRequest

_CLASSICAL_GRAHAS = set(CLASSICAL_GRAHAS)

_LEVELS = (
    DashaInterpretationLevel.MAHADASHA,
    DashaInterpretationLevel.ANTARDASHA,
    DashaInterpretationLevel.PRATYANTARDASHA,
    DashaInterpretationLevel.SOOKSHMA,
)

_INTEGRATION_RULE_IDS = {
    "ownership": "VM-BJ-C01-DASHA-OWNERSHIP-CONTEXT-001",
    "condition": "VM-BJ-C02-DASHA-CONDITION-CONTEXT-001",
    "aspect": "VM-BJ-C02-DASHA-ASPECT-CONTEXT-001",
    "ashtakavarga": "VM-BJ-C09-DASHA-ASHTAKAVARGA-CONTEXT-001",
    "career": "VM-BJ-C10-DASHA-CAREER-CONTEXT-001",
    "node": "VM-BJ-C02-DASHA-NODE-COVERAGE-001",
}


def _evidence(
    category: DashaEvidenceCategory,
    fact: str,
    value: str,
    reason: str,
    rule_ids: list[str],
) -> DashaEvidence:
    return DashaEvidence(
        category=category,
        fact=fact,
        value=value,
        reason=reason,
        rule_ids=rule_ids,
    )


def _aspect_fact(ray: AspectRay) -> DashaAspectFact:
    return DashaAspectFact(
        source_graha=ray.source_graha,
        target_sign=ray.target_sign,
        target_house=ray.target_house,
        relative_house=ray.relative_house,
        strength_fraction=ray.strength_fraction,
        strength_label=ray.strength_label.value,
        is_special_full=ray.is_special_full,
        rule_ids=list(ray.rule_ids),
    )


def _active_level_relationships(
    periods: tuple[ActiveDashaPeriod, ...],
    points: dict[str, object],
) -> list[DashaLevelRelationship]:
    """Return all twelve directed relationships among four active levels."""

    results: list[DashaLevelRelationship] = []
    for source_index, source_period in enumerate(periods):
        source_level = _LEVELS[source_index]
        source_lord = source_period.lord.value
        for target_index, target_period in enumerate(periods):
            if source_index == target_index:
                continue
            target_level = _LEVELS[target_index]
            target_lord = target_period.lord.value

            if source_lord == target_lord:
                results.append(
                    DashaLevelRelationship(
                        source_level=source_level,
                        source_lord=source_lord,
                        target_level=target_level,
                        target_lord=target_lord,
                        available=False,
                        rule_ids=[NATURAL_RULE_ID],
                        reason=(
                            "Both active levels have the same lord; the Chapter 2 "
                            "relationship table applies between different Grahas."
                        ),
                    )
                )
                continue

            if source_lord not in _CLASSICAL_GRAHAS or target_lord not in _CLASSICAL_GRAHAS:
                results.append(
                    DashaLevelRelationship(
                        source_level=source_level,
                        source_lord=source_lord,
                        target_level=target_level,
                        target_lord=target_lord,
                        available=False,
                        rule_ids=[_INTEGRATION_RULE_IDS["node"]],
                        reason=(
                            "The seven-Graha relationship table does not assign natural "
                            "friendship to Rahu or Ketu."
                        ),
                    )
                )
                continue

            source_point = points[source_lord]
            target_point = points[target_lord]
            natural, temporary, compound, target_house = evaluate_relationship(
                source_lord,
                target_lord,
                source_point.sign_index,
                target_point.sign_index,
            )
            results.append(
                DashaLevelRelationship(
                    source_level=source_level,
                    source_lord=source_lord,
                    target_level=target_level,
                    target_lord=target_lord,
                    available=True,
                    target_relative_house=target_house,
                    natural_relationship=natural,
                    temporary_relationship=temporary,
                    compound_relationship=compound,
                    rule_ids=[NATURAL_RULE_ID, TEMPORARY_RULE_ID, COMPOUND_RULE_ID],
                    reason=(
                        f"{source_lord} treats {target_lord} as {natural.value} "
                        f"naturally and {temporary.value} temporarily, producing "
                        f"{compound.value}."
                    ),
                )
            )
    return results


def calculate_varahamihira_dasha_context(
    request: ClassicalDashaRequest,
) -> ClassicalDashaResponse:
    """Return active Vimshottari timing annotated with non-predictive context."""

    current_request = CurrentVimshottariRequest(
        birth=request.birth,
        as_of=request.as_of,
        calculation_profile=request.calculation_profile,
    )
    timing = calculate_current_vimshottari(current_request)

    chart_request = ChartRequest(
        birth=request.birth,
        calculation_profile=request.calculation_profile,
    )
    d1 = calculate_chart(chart_request, ChartType.D1_RASI)
    conditions = calculate_varahamihira_conditions(
        ClassicalConditionsRequest(
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
    career = calculate_varahamihira_career(
        ClassicalCareerRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )

    points = {point.name: point for point in d1.points}
    signs = {rashi.index: rashi for rashi in get_varahamihira_rashis().rashis}
    condition_by_graha = {condition.graha: condition for condition in conditions.grahas}
    bav_by_graha = {
        record.graha: record for record in ashtakavarga.bhinnashtakavargas
    }
    sav_by_sign = {
        summary.sign_index: summary
        for summary in ashtakavarga.sarvashtakavarga.signs
    }

    periods: tuple[ActiveDashaPeriod, ...] = (
        timing.mahadasha,
        timing.antardasha,
        timing.pratyantardasha,
        timing.sookshma,
    )
    levels: list[DashaLordInterpretation] = []

    for level, period in zip(_LEVELS, periods, strict=True):
        lord = period.lord.value
        point = points[lord]
        rashi = signs[point.sign_index]
        classical_available = lord in _CLASSICAL_GRAHAS

        owned_rashis = [item for item in signs.values() if item.lord == lord]
        owned_signs = [item.canonical_id for item in owned_rashis]
        owned_houses = [
            ((item.index - d1.ascendant.sign_index) % 12) + 1
            for item in owned_rashis
        ]

        sign_cell = next(cell for cell in d1.signs if cell.sign_index == point.sign_index)
        cooccupants = sorted(
            occupant
            for occupant in sign_cell.occupants
            if occupant not in {lord, "ascendant"}
        )

        conjunctions: list[DashaConjunctionFact] = []
        if classical_available:
            for conjunction in aspects.conjunctions:
                if lord not in conjunction.grahas:
                    continue
                other = next(graha for graha in conjunction.grahas if graha != lord)
                conjunctions.append(
                    DashaConjunctionFact(
                        other_graha=other,
                        sign=conjunction.sign,
                        house=conjunction.house,
                        angular_separation_degrees=(
                            conjunction.angular_separation_degrees
                        ),
                        rule_ids=list(conjunction.rule_ids),
                    )
                )

        cast_rays = [
            _aspect_fact(ray)
            for ray in aspects.aspects
            if ray.source_graha == lord
        ]
        received_rays = [
            _aspect_fact(ray)
            for ray in aspects.aspects
            if ray.target_sign_index == point.sign_index
        ]
        if not classical_available:
            cast_rays = []

        condition = condition_by_graha.get(lord)
        bav = bav_by_graha.get(lord)
        bav_bindus = (
            bav.bindus_by_sign[point.sign_index - 1]
            if bav is not None
            else None
        )
        sav_bindus = sav_by_sign[point.sign_index].sarvashtakavarga_bindus

        career_channels = [
            channel.reference_point.value
            for channel in career.channels
            if channel.karmājīva_indicator_graha == lord
        ]
        vocation_theme_ids = sorted(
            {
                theme.theme_id
                for channel in career.channels
                if channel.karmājīva_indicator_graha == lord
                for theme in channel.vocation_themes
            }
        )

        supporting: list[DashaEvidence] = []
        challenging: list[DashaEvidence] = []
        contextual: list[DashaEvidence] = []
        collected_rule_ids = set(_INTEGRATION_RULE_IDS.values())

        if condition is not None:
            if condition.in_exaltation_sign:
                supporting.append(
                    _evidence(
                        DashaEvidenceCategory.SUPPORTING,
                        "exaltation_sign",
                        condition.d1_sign,
                        f"{lord} occupies its registered exaltation sign.",
                        ["VM-BJ-C02-DIGNITY-EVAL-001"],
                    )
                )
            if condition.own_sign:
                supporting.append(
                    _evidence(
                        DashaEvidenceCategory.SUPPORTING,
                        "own_sign",
                        condition.d1_sign,
                        f"{lord} occupies a Rashi it owns.",
                        ["VM-BJ-C01-OWN-SIGN-EVAL-001"],
                    )
                )
            if condition.vargottama:
                supporting.append(
                    _evidence(
                        DashaEvidenceCategory.SUPPORTING,
                        "vargottama",
                        "true",
                        f"{lord} occupies the same Rashi in D1 and D9.",
                        ["VM-BJ-C01-VARGOTTAMA-EVAL-001"],
                    )
                )
            if condition.in_debilitation_sign:
                challenging.append(
                    _evidence(
                        DashaEvidenceCategory.CHALLENGING,
                        "debilitation_sign",
                        condition.d1_sign,
                        f"{lord} occupies its registered debilitation sign.",
                        ["VM-BJ-C02-DIGNITY-EVAL-001"],
                    )
                )
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "resolved_tendency",
                    condition.resolved_tendency.value,
                    condition.tendency_reason,
                    [_INTEGRATION_RULE_IDS["condition"]],
                )
            )
            if condition.retrograde:
                contextual.append(
                    _evidence(
                        DashaEvidenceCategory.CONTEXTUAL,
                        "retrograde",
                        "true",
                        f"{lord} is retrograde in the natal D1 calculation.",
                        [_INTEGRATION_RULE_IDS["condition"]],
                    )
                )
        else:
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "classical_node_coverage",
                    "not_available",
                    (
                        f"{lord} timing and natal placement are returned, but the "
                        "seven-Graha Chapter 2 dignity evaluator does not score this node."
                    ),
                    [_INTEGRATION_RULE_IDS["node"]],
                )
            )

        if owned_houses:
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "owned_houses",
                    ",".join(str(house) for house in owned_houses),
                    f"{lord} rules {', '.join(owned_signs)} in the D1 whole-sign chart.",
                    [_INTEGRATION_RULE_IDS["ownership"]],
                )
            )
        if cooccupants:
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "same_sign_cooccupants",
                    ",".join(cooccupants),
                    f"The natal D1 sign occupied by {lord} contains other points.",
                    [_INTEGRATION_RULE_IDS["aspect"]],
                )
            )
        contextual.append(
            _evidence(
                DashaEvidenceCategory.CONTEXTUAL,
                "sarvashtakavarga_bindus",
                str(sav_bindus),
                (
                    f"The occupied sign {rashi.canonical_id} has {sav_bindus} raw "
                    "Sarvashtakavarga bindus. No predictive threshold is applied."
                ),
                [_INTEGRATION_RULE_IDS["ashtakavarga"]],
            )
        )
        if bav_bindus is not None:
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "bhinnashtakavarga_bindus",
                    str(bav_bindus),
                    (
                        f"{lord}'s raw Bhinnashtakavarga gives {bav_bindus} bindus "
                        f"to its occupied sign {rashi.canonical_id}."
                    ),
                    [*bav.rule_ids, _INTEGRATION_RULE_IDS["ashtakavarga"]],
                )
            )
            collected_rule_ids.update(bav.rule_ids)
        if career_channels:
            contextual.append(
                _evidence(
                    DashaEvidenceCategory.CONTEXTUAL,
                    "karmajiiva_channels",
                    ",".join(career_channels),
                    (
                        f"{lord} is a Chapter 10 Karmājīva indicator in the listed "
                        "reference channels; no career event is predicted."
                    ),
                    [_INTEGRATION_RULE_IDS["career"]],
                )
            )

        for conjunction in conjunctions:
            collected_rule_ids.update(conjunction.rule_ids)
        for ray in [*cast_rays, *received_rays]:
            collected_rule_ids.update(ray.rule_ids)

        levels.append(
            DashaLordInterpretation(
                level=level,
                period=period,
                lord=lord,
                classical_condition_available=classical_available,
                source_longitude=point.source_longitude,
                d1_sign_index=point.sign_index,
                d1_sign=rashi.canonical_id,
                d1_house=point.house,
                owned_signs=owned_signs,
                owned_houses=owned_houses,
                dignity=condition.dignity if condition is not None else None,
                own_sign=condition.own_sign if condition is not None else None,
                in_exaltation_sign=(
                    condition.in_exaltation_sign if condition is not None else None
                ),
                in_debilitation_sign=(
                    condition.in_debilitation_sign if condition is not None else None
                ),
                vargottama=condition.vargottama if condition is not None else None,
                retrograde=point.retrograde,
                resolved_tendency=(
                    condition.resolved_tendency if condition is not None else None
                ),
                same_sign_cooccupants=cooccupants,
                conjunctions=conjunctions,
                aspects_cast=cast_rays,
                aspects_received=received_rays,
                bhinnashtakavarga_bindus_in_occupied_sign=bav_bindus,
                sarvashtakavarga_bindus_in_occupied_sign=sav_bindus,
                karmajiiva_channels=career_channels,
                vocation_theme_ids=vocation_theme_ids,
                supporting_evidence=supporting,
                challenging_evidence=challenging,
                contextual_evidence=contextual,
                rule_ids=sorted(collected_rule_ids),
            )
        )

    lord_sequence = [period.lord.value for period in periods]
    counts = Counter(lord_sequence)
    unique_lords = list(dict.fromkeys(lord_sequence))
    repeated_lords = [lord for lord in unique_lords if counts[lord] > 1]
    level_relationships = _active_level_relationships(periods, points)

    return ClassicalDashaResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        timing=timing,
        levels=levels,
        relationships_between_levels=level_relationships,
        unique_lords=unique_lords,
        repeated_lords=repeated_lords,
        interpretation_mode="evidence_only",
        prediction_applied=False,
        cancellations_applied=False,
        strength_weighting_applied=False,
        caveats=[
            "Vimshottari supplies timing; Brihat Jataka context does not redefine it.",
            "Supporting and challenging labels are unweighted condition buckets.",
            "Active-lord relationship labels are categorical and unweighted.",
            "Raw Ashtakavarga bindus are returned without thresholds or transit judgment.",
            "Rahu and Ketu receive neutral placement context, not invented dignity rules.",
            "No event, profession, health, relationship, or longevity outcome is predicted.",
        ],
    )
