"""Register the source boundary for Chapter 9 transit balance."""

from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.engine.classical_strength_rules import (
    extend_varahamihira_profile as extend_strength_profile,
)
from app.engine.classical_strength_rules import (
    extend_varahamihira_rules as extend_strength_rules,
)
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

TRANSIT_EVALUATION_ENDPOINT = "/v1/classical/varahamihira_v1/transits/evaluate"
TRANSIT_BALANCE_RULE = ClassicalRuleReference(
    rule_id="VM-BJ-C09-TRANSIT-BAV-BALANCE-001",
    profile_id=PROFILE_ID,
    source_id=SOURCE_ID,
    chapter=9,
    verse_reference="9.1-9.7 and edition notes following 9.7",
    citation_precision=CitationPrecision.CHAPTER,
    topic="bhinnashtakavarga_transit_balance",
    statement=(
        "For a Graha transiting a sign, its benefic dots and complementary "
        "malefic lines in that Graha's natal Bhinnashtakavarga are compared; "
        "the difference is expressed in eighths of the Graha's power."
    ),
    implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
    confidence="high",
    data_keys=[
        "body",
        "transit_sign_index",
        "bindus",
        "rekhas",
        "net_eighths",
        "normalized_balance",
        "polarity",
    ],
    notes=[
        "Same-sign balance is arithmetic: bindus minus (8 minus bindus).",
        "Rahu and Ketu are excluded because Chapter 9 provides seven Graha tables.",
        "Upachaya and dignity overrides in the edition notes remain disabled.",
        "No life-domain or event mapping is claimed by this rule.",
    ],
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Advertise the transit evaluator after strength capabilities."""

    extended = extend_strength_profile(profile)
    endpoints = list(extended.endpoints)
    if TRANSIT_EVALUATION_ENDPOINT not in endpoints:
        endpoints.append(TRANSIT_EVALUATION_ENDPOINT)
    return extended.model_copy(
        update={
            "profile_version": "1.11.0",
            "endpoints": endpoints,
            "caveats": [
                *extended.caveats,
                "Chapter 9 transit balance is planet-specific and not a domain forecast.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append the Chapter 9 transit-balance evaluator."""

    extended = extend_strength_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[*extended.rules, TRANSIT_BALANCE_RULE.model_copy(deep=True)],
    )
