from datetime import datetime

import pytest
from pydantic import ValidationError

from app.engine.compatibility_contract import (
    birth_input_fingerprint,
    compatibility_pair_fingerprint,
    compatibility_request_fingerprints,
)
from app.schemas.compatibility import (
    ASHTAKOOTA_MAXIMUM_POINTS,
    ASHTAKOOTA_TOTAL_POINTS,
    COMPATIBILITY_FACTS_VERSION,
    AshtakootaComponent,
    AshtakootaComponentFact,
    CompatibilityFactsResponse,
    CompatibilityNatalFacts,
    DualChartCompatibilityRequest,
)
from app.schemas.positions import BirthInput, CalculationProfile, EngineMetadata


def birth(
    *,
    day: int,
    latitude: float = 16.575,
    longitude: float = 79.312,
) -> BirthInput:
    return BirthInput(
        local_datetime=datetime(1998, 10, day, 10, 28),
        timezone="Asia/Kolkata",
        latitude=latitude,
        longitude=longitude,
        altitude_meters=100,
    )


def request(*, reverse: bool = False) -> DualChartCompatibilityRequest:
    first = birth(day=26)
    second = birth(day=27, latitude=17.385, longitude=78.487)
    if reverse:
        first, second = second, first
    return DualChartCompatibilityRequest(
        subject_birth=first,
        partner_birth=second,
    )


def component_facts() -> list[AshtakootaComponentFact]:
    return [
        AshtakootaComponentFact(
            component=component,
            achieved_points=maximum / 2,
            maximum_points=maximum,
            rule_ids=(f"TEST-{component.value.upper()}",),
            source_kind="convention",
        )
        for component, maximum in ASHTAKOOTA_MAXIMUM_POINTS.items()
    ]


def natal_facts(fingerprint: str) -> CompatibilityNatalFacts:
    return CompatibilityNatalFacts(
        chart_fingerprint=fingerprint,
        ascendant_sign_index=1,
        moon_sign_index=2,
        moon_nakshatra_index=3,
        moon_nakshatra="Krittika",
        moon_pada=2,
        planet_sign_indices={
            "sun": 1,
            "moon": 2,
            "mars": 3,
            "mercury": 4,
            "jupiter": 5,
            "venus": 6,
            "saturn": 7,
        },
    )


def metadata() -> EngineMetadata:
    return EngineMetadata(
        engine="astro",
        engine_version="test",
        provider_version="test",
        ephemeris_model="de440s",
        zodiac="sidereal",
        ayanamsha="lahiri",
        node_type="mean",
        house_system="whole_sign",
        ephemeris_sources=["test-fixture"],
    )


def response() -> CompatibilityFactsResponse:
    subject, partner, pair = compatibility_request_fingerprints(request())
    components = component_facts()
    return CompatibilityFactsResponse(
        request_id="test-request",
        calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        subject_fingerprint=subject,
        partner_fingerprint=partner,
        pair_fingerprint=pair,
        subject=natal_facts(subject),
        partner=natal_facts(partner),
        ashtakoota_components=components,
        total_achieved_points=sum(item.achieved_points for item in components),
        rule_ids=["TEST-COMPATIBILITY-CONTRACT"],
        metadata=metadata(),
        caveats=["Synthetic contract fixture; no compatibility claim."],
    )


def test_request_rejects_names_and_identity_fields() -> None:
    payload = request().model_dump(mode="json")
    payload["subject_name"] = "Not allowed"

    with pytest.raises(ValidationError):
        DualChartCompatibilityRequest.model_validate(payload)

    nested = request().model_dump(mode="json")
    nested["partner_birth"]["full_name"] = "Also not allowed"
    with pytest.raises(ValidationError):
        DualChartCompatibilityRequest.model_validate(nested)


def test_request_requires_pinned_jpl_profile() -> None:
    with pytest.raises(ValidationError, match="pinned JPL DE440s"):
        DualChartCompatibilityRequest(
            subject_birth=birth(day=26),
            partner_birth=birth(day=27),
            calculation_profile=CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1,
        )


def test_birth_fingerprint_is_stable_and_sensitive_to_calculation_inputs() -> None:
    profile = CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    original = birth(day=26)

    first = birth_input_fingerprint(original, profile)
    second = birth_input_fingerprint(original.model_copy(deep=True), profile)
    changed = birth_input_fingerprint(
        original.model_copy(update={"latitude": original.latitude + 0.000001}),
        profile,
    )

    assert first == second
    assert first != changed
    assert len(first) == 64


def test_pair_fingerprint_is_order_sensitive() -> None:
    forward = compatibility_pair_fingerprint(request())
    reversed_pair = compatibility_pair_fingerprint(request(reverse=True))

    assert forward != reversed_pair


def test_component_maximums_are_frozen_and_total_36() -> None:
    assert sum(ASHTAKOOTA_MAXIMUM_POINTS.values()) == ASHTAKOOTA_TOTAL_POINTS

    with pytest.raises(ValidationError, match="maximum_points must be"):
        AshtakootaComponentFact(
            component=AshtakootaComponent.NADI,
            achieved_points=4,
            maximum_points=7,
            rule_ids=["TEST-NADI"],
            source_kind="convention",
        )


def test_response_requires_all_eight_unique_components() -> None:
    payload = response().model_dump(mode="json")
    payload["ashtakoota_components"][-1] = payload["ashtakoota_components"][0]

    with pytest.raises(ValidationError, match="exactly once"):
        CompatibilityFactsResponse.model_validate(payload)


def test_response_total_must_match_component_facts() -> None:
    payload = response().model_dump(mode="json")
    payload["total_achieved_points"] += 1

    with pytest.raises(ValidationError, match="does not match"):
        CompatibilityFactsResponse.model_validate(payload)


def test_serialized_response_contains_no_birth_or_name_fields() -> None:
    payload = response().model_dump(mode="json")
    serialized = response().model_dump_json()

    assert payload["facts_version"] == COMPATIBILITY_FACTS_VERSION
    assert payload["total_maximum_points"] == 36
    assert len(payload["ashtakoota_components"]) == 8
    assert "local_datetime" not in serialized
    assert "subject_birth" not in serialized
    assert "partner_birth" not in serialized
    assert "full_name" not in serialized
