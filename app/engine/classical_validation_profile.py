"""Profile extension for the external golden-chart validation harness."""

from app.engine.classical_weighting_profile import (
    extend_varahamihira_profile as extend_weighting_profile,
)
from app.engine.classical_weighting_profile import (
    extend_varahamihira_rules as extend_weighting_rules,
)
from app.schemas.classical import ClassicalProfileResponse, RuleRegistryResponse

VALIDATION_PROFILE_ENDPOINT = "/v1/classical/varahamihira_v1/validation/profile"
VALIDATION_CASES_ENDPOINT = "/v1/classical/varahamihira_v1/validation/cases"
VALIDATION_COMPARE_ENDPOINT = "/v1/classical/varahamihira_v1/validation/compare"


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Advertise the validation harness while preserving incomplete status."""

    extended = extend_weighting_profile(profile)
    endpoints = list(extended.endpoints)
    for endpoint in (
        VALIDATION_PROFILE_ENDPOINT,
        VALIDATION_CASES_ENDPOINT,
        VALIDATION_COMPARE_ENDPOINT,
    ):
        if endpoint not in endpoints:
            endpoints.append(endpoint)

    return extended.model_copy(
        update={
            "profile_version": "1.9.0",
            "endpoints": endpoints,
            "caveats": [
                "Twelve globally diverse validation inputs are frozen in case set v1.",
                "The harness accepts partial snapshots and reports field-level differences.",
                "No external software snapshots are approved or committed yet.",
                "Two independent external sources per case remain required.",
                "Validation disagreements are documented rather than majority-voted.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Keep validation mechanics outside the classical textual rule registry."""

    return extend_weighting_rules(registry)
