"""Profile extension for weighting and external golden-chart validation."""

from app.engine.classical_strength_rules import (
    extend_varahamihira_profile as extend_strength_profile,
)
from app.engine.classical_strength_rules import (
    extend_varahamihira_rules as extend_strength_rules,
)
from app.schemas.classical import ClassicalProfileResponse, RuleRegistryResponse

WEIGHTING_PROFILE_ENDPOINT = "/v1/classical/varahamihira_v1/weighting/profile"
WEIGHTED_STRENGTH_ENDPOINT = "/v1/classical/varahamihira_v1/strength/weighted"
WEIGHTED_CAREER_ENDPOINT = "/v1/classical/varahamihira_v1/career/weighted"
WEIGHTED_DASHA_ENDPOINT = "/v1/classical/varahamihira_v1/dasha/current/weighted"
VALIDATION_PROFILE_ENDPOINT = "/v1/classical/varahamihira_v1/validation/profile"
VALIDATION_CASES_ENDPOINT = "/v1/classical/varahamihira_v1/validation/cases"
VALIDATION_COMPARE_ENDPOINT = "/v1/classical/varahamihira_v1/validation/compare"


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Advertise convention and validation endpoints without creating textual rules."""

    extended = extend_strength_profile(profile)
    endpoints = list(extended.endpoints)
    additional_endpoints = (
        WEIGHTING_PROFILE_ENDPOINT,
        WEIGHTED_STRENGTH_ENDPOINT,
        WEIGHTED_CAREER_ENDPOINT,
        WEIGHTED_DASHA_ENDPOINT,
        VALIDATION_PROFILE_ENDPOINT,
        VALIDATION_CASES_ENDPOINT,
        VALIDATION_COMPARE_ENDPOINT,
    )
    for endpoint in additional_endpoints:
        if endpoint not in endpoints:
            endpoints.append(endpoint)

    return extended.model_copy(
        update={
            "profile_version": "1.9.0",
            "endpoints": endpoints,
            "caveats": [
                "The controlled weighting profile is an API convention, not a textual rule.",
                "Every weighted result embeds its raw unweighted strength evidence.",
                "Weighted career and Dasha routes are additive; old contracts are unchanged.",
                "Twelve globally diverse validation inputs are frozen in case set v1.",
                "No external software snapshots are approved or committed yet.",
                "Two independent external sources per case remain required.",
                "Cancellation adjustments and predictions remain disabled.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Keep API conventions and validation mechanics outside the verse registry."""

    return extend_strength_rules(registry)
