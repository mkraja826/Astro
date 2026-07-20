"""Deterministic Varahamihira aspect and whole-sign house-influence evaluation."""

from dataclasses import dataclass
from itertools import combinations
from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_reference import (
    PROFILE_ID,
    get_varahamihira_rashis,
)
from app.schemas.charts import ChartPoint, ChartRequest, ChartType
from app.schemas.classical_aspects import (
    AspectRay,
    AspectStrengthLabel,
    ClassicalAspectsRequest,
    ClassicalAspectsResponse,
    ConjunctionRecord,
    HouseAspectInfluence,
    HouseInfluence,
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

_GENERAL_ASPECTS = (
    (3, 0.25, AspectStrengthLabel.QUARTER),
    (4, 0.75, AspectStrengthLabel.THREE_QUARTERS),
    (5, 0.50, AspectStrengthLabel.HALF),
    (7, 1.00, AspectStrengthLabel.FULL),
    (8, 0.75, AspectStrengthLabel.THREE_QUARTERS),
    (9, 0.50, AspectStrengthLabel.HALF),
    (10, 0.25, AspectStrengthLabel.QUARTER),
)

_SPECIAL_FULL_ASPECTS = {
    "mars": {4, 8},
    "jupiter": {5, 9},
    "saturn": {3, 10},
}


@dataclass(frozen=True)
class AspectSpecification:
    """Pure aspect rule resolved for one Graha and relative house."""

    relative_house: int
    strength_fraction: float
    strength_label: AspectStrengthLabel
    is_special_full: bool
    rule_ids: tuple[str, ...]


def aspect_specifications_for_graha(graha: str) -> tuple[AspectSpecification, ...]:
    """Return the seven Bṛhat Jātaka 2.13 aspect strengths for one Graha."""

    if graha not in _CLASSICAL_GRAHAS:
        raise ValueError(f"Unsupported classical Graha: {graha}")

    special_houses = _SPECIAL_FULL_ASPECTS.get(graha, set())
    specifications: list[AspectSpecification] = []
    for relative_house, fraction, label in _GENERAL_ASPECTS:
        is_special_full = relative_house in special_houses
        rule_ids = ["VM-BJ-C02-ASPECT-STRENGTH-EVAL-001"]
        if is_special_full:
            fraction = 1.0
            label = AspectStrengthLabel.FULL
            rule_ids.append("VM-BJ-C02-SPECIAL-ASPECT-EVAL-001")
        specifications.append(
            AspectSpecification(
                relative_house=relative_house,
                strength_fraction=fraction,
                strength_label=label,
                is_special_full=is_special_full,
                rule_ids=tuple(rule_ids),
            )
        )
    return tuple(specifications)


def target_sign_index(source_sign_index: int, relative_house: int) -> int:
    """Count inclusively from a source sign to an aspected whole sign."""

    if not 1 <= source_sign_index <= 12:
        raise ValueError("source_sign_index must be between 1 and 12")
    if not 1 <= relative_house <= 12:
        raise ValueError("relative_house must be between 1 and 12")
    return ((source_sign_index + relative_house - 2) % 12) + 1


def _angular_separation(first_longitude: float, second_longitude: float) -> float:
    separation = abs((first_longitude - second_longitude) % 360.0)
    return min(separation, 360.0 - separation)


def _canonical_sign_maps() -> tuple[dict[int, object], dict[str, str]]:
    rashis = get_varahamihira_rashis().rashis
    by_index = {rashi.index: rashi for rashi in rashis}
    by_english = {rashi.english_name.lower(): rashi.canonical_id for rashi in rashis}
    return by_index, by_english


def _classical_points(points: list[ChartPoint]) -> dict[str, ChartPoint]:
    return {point.name: point for point in points if point.name in _CLASSICAL_GRAHAS}


def calculate_varahamihira_aspects(
    request: ClassicalAspectsRequest,
) -> ClassicalAspectsResponse:
    """Evaluate fractional Graha aspects, conjunctions, and house influence."""

    d1 = calculate_chart(
        ChartRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        ),
        ChartType.D1_RASI,
    )
    rashi_by_index, canonical_by_english = _canonical_sign_maps()
    points = _classical_points(d1.points)
    ascendant_sign_index = d1.ascendant.sign_index
    ascendant_sign = canonical_by_english[d1.ascendant.sign.lower()]

    occupants_by_sign: dict[int, list[str]] = {index: [] for index in range(1, 13)}
    for name in _CLASSICAL_GRAHAS:
        occupants_by_sign[points[name].sign_index].append(name)

    aspects: list[AspectRay] = []
    for source_graha in _CLASSICAL_GRAHAS:
        source = points[source_graha]
        source_sign = canonical_by_english[source.sign.lower()]
        for specification in aspect_specifications_for_graha(source_graha):
            target_index = target_sign_index(
                source.sign_index,
                specification.relative_house,
            )
            target_rashi = rashi_by_index[target_index]
            target_house = ((target_index - ascendant_sign_index) % 12) + 1
            special_note = (
                " The special rule raises this aspect to full strength."
                if specification.is_special_full
                else ""
            )
            aspects.append(
                AspectRay(
                    source_graha=source_graha,
                    source_sign_index=source.sign_index,
                    source_sign=source_sign,
                    source_house=source.house,
                    relative_house=specification.relative_house,
                    target_sign_index=target_index,
                    target_sign=target_rashi.canonical_id,
                    target_house=target_house,
                    strength_fraction=specification.strength_fraction,
                    strength_label=specification.strength_label,
                    is_special_full=specification.is_special_full,
                    target_grahas=list(occupants_by_sign[target_index]),
                    rule_ids=list(specification.rule_ids),
                    reason=(
                        f"{source_graha} in {source_sign} aspects the "
                        f"{specification.relative_house}th sign, {target_rashi.canonical_id}, "
                        f"with {specification.strength_label.value} strength.{special_note}"
                    ),
                )
            )

    conjunctions: list[ConjunctionRecord] = []
    for sign_index, occupants in occupants_by_sign.items():
        if len(occupants) < 2:
            continue
        sign = rashi_by_index[sign_index].canonical_id
        house = ((sign_index - ascendant_sign_index) % 12) + 1
        for first, second in combinations(occupants, 2):
            separation = _angular_separation(
                points[first].source_longitude,
                points[second].source_longitude,
            )
            conjunctions.append(
                ConjunctionRecord(
                    grahas=[first, second],
                    sign_index=sign_index,
                    sign=sign,
                    house=house,
                    angular_separation_degrees=round(separation, 8),
                    rule_ids=["VM-BJ-C02-CONJUNCTION-EVAL-001"],
                    reason=(
                        f"{first} and {second} occupy the same D1 sign, {sign}; "
                        f"their angular separation is {round(separation, 8)} degrees."
                    ),
                )
            )

    conjunctions_by_house: dict[int, list[list[str]]] = {
        house: [] for house in range(1, 13)
    }
    for conjunction in conjunctions:
        conjunctions_by_house[conjunction.house].append(list(conjunction.grahas))

    aspects_by_house: dict[int, list[AspectRay]] = {
        house: [] for house in range(1, 13)
    }
    for aspect in aspects:
        aspects_by_house[aspect.target_house].append(aspect)

    houses: list[HouseInfluence] = []
    for house in range(1, 13):
        sign_index = ((ascendant_sign_index + house - 2) % 12) + 1
        rashi = rashi_by_index[sign_index]
        lord = rashi.lord
        lord_point = points[lord]
        lord_placement_sign = canonical_by_english[lord_point.sign.lower()]
        received = aspects_by_house[house]
        influences = [
            HouseAspectInfluence(
                source_graha=aspect.source_graha,
                relative_house=aspect.relative_house,
                strength_fraction=aspect.strength_fraction,
                strength_label=aspect.strength_label,
                is_special_full=aspect.is_special_full,
                rule_ids=list(aspect.rule_ids),
            )
            for aspect in received
        ]
        full_sources = sorted(
            aspect.source_graha
            for aspect in received
            if aspect.strength_fraction == 1.0
        )
        total_weight = round(
            sum(aspect.strength_fraction for aspect in received),
            8,
        )
        houses.append(
            HouseInfluence(
                house=house,
                sign_index=sign_index,
                sign=rashi.canonical_id,
                contains_ascendant=house == 1,
                lord=lord,
                lord_placement_sign=lord_placement_sign,
                lord_placement_house=lord_point.house,
                occupants=list(occupants_by_sign[sign_index]),
                conjunction_pairs=conjunctions_by_house[house],
                aspects_received=influences,
                total_aspect_weight=total_weight,
                full_aspect_sources=full_sources,
                rule_ids=[
                    "VM-BJ-C01-HOUSE-LORD-EVAL-001",
                    "VM-BJ-C02-HOUSE-INFLUENCE-EVAL-001",
                ],
                reason=(
                    f"House {house} is {rashi.canonical_id}, ruled by {lord}; "
                    f"{lord} occupies house {lord_point.house}. The house receives "
                    f"{len(received)} aspect rays with total fractional weight {total_weight}."
                ),
            )
        )

    return ClassicalAspectsResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=d1.time,
        coordinates=d1.coordinates,
        ayanamsha_degrees=d1.ayanamsha_degrees,
        ascendant_sign_index=ascendant_sign_index,
        ascendant_sign=ascendant_sign,
        aspects=aspects,
        conjunctions=conjunctions,
        houses=houses,
        excluded_points=["rahu", "ketu"],
        metadata=d1.metadata,
        caveats=[
            "This endpoint reports deterministic aspect facts, not predictions.",
            "Brihat Jataka 2.13 fractional aspects are retained, not discarded.",
            "Special full aspects override the general fractional strength.",
            "Conjunction means same-sign occupancy; angular separation is also returned.",
            "House influence uses whole-sign houses from the D1 ascendant.",
            "Rahu and Ketu are excluded from this seven-Graha aspect pass.",
        ],
    )
