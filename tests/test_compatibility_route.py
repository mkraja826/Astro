from datetime import datetime

import pytest
from fastapi import HTTPException

import app.api.routes.compatibility as compatibility_route
from app.schemas.compatibility import DualChartCompatibilityRequest
from app.schemas.positions import BirthInput


def request() -> DualChartCompatibilityRequest:
    return DualChartCompatibilityRequest(
        subject_birth=BirthInput(
            local_datetime=datetime(1998, 10, 26, 10, 28),
            timezone="Asia/Kolkata",
            latitude=16.575,
            longitude=79.312,
        ),
        partner_birth=BirthInput(
            local_datetime=datetime(1999, 5, 14, 8, 15),
            timezone="Asia/Kolkata",
            latitude=17.385,
            longitude=78.487,
        ),
    )


def test_router_exposes_versioned_compatibility_facts_path() -> None:
    paths = {route.path for route in compatibility_route.router.routes}

    assert "/v1/classical/varahamihira_v1/compatibility/facts" in paths


def test_route_translates_calculation_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        compatibility_route,
        "calculate_compatibility_facts",
        lambda _request: (_ for _ in ()).throw(ValueError("invalid compatibility facts")),
    )

    with pytest.raises(HTTPException) as error:
        compatibility_route.compatibility_facts(request())

    assert error.value.status_code == 422
    assert error.value.detail == "invalid compatibility facts"
