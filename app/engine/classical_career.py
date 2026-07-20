"""Deterministic Varahamihira Chapter 10 Karmājīva career analysis."""

from collections import defaultdict
from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_aspects import (
    aspect_specifications_for_graha,
    target_sign_index,
)
from app.engine.classical_conditions import evaluate_dignity
from app.engine.classical_reference import (
    PROFILE_ID,
    get_varahamihira_grahas,
    get_varahamihira_rashis,
)
from app.schemas.charts import ChartPoint, ChartRequest, ChartType
from app.schemas.classical_career import (
    CareerAspectFact,
    CareerCandidate,
    CareerChannel,
    CareerEvidence,
    CareerReferencePoint,
    ClassicalCareerRequest,
    ClassicalCareerResponse,
    IncomeSourceIndication,
    IndicatorConditionSnapshot,
    VocationTheme,
)

_CLASSICAL_GRAHAS = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)

_INCOME_SOURCE_DATA = {
    "sun": ("father", "Father", "pitṛ"),
    "moon": ("mother", "Mother", "pitṛ-patnī"),
    "mars": ("enemy", "Enemies or competitors", "śatru"),
    "mercury": ("friend", "Friends or allies", "mitra"),
    "jupiter": ("brother", "Brothers or siblings", "bhrātṛ"),
    "venus": ("wife_or_woman", "Wife or women", "strī"),
    "saturn": ("servant", "Servants or service relationships", "servant"),
}

_VOCATION_DATA = {
    "sun": (
        (
            "plant_medicine_trade",
            "Plants, medicines, and healing materials",
            ["perfumes or herbs", "medicines", "medical treatment"],
            ["pharmacy", "healthcare supplies", "herbal products", "clinical work"],
        ),
        (
            "gold_wool_trade",
            "Gold and woollen goods",
            ["gold", "woollen fabric"],
            ["precious-metal trade", "textiles", "luxury materials"],
        ),
    ),
    "moon": (
        (
            "agriculture",
            "Agriculture and cultivation",
            ["tilling lands", "agriculture"],
            ["farming", "horticulture", "agricultural operations"],
        ),
        (
            "aquatic_products",
            "Water-derived products",
            ["productions of water"],
            ["fisheries", "pearls and marine products", "water-linked commerce"],
        ),
        (
            "women_patronage",
            "Work supported through women",
            ["through women"],
            ["women-led organizations", "female clientele", "patronage or service"],
        ),
    ),
    "mars": (
        (
            "metals_minerals",
            "Metals and minerals",
            ["metals", "minerals"],
            ["metallurgy", "mining", "engineering materials", "manufacturing"],
        ),
        (
            "fire_weapons_operations",
            "Fire, weapons, and forceful operations",
            ["fire", "weapons", "acts of boldness"],
            ["fire services", "defence", "security", "hazardous operations"],
        ),
    ),
    "mercury": (
        (
            "writing_accounting",
            "Writing, calculation, and accounts",
            ["writing", "accounting", "mathematics"],
            ["software", "data analysis", "accounting", "publishing"],
        ),
        (
            "literature_crafts",
            "Literature and skilled crafts",
            ["poetry", "handicraft", "fine arts"],
            ["content creation", "design", "technical crafts", "creative arts"],
        ),
    ),
    "jupiter": (
        (
            "learning_religion_law",
            "Learning, religion, law, and ethical service",
            ["learned men", "religious duties", "acts of virtue"],
            ["education", "law", "advisory work", "religious or charitable service"],
        ),
        (
            "mines_contracts",
            "Mines and organized undertakings",
            ["mines", "contract work"],
            ["resource industries", "institutional projects", "contracting"],
        ),
    ),
    "venus": (
        (
            "gems_silver_luxury",
            "Gems, silver, and valuable goods",
            ["gems", "silver", "other metals"],
            ["jewellery", "luxury retail", "precious materials", "fashion"],
        ),
        (
            "livestock",
            "Cattle and livestock",
            ["cows", "buffaloes"],
            ["dairy", "livestock management", "animal-based commerce"],
        ),
    ),
    "saturn": (
        (
            "labor_heavy_work",
            "Hard labour and heavy-load work",
            ["hard labour", "carrying burdens"],
            ["logistics", "construction", "manual operations", "heavy industry"],
        ),
        (
            "difficult_manual_service",
            "Difficult manual or service work",
            ["acts of torture", "low deeds unsuited to rank"],
            ["demanding service roles", "waste or demolition work", "manual crafts"],
        ),
    ),
}


def _vocation_rule_id(graha: str) -> str:
    if graha in {"sun", "moon", "mars", "mercury"}:
        return "VM-BJ-C10-VOCATION-SUN-MERCURY-001"
    return "VM-BJ-C10-VOCATION-JUPITER-SATURN-001"


