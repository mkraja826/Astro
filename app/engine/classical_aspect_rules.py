"""Rule registrations and profile extensions for classical aspect evaluation."""

from app.engine.classical_condition_rules import (
    extend_varahamihira_profile as extend_condition_profile,
)
from app.engine.classical_condition_rules import (
    extend_varahamihira_rules as extend_condition_rules,
)
from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

ASPECTS_ENDPOINT = "/v1/classical/varahamihira_v1/aspects"

ASPECT_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-ASPECT-STRENGTH-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.13",
        citation_precision=CitationPrecision.VERSE,
        topic="fractional_graha_aspects",
        statement=(
            "All seven classical Grahas aspect the 3rd and 10th with one-quarter, "
            "the 5th and 9th with one-half, the 4th and 8th with three-quarters, "
            "and the 7th with full strength."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "relative_house",
            "strength_fraction",
            "strength_label",
            "target_sign",
            "target_house",
        ],
        notes=[
            "Whole-sign targets are counted inclusively from the Graha's D1 sign.",
            "The fractional aspects are retained in the API instead of being discarded.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-SPECIAL-ASPECT-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.13",
        citation_precision=CitationPrecision.VERSE,
        topic="special_full_graha_aspects",
        statement=(
            "Saturn fully aspects the 3rd and 10th, Jupiter fully aspects the 5th "
            "and 9th, and Mars fully aspects the 4th and 8th."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "source_graha",
            "relative_house",
            "is_special_full",
            "strength_fraction",
        ],
        notes=["A special full aspect overrides the general fractional strength."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-CONJUNCTION-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="same_sign_conjunction",
        statement=(
            "Two classical Grahas occupying the same D1 Rashi are registered as a "
            "same-sign conjunction pair."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="medium",
        data_keys=[
            "grahas",
            "sign",
            "house",
            "angular_separation_degrees",
        ],
        notes=[
            "Same-sign occupancy is an explicit varahamihira_v1 API convention.",
            "The exact angular separation is returned without applying an orb cutoff.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-HOUSE-LORD-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="whole_sign_house_lord_placement",
        statement=(
            "Each whole-sign house receives the lord of its Rashi from the immutable "
            "Chapter 1 lordship table, and that lord's D1 placement is reported."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "house",
            "sign",
            "lord",
            "lord_placement_sign",
            "lord_placement_house",
        ],
        notes=["House 1 begins at the D1 ascendant sign."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-HOUSE-INFLUENCE-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.13",
        citation_precision=CitationPrecision.VERSE,
        topic="house_aspect_influence",
        statement=(
            "A house influence record aggregates its classical Graha occupants, "
            "conjunction pairs, lord placement, and all received aspect rays."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "occupants",
            "conjunction_pairs",
            "aspects_received",
            "total_aspect_weight",
            "full_aspect_sources",
        ],
        notes=[
            "The total aspect weight is a transparent arithmetic sum, not a prediction score.",
            "Rahu and Ketu are excluded from this seven-Graha evaluator.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add aspect capability after applying the condition-profile extension."""

    extended = extend_condition_profile(profile)
    endpoints = list(extended.endpoints)
    if ASPECTS_ENDPOINT not in endpoints:
        endpoints.append(ASPECTS_ENDPOINT)

    return extended.model_copy(
        update={
            "profile_version": "1.2.0",
            "aspects_evaluator_enabled": True,
            "house_influence_evaluator_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "Conditions and aspects are deterministic and non-predictive.",
                "Brihat Jataka 2.13 fractional and special full aspects are retained.",
                "House influence uses whole-sign D1 houses and transparent arithmetic.",
                "The evaluators do not alter D1, D9, Panchanga, or Vimshottari calculations.",
                "Career, Ashtakavarga, Dasha interpretation, and longevity are not included.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append aspect rules after applying all condition-rule extensions."""

    extended = extend_condition_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in ASPECT_RULES),
        ],
    )
