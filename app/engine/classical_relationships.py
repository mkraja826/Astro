"""Deterministic Brihat Jataka 2.16-2.18 planetary relationships."""

from itertools import combinations
from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_reference import PROFILE_ID, get_varahamihira_rashis
from app.schemas.charts import ChartRequest, ChartType
from app.schemas.classical_relationships import (
    ClassicalRelationshipsRequest,
    ClassicalRelationshipsResponse,
    CompoundRelationship,
    DirectedGrahaRelationship,
    MutualGrahaPair,
    NaturalRelationship,
    RelationshipGrahaPosition,
    TemporaryRelationship,
)

CLASSICAL_GRAHAS = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)

TEMPORARY_FRIEND_HOUSES = frozenset({2, 3, 4, 10, 11, 12})

NATURAL_RELATIONSHIPS: dict[str, dict[str, NaturalRelationship]] = {
    "sun": {
        "moon": NaturalRelationship.FRIEND,
        "mars": NaturalRelationship.FRIEND,
        "mercury": NaturalRelationship.NEUTRAL,
        "jupiter": NaturalRelationship.FRIEND,
        "venus": NaturalRelationship.ENEMY,
        "saturn": NaturalRelationship.ENEMY,
    },
    "moon": {
        "sun": NaturalRelationship.FRIEND,
        "mars": NaturalRelationship.NEUTRAL,
        "mercury": NaturalRelationship.FRIEND,
        "jupiter": NaturalRelationship.NEUTRAL,
        "venus": NaturalRelationship.NEUTRAL,
        "saturn": NaturalRelationship.NEUTRAL,
    },
    "mars": {
        "sun": NaturalRelationship.FRIEND,
        "moon": NaturalRelationship.FRIEND,
        "mercury": NaturalRelationship.ENEMY,
        "jupiter": NaturalRelationship.FRIEND,
        "venus": NaturalRelationship.NEUTRAL,
        "saturn": NaturalRelationship.NEUTRAL,
    },
    "mercury": {
        "sun": NaturalRelationship.FRIEND,
        "moon": NaturalRelationship.ENEMY,
        "mars": NaturalRelationship.NEUTRAL,
        "jupiter": NaturalRelationship.NEUTRAL,
        "venus": NaturalRelationship.FRIEND,
        "saturn": NaturalRelationship.NEUTRAL,
    },
    "jupiter": {
        "sun": NaturalRelationship.FRIEND,
        "moon": NaturalRelationship.FRIEND,
        "mars": NaturalRelationship.FRIEND,
        "mercury": NaturalRelationship.ENEMY,
        "venus": NaturalRelationship.ENEMY,
        "saturn": NaturalRelationship.NEUTRAL,
    },
    "venus": {
        "sun": NaturalRelationship.ENEMY,
        "moon": NaturalRelationship.ENEMY,
        "mars": NaturalRelationship.NEUTRAL,
        "mercury": NaturalRelationship.FRIEND,
        "jupiter": NaturalRelationship.NEUTRAL,
        "saturn": NaturalRelationship.FRIEND,
    },
    "saturn": {
        "sun": NaturalRelationship.ENEMY,
        "moon": NaturalRelationship.ENEMY,
        "mars": NaturalRelationship.ENEMY,
        "mercury": NaturalRelationship.FRIEND,
        "jupiter": NaturalRelationship.NEUTRAL,
        "venus": NaturalRelationship.FRIEND,
    },
}

_COMPOUND_RELATIONSHIPS = {
    (NaturalRelationship.FRIEND, TemporaryRelationship.FRIEND): (
        CompoundRelationship.GREAT_FRIEND
    ),
    (NaturalRelationship.FRIEND, TemporaryRelationship.ENEMY): (
        CompoundRelationship.NEUTRAL
    ),
    (NaturalRelationship.NEUTRAL, TemporaryRelationship.FRIEND): (
        CompoundRelationship.FRIEND
    ),
    (NaturalRelationship.NEUTRAL, TemporaryRelationship.ENEMY): (
        CompoundRelationship.ENEMY
    ),
    (NaturalRelationship.ENEMY, TemporaryRelationship.FRIEND): (
        CompoundRelationship.NEUTRAL
    ),
    (NaturalRelationship.ENEMY, TemporaryRelationship.ENEMY): (
        CompoundRelationship.GREAT_ENEMY
    ),
}

NATURAL_RULE_ID = "VM-BJ-C02-NATURAL-RELATIONSHIP-EVAL-001"
TEMPORARY_RULE_ID = "VM-BJ-C02-TEMPORARY-RELATIONSHIP-EVAL-001"
COMPOUND_RULE_ID = "VM-BJ-C02-COMPOUND-RELATIONSHIP-EVAL-001"


def relative_house(source_sign_index: int, target_sign_index: int) -> int:
    """Return the target's inclusive whole-sign distance from the source."""

    return ((target_sign_index - source_sign_index) % 12) + 1


def natural_relationship(
    source_graha: str,
    target_graha: str,
) -> NaturalRelationship:
    """Return the directional permanent relationship from source to target."""

    if source_graha == target_graha:
        raise ValueError("Natural relationship requires two different Grahas")
    try:
        return NATURAL_RELATIONSHIPS[source_graha][target_graha]
    except KeyError as exc:
        raise ValueError(
            "Natural relationships are available only for the seven classical Grahas"
        ) from exc