def _vocation_themes(graha: str) -> list[VocationTheme]:
    rule_id = _vocation_rule_id(graha)
    return [
        VocationTheme(
            theme_id=theme_id,
            label=label,
            classical_terms=classical_terms,
            modern_examples=modern_examples,
            rule_ids=[rule_id],
        )
        for theme_id, label, classical_terms, modern_examples in _VOCATION_DATA[graha]
    ]


def _income_sources(occupants: list[str]) -> list[IncomeSourceIndication]:
    results = []
    for graha in occupants:
        source_id, label, classical_relation = _INCOME_SOURCE_DATA[graha]
        results.append(
            IncomeSourceIndication(
                graha=graha,
                source_id=source_id,
                label=label,
                classical_relation=classical_relation,
                rule_ids=["VM-BJ-C10-INCOME-SOURCE-EVAL-001"],
            )
        )
    return results


def _canonical_maps() -> tuple[dict[int, object], dict[str, str]]:
    rashis = get_varahamihira_rashis().rashis
    by_index = {rashi.index: rashi for rashi in rashis}
    by_english = {rashi.english_name.lower(): rashi.canonical_id for rashi in rashis}
    return by_index, by_english


def _d9_position(point: ChartPoint) -> tuple[float, int, float]:
    longitude = (point.source_longitude * 9.0) % 360.0
    sign_index = int(longitude // 30.0) + 1
    return longitude, sign_index, longitude % 30.0


def _condition_snapshot(
    graha: str,
    points: dict[str, ChartPoint],
    canonical_by_english: dict[str, str],
    graha_references: dict[str, object],
) -> IndicatorConditionSnapshot:
    point = points[graha]
    reference = graha_references[graha]
    d1_sign = canonical_by_english[point.sign.lower()]
    _, d9_sign_index, _ = _d9_position(point)
    d9_sign = get_varahamihira_rashis().rashis[d9_sign_index - 1].canonical_id
    dignity = evaluate_dignity(d1_sign, point.degree_in_sign, reference)
    conjunctions = [
        name
        for name in _CLASSICAL_GRAHAS
        if name != graha and points[name].sign_index == point.sign_index
    ]

    return IndicatorConditionSnapshot(
        graha=graha,
        d1_sign=d1_sign,
        d1_house=point.house,
        d1_degree_in_sign=point.degree_in_sign,
        dignity=dignity.dignity,
        own_sign=dignity.own_sign,
        in_exaltation_sign=dignity.in_exaltation_sign,
        in_debilitation_sign=dignity.in_debilitation_sign,
        vargottama=d1_sign == d9_sign,
        retrograde=bool(point.retrograde),
        conjunctions=conjunctions,
    )


def _aspects_to_sign(
    target_index: int,
    points: dict[str, ChartPoint],
) -> list[CareerAspectFact]:
    results = []
    for source_graha in _CLASSICAL_GRAHAS:
        source = points[source_graha]
        for specification in aspect_specifications_for_graha(source_graha):
            if (
                target_sign_index(source.sign_index, specification.relative_house)
                != target_index
            ):
                continue
            results.append(
                CareerAspectFact(
                    source_graha=source_graha,
                    relative_house=specification.relative_house,
                    strength_fraction=specification.strength_fraction,
                    strength_label=specification.strength_label.value,
                    is_special_full=specification.is_special_full,
                    rule_ids=list(specification.rule_ids),
                )
            )
    return results


def calculate_varahamihira_career(
    request: ClassicalCareerRequest,
) -> ClassicalCareerResponse:
    """Return all three Chapter 10 Karmājīva channels without ranking them."""

    d1 = calculate_chart(
        ChartRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        ),
        ChartType.D1_RASI,
    )
    rashi_by_index, canonical_by_english = _canonical_maps()
    graha_references = {
        reference.canonical_id: reference
        for reference in get_varahamihira_grahas().grahas
    }
    points = {
        point.name: point
        for point in d1.points
        if point.name in _CLASSICAL_GRAHAS
    }
    occupants_by_sign: dict[int, list[str]] = {
        index: [] for index in range(1, 13)
    }
    for graha in _CLASSICAL_GRAHAS:
        occupants_by_sign[points[graha].sign_index].append(graha)

    reference_signs = {
        CareerReferencePoint.LAGNA: d1.ascendant.sign_index,
        CareerReferencePoint.MOON: points["moon"].sign_index,
        CareerReferencePoint.SUN: points["sun"].sign_index,
    }
    condition_cache: dict[str, IndicatorConditionSnapshot] = {}
    channels: list[CareerChannel] = []

    for reference_point in CareerReferencePoint:
        reference_sign_index = reference_signs[reference_point]
        reference_sign = rashi_by_index[reference_sign_index].canonical_id
        tenth_sign_index = target_sign_index(reference_sign_index, 10)
        tenth_rashi = rashi_by_index[tenth_sign_index]
        occupants = list(occupants_by_sign[tenth_sign_index])
        tenth_lord = tenth_rashi.lord
        tenth_lord_point = points[tenth_lord]
        tenth_lord_d1_sign = canonical_by_english[tenth_lord_point.sign.lower()]
        _, d9_sign_index, d9_degree = _d9_position(tenth_lord_point)
        d9_rashi = rashi_by_index[d9_sign_index]
        indicator = d9_rashi.lord

        if indicator not in condition_cache:
            condition_cache[indicator] = _condition_snapshot(
                indicator,
                points,
                canonical_by_english,
                graha_references,
            )

        themes = _vocation_themes(indicator)
        income_sources = _income_sources(occupants)
        aspects = _aspects_to_sign(tenth_sign_index, points)
        evidence = [
            CareerEvidence(
                rule_id="VM-BJ-C10-INCOME-SOURCE-EVAL-001",
                condition="tenth_sign_occupants",
                value=",".join(occupants) if occupants else "none",
                reason=(
                    f"The 10th sign from {reference_point.value} is "
                    f"{tenth_rashi.canonical_id}; its classical occupants are retained."
                ),
            ),
            CareerEvidence(
                rule_id="VM-BJ-C10-NAVAMSA-LORD-EVAL-001",
                condition="karmājīva_indicator",
                value=indicator,
                reason=(
                    f"The 10th lord is {tenth_lord}; it occupies "
                    f"{d9_rashi.canonical_id} in D9, ruled by {indicator}."
                ),
            ),
            CareerEvidence(
                rule_id=_vocation_rule_id(indicator),
                condition="vocation_theme_mapping",
                value=indicator,
                reason=(
                    f"Chapter 10 vocation themes registered for {indicator} are returned "
                    "without choosing a single modern profession."
                ),
            ),
            CareerEvidence(
                rule_id="VM-BJ-C10-SUPPORT-FACTS-EVAL-001",
                condition="unweighted_support",
                value="not_ranked",
                reason=(
                    "Dignity, conjunction, and aspect facts are exposed, but no final "
                    "strength score or cancellation rule is applied."
                ),
            ),
        ]

        channels.append(
            CareerChannel(
                reference_point=reference_point,
                reference_sign_index=reference_sign_index,
                reference_sign=reference_sign,
                tenth_sign_index=tenth_sign_index,
                tenth_sign=tenth_rashi.canonical_id,
                tenth_house_occupants=occupants,
                income_source_indications=income_sources,
                tenth_lord=tenth_lord,
                tenth_lord_d1_sign=tenth_lord_d1_sign,
                tenth_lord_d1_house=tenth_lord_point.house,
                tenth_lord_d1_degree_in_sign=tenth_lord_point.degree_in_sign,
                tenth_lord_d9_sign_index=d9_sign_index,
                tenth_lord_d9_sign=d9_rashi.canonical_id,
                tenth_lord_d9_degree_in_sign=round(d9_degree, 8),
                karmājīva_indicator_graha=indicator,
                vocation_themes=themes,
                indicator_condition=condition_cache[indicator],
                aspects_to_tenth_sign=aspects,
                evidence=evidence,
            )
        )

    references_by_indicator: dict[str, list[CareerReferencePoint]] = defaultdict(list)
    for channel in channels:
        references_by_indicator[channel.karmājīva_indicator_graha].append(
            channel.reference_point
        )

    candidates = [
        CareerCandidate(
            graha=graha,
            derived_from=reference_points,
            repetition_count=len(reference_points),
            vocation_themes=_vocation_themes(graha),
            indicator_condition=condition_cache[graha],
            rule_ids=[
                "VM-BJ-C10-NAVAMSA-LORD-EVAL-001",
                _vocation_rule_id(graha),
                "VM-BJ-C10-SUPPORT-FACTS-EVAL-001",
            ],
        )
        for graha, reference_points in references_by_indicator.items()
    ]

    return ClassicalCareerResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=d1.time,
        coordinates=d1.coordinates,
        ayanamsha_degrees=d1.ayanamsha_degrees,
        channels=channels,
        candidates=candidates,
        primary_indicator=None,
        ranking_applied=False,
        excluded_points=["rahu", "ketu"],
        metadata=d1.metadata,
        caveats=[
            "The result contains vocation themes, not a guaranteed profession.",
            "Lagna, Moon, and Sun channels are all retained as the source commentary directs.",
            "Repeated indicators are counted but are not automatically declared dominant.",
            "Modern examples explain classical categories and are not new textual rules.",
            "Natural friendship, cancellations, and weighted strength remain future work.",
            "Rahu and Ketu are excluded from the seven-Graha Chapter 10 mapping.",
        ],
    )
