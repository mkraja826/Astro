"""Rule registrations for transparent strength and cancellation boundaries."""

from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.engine.classical_relationship_rules import (
    extend_varahamihira_profile as extend_relationship_profile,
)
from app.engine.classical_relationship_rules import (
    extend_varahamihira_rules as extend_relationship_rules,
)
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

STRENGTH_ENDPOINT = "/v1/classical/varahamihira_v1/strength"

STRENGTH_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-STRENGTH-FACTOR-FRAMEWORK-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="transparent_unweighted_strength_factors",
        statement=(
            "Registered dignity, Vargottama, retrograde, aspect, conjunction, and "
            "relationship facts are assembled into supporting, challenging, and "
            "contextual evidence buckets without numerical weights."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "grahas",
            "factors",
            "sign_lord_relationship",
            "weights_applied",
            "ranking_applied",
        ],
        notes=[
            "This is an implementation framework over already registered source rules.",
            "Evidence categories are not a strongest-planet score.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C09-STRENGTH-BINDU-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=9,
        verse_reference="9.1-9.8",
        citation_precision=CitationPrecision.VERSE,
        topic="raw_ashtakavarga_strength_context",
        statement=(
            "Raw Bhinnashtakavarga and Sarvashtakavarga bindus at each Graha's "
            "occupied sign are retained as contextual facts without reductions or "
            "predictive thresholds."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "bhinnashtakavarga_bindus_in_occupied_sign",
            "sarvashtakavarga_bindus_in_occupied_sign",
        ],
        notes=[
            "Bindu values are not converted into numeric planetary-strength weights.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-CANCELLATION-SOURCE-BOUNDARY-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="debilitation_cancellation_source_boundary",
        statement=(
            "The profile applies no debilitation-cancellation formula unless a "
            "verse-level rule is explicitly registered for this immutable source profile."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "cancellation_policy",
            "cancellation",
            "cancellations_applied",
        ],
        notes=[
            "This is a source-integrity boundary, not a claim that other texts lack rules.",
            "Later Neecha Bhanga conventions require a separate versioned source profile.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add strength-framework capability after relationship extensions."""

    extended = extend_relationship_profile(profile)
    endpoints = list(extended.endpoints)
    if STRENGTH_ENDPOINT not in endpoints:
        endpoints.append(STRENGTH_ENDPOINT)

    return extended.model_copy(
        update={
            "profile_version": "1.7.0",
            "endpoints": endpoints,
            "caveats": [
                "Strength factors remain categorical and unweighted.",
                "No strongest-planet ranking is produced.",
                "No debilitation cancellation is activated without a registered source rule.",
                "Later cross-text Neecha Bhanga conventions are outside varahamihira_v1.",
                "No prediction, birth-risk, or longevity judgment is applied.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append strength and cancellation-boundary registrations."""

    extended = extend_relationship_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in STRENGTH_RULES),
        ],
    )