def temporary_relationship(
    source_sign_index: int,
    target_sign_index: int,
) -> tuple[TemporaryRelationship, int]:
    """Return natal temporary relation and target relative house."""

    target_house = relative_house(source_sign_index, target_sign_index)
    relation = (
        TemporaryRelationship.FRIEND
        if target_house in TEMPORARY_FRIEND_HOUSES
        else TemporaryRelationship.ENEMY
    )
    return relation, target_house


def compound_relationship(
    natural: NaturalRelationship,
    temporary: TemporaryRelationship,
) -> CompoundRelationship:
    """Combine natural and temporary relations into the fivefold result."""

    return _COMPOUND_RELATIONSHIPS[(natural, temporary)]


def evaluate_relationship(
    source_graha: str,
    target_graha: str,
    source_sign_index: int,
    target_sign_index: int,
) -> tuple[NaturalRelationship, TemporaryRelationship, CompoundRelationship, int]:
    """Evaluate one complete directed relationship without constructing a response."""

    natural = natural_relationship(source_graha, target_graha)
    temporary, target_house = temporary_relationship(
        source_sign_index,
        target_sign_index,
    )
    compound = compound_relationship(natural, temporary)
    return natural, temporary, compound, target_house


def calculate_varahamihira_relationships(
    request: ClassicalRelationshipsRequest,
) -> ClassicalRelationshipsResponse:
    """Return all directed and mutual relationships among the seven Grahas."""

    d1 = calculate_chart(
        ChartRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        ),
        ChartType.D1_RASI,
    )
    rashis = get_varahamihira_rashis().rashis
    canonical_by_english = {
        rashi.english_name.lower(): rashi.canonical_id for rashi in rashis
    }
    points = {
        point.name: point for point in d1.points if point.name in CLASSICAL_GRAHAS
    }

    positions = [
        RelationshipGrahaPosition(
            graha=graha,
            source_longitude=points[graha].source_longitude,
            sign_index=points[graha].sign_index,
            sign=canonical_by_english[points[graha].sign.lower()],
            house=points[graha].house,
        )
        for graha in CLASSICAL_GRAHAS
    ]

    directed: list[DirectedGrahaRelationship] = []
    directed_lookup: dict[tuple[str, str], DirectedGrahaRelationship] = {}
    for source_graha in CLASSICAL_GRAHAS:
        source = points[source_graha]
        for target_graha in CLASSICAL_GRAHAS:
            if source_graha == target_graha:
                continue
            target = points[target_graha]
            natural, temporary, compound, target_house = evaluate_relationship(
                source_graha,
                target_graha,
                source.sign_index,
                target.sign_index,
            )
            result = DirectedGrahaRelationship(
                source_graha=source_graha,
                target_graha=target_graha,
                source_sign_index=source.sign_index,
                source_sign=canonical_by_english[source.sign.lower()],
                target_sign_index=target.sign_index,
                target_sign=canonical_by_english[target.sign.lower()],
                target_relative_house=target_house,
                natural_relationship=natural,
                temporary_relationship=temporary,
                compound_relationship=compound,
                rule_ids=[NATURAL_RULE_ID, TEMPORARY_RULE_ID, COMPOUND_RULE_ID],
                reason=(
                    f"{target_graha} is in the {target_house}th sign from "
                    f"{source_graha}; natural {natural.value} plus temporary "
                    f"{temporary.value} gives {compound.value}."
                ),
            )
            directed.append(result)
            directed_lookup[(source_graha, target_graha)] = result

    mutual_pairs = []
    for graha_a, graha_b in combinations(CLASSICAL_GRAHAS, 2):
        a_to_b = directed_lookup[(graha_a, graha_b)]
        b_to_a = directed_lookup[(graha_b, graha_a)]
        if a_to_b.temporary_relationship != b_to_a.temporary_relationship:
            raise RuntimeError("Temporary relationship symmetry invariant failed")
        mutual_pairs.append(
            MutualGrahaPair(
                graha_a=graha_a,
                graha_b=graha_b,
                a_relative_house_from_b=b_to_a.target_relative_house,
                b_relative_house_from_a=a_to_b.target_relative_house,
                temporary_relationship=a_to_b.temporary_relationship,
                a_to_b_compound=a_to_b.compound_relationship,
                b_to_a_compound=b_to_a.compound_relationship,
                rule_ids=[TEMPORARY_RULE_ID, COMPOUND_RULE_ID],
            )
        )

    return ClassicalRelationshipsResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=d1.time,
        coordinates=d1.coordinates,
        ayanamsha_degrees=d1.ayanamsha_degrees,
        positions=positions,
        directed_relationships=directed,
        mutual_pairs=mutual_pairs,
        excluded_points=["rahu", "ketu"],
        scoring_applied=False,
        metadata=d1.metadata,
        caveats=[
            "Natural relationships are directional and limited to seven classical Grahas.",
            "Temporary friendship uses whole-sign natal separation only.",
            "The alternate exaltation-lord opinion mentioned in 2.18 is not enabled.",
            "Compound labels are classifications, not numeric strength scores.",
            "No cancellation, event prediction, or longevity judgment is applied.",
        ],
    )
