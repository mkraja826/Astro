"""Tests for external Jyotisha snapshot normalization."""

import pytest
from fastapi.testclient import TestClient

from app.engine.classical_validation_imports import (
    ExternalSnapshotNormalizationError,
    normalize_external_snapshot,
)
from app.main import app
from app.schemas.classical_validation_imports import ExternalSnapshotImportRequest

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1/validation"
SOURCE = {
    "source_name": "Independent Jyotisha Program",
    "source_version": "test-export-1",
    "source_kind": "external_software",
    "calculation_notes": [
        "Sidereal zodiac",
        "Chitrapaksha ayanamsha",
        "True node",
    ],
}


def _request(payload: dict[str, object]) -> ExternalSnapshotImportRequest:
    return ExternalSnapshotImportRequest.model_validate(
        {
            "source": SOURCE,
            "format": "generic_json_v1",
            "payload": payload,
        }
    )


def test_normalizer_converts_common_planet_sign_and_group_aliases() -> None:
    request = _request(
        {
            "chart": {
                "ayanamsa": "23.81619793",
                "lagna_longitude": 246.88818395,
                "planetary_longitudes": {
                    "Surya": 188.75805003,
                    "Chandra": 252.2537349,
                    "Kuja": 137.48582616,
                    "Budha": 207.31073938,
                    "Guru": 324.9137552,
                    "Shukra": 187.74322029,
                    "Shani": 6.14956735,
                    "True Node": 125.20717069,
                    "Ketu": 305.20717069,
                },
                "rasi_signs": {
                    "Lagna": "Dhanu",
                    "Surya": "Libra",
                    "Chandra": 9,
                },
                "navamsha_signs": {
                    "Lagna": "Mithuna",
                    "Surya": "Sagittarius",
                    "Chandra": "Cancer",
                },
                "dignities": {
                    "Surya": "debilitated",
                    "Shukra": "own",
                },
                "vargottama": {
                    "Surya": "false",
                    "Shukra": False,
                },
            }
        }
    )

    result = normalize_external_snapshot(request)

    assert result.normalization_profile == "jyothisyam_external_snapshot_normalizer_v1"
    assert result.snapshot.ayanamsha_degrees == 23.81619793
    assert result.snapshot.ascendant_longitude == 246.88818395
    assert result.snapshot.point_longitudes is not None
    assert result.snapshot.point_longitudes["sun"] == 188.75805003
    assert result.snapshot.point_longitudes["rahu"] == 125.20717069
    assert result.snapshot.d1_signs == {
        "ascendant": 9,
        "sun": 7,
        "moon": 9,
    }
    assert result.snapshot.d9_signs == {
        "ascendant": 3,
        "sun": 9,
        "moon": 4,
    }
    assert result.snapshot.dignity == {
        "sun": "debilitation_sign",
        "venus": "own_sign",
    }
    assert result.snapshot.vargottama == {"sun": False, "venus": False}
    assert result.ignored_paths == []
    assert any("verify the source node convention" in item for item in result.warnings)


def test_normalizer_accepts_planet_lists_and_reports_ignored_fields() -> None:
    result = normalize_external_snapshot(
        _request(
            {
                "planets": [
                    {"name": "Sun", "longitude": 10.5},
                    {"graha": "Chandra", "degrees": 20.25},
                    {"body": "Pluto", "longitude": 30.0},
                ],
                "software_theme": "dark",
            }
        )
    )

    assert result.snapshot.point_longitudes == {"sun": 10.5, "moon": 20.25}
    assert "software_theme" in result.ignored_paths
    assert "planets[2]" in result.ignored_paths
    assert any("Pluto" in item for item in result.warnings)


def test_normalizer_rejects_internal_baseline_provenance() -> None:
    request = ExternalSnapshotImportRequest.model_validate(
        {
            "source": {
                **SOURCE,
                "source_kind": "internal_baseline",
            },
            "payload": {"ayanamsha": 24.0},
        }
    )

    with pytest.raises(
        ExternalSnapshotNormalizationError,
        match="does not accept internal_baseline",
    ):
        normalize_external_snapshot(request)


def test_normalizer_rejects_payload_without_supported_snapshot_fields() -> None:
    with pytest.raises(
        ExternalSnapshotNormalizationError,
        match="Normalized external snapshot is invalid",
    ):
        normalize_external_snapshot(_request({"software_theme": "dark"}))


def test_external_normalization_route_is_public_and_does_not_require_jpl() -> None:
    response = client.post(
        f"{BASE_PATH}/normalize/external",
        json={
            "source": SOURCE,
            "format": "generic_json_v1",
            "payload": {
                "ayanamsa": 23.8,
                "longitudes": {"Surya": 188.75, "Chandra": 252.25},
                "rashi_signs": {"Surya": "Libra", "Chandra": "Sagittarius"},
            },
        },
    )
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["snapshot"]["point_longitudes"] == {
        "sun": 188.75,
        "moon": 252.25,
    }
    assert payload["snapshot"]["d1_signs"] == {"sun": 7, "moon": 9}
    assert payload["source"]["source_name"] == "Independent Jyotisha Program"

    paths = client.get("/openapi.json").json()["paths"]
    assert f"{BASE_PATH}/normalize/external" in paths


def test_external_normalization_route_returns_422_for_unusable_export() -> None:
    response = client.post(
        f"{BASE_PATH}/normalize/external",
        json={
            "source": SOURCE,
            "payload": {"software_theme": "dark"},
        },
    )

    assert response.status_code == 422
    assert "Normalized external snapshot is invalid" in response.json()["detail"]
