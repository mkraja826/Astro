"""Rule registrations for Brihat Jataka planetary relationships."""

from app.engine.classical_dasha_rules import (
    extend_varahamihira_profile as extend_dasha_profile,
)
from app.engine.classical_dasha_rules import (
    extend_varahamihira_rules as extend_dasha_rules,
)
from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

RELATIONSHIPS_ENDPOINT = "/v1/classical/varahamihira_v1/relationships"

RELATIONSHIP_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-NATURAL-RELATIONSHIP-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.16-2.17",
        citation_precision=CitationPrecision.VERSE,
        topic="natural_planetary_relationships",
        statement=(
            "The seven classical Grahas receive directional natural friend, neutral, "
            "or enemy relationships from the tables stated in verses 2.16 and 2.17."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "source_graha",
            "target_graha",
            "natural_relationship",
        ],
        notes=[
            "Natural relationship is directional and must not be assumed symmetric.",
            "Rahu and Ketu are excluded from this seven-Graha table.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-TEMPORARY-RELATIONSHIP-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.18",
        citation_precision=CitationPrecision.VERSE,
        topic="temporary_planetary_relationships",
        statement=(
            "Grahas in the 2nd, 3rd, 4th, 10th, 11th, or 12th sign from one "
            "another are temporary friends; other separations are temporary enemies."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "target_relative_house",
            "temporary_relationship",
            "mutual_pairs",
        ],
        notes=[
            "The calculation uses inclusive whole-sign distance in the natal D1 chart.",
            "The alternate exaltation-lord opinion mentioned in the verse is not enabled.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-COMPOUND-RELATIONSHIP-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.18",
        citation_precision=CitationPrecision.VERSE,
        topic="compound_planetary_relationships",
        statement=(
            "Natural and temporary relations are combined into great friend, friend, "
            "neutral, enemy, or great enemy classifications."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "natural_relationship",
            "temporary_relationship",
            "compound_relationship",
        ],
        notes=[
            "The fivefold result is categorical and receives no numeric weight in v1.",
            "Cancellation and final strength ranking remain separate milestones.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add relationship capability after all earlier profile extensions."""

    extended = extend_dasha_profile(profile)
    endpoints = list(extended.endpoints)
    if RELATIONSHIPS_ENDPOINT not in endpoints:
        endpoints.append(RELATIONSHIPS_ENDPOINT)

    return extended.model_copy(
        update={
            "profile_version": "1.6.0",
            "relationships_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "Natural relationships are directional; temporary relationships are mutual.",
                "Only the seven classical Grahas are included in relationship matrices.",
                "Compound relationship labels are not numerical strength scores.",
                "No cancellation, prediction, or longevity judgment is applied.",
                "The evaluator does not alter any existing calculation endpoint.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append relationship rules after all earlier profile registrations."""

    extended = extend_dasha_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in RELATIONSHIP_RULES),
        ],
    )
