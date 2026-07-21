"""Tests for immutable internal Skyfield/JPL golden-chart baselines."""

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from app.engine import classical_validation_baselines
from app.engine.classical_validation_baselines import (
    get_jpl_baseline_case,
    load_jpl_baseline_manifest,
    verify_current_jpl_baselines,
    verify_jpl_baseline_storage,
)
from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1/validation/baseline"
EXPECTED_BASELINE_SET_DIGEST = (
    "e4c97e2c62ce380dfd361f645cc18682849085b823541ae509edd2d1f3568da0"
)
EXPECTED_CASE_SET_DIGEST = (
    "5dcd67cd142e49127cdb62165ca8e1ccb7b28f58fabbf3612eeca42c5392f624"
)


def test_jpl_baseline_manifest_is_versioned_and_digest_locked() -> None:
    manifest = load_jpl_baseline_manifest()

    assert manifest.baseline_set_id == "jyothisyam_jpl_de440s_golden_baselines_v1"
    assert manifest.baseline_set_version == "1.0.0"
    assert manifest.snapshot_schema_version == "1.0.0"
    assert manifest.case_set_digest == EXPECTED_CASE_SET_DIGEST
    assert manifest.baseline_set_digest == EXPECTED_BASELINE_SET_DIGEST
    assert manifest.calculation_profile == "south_indian_drik_lahiri_jpl_de440s_v1"
    assert manifest.astronomical_provider == "skyfield_jpl"
    assert manifest.ephemeris_model == "de440s"
    assert manifest.provider_version == "1.54"
    assert manifest.case_count == 12
    assert len(manifest.cases) == 12


def test_jpl_baseline_storage_integrity_passes() -> None:
    report = verify_jpl_baseline_storage()

    assert report.verified is True
    assert report.expected_case_count == 12
    assert report.loaded_case_count == 12
    assert report.case_set_digest_match is True
    assert report.baseline_set_digest_match is True
    assert report.missing_case_ids == []
    assert report.unexpected_case_ids == []
    assert report.duplicate_case_ids == []
    assert report.invalid_snapshot_digest_case_ids == []
    assert report.issues == []
    assert report.external_reference_validation_complete is False


def test_one_committed_baseline_is_readable_and_not_external_evidence() -> None:
    result = get_jpl_baseline_case("gc_india_nagarjuna_sagar_1998")

    assert result.snapshot_digest == (
        "9e6f72e95dfa96b8e445ce686a6c12a48ecf4ee29a9fb2a4ec67be0e52d3d4d9"
    )
    assert result.snapshot.ascendant_longitude == 246.88818395
    assert result.snapshot.point_longitudes is not None
    assert result.snapshot.point_longitudes["sun"] == 188.75805003
    assert result.snapshot.d1_signs is not None
    assert result.snapshot.d1_signs["ascendant"] == 9
    assert result.internal_regression_baseline is True
    assert result.external_reference_validation_complete is False


def test_tampered_case_file_fails_storage_integrity(
    monkeypatch,
    tmp_path: Path,
) -> None:
    original = classical_validation_baselines._baseline_directory()
    copied = tmp_path / "jpl_de440s_v1"
    shutil.copytree(original, copied)
    case_path = copied / "gc_india_nagarjuna_sagar_1998.json"
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    payload["snapshot"]["point_longitudes"]["sun"] += 1.0
    case_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(
        classical_validation_baselines,
        "_baseline_directory",
        lambda: copied,
    )

    report = verify_jpl_baseline_storage()

    assert report.verified is False
    assert "gc_india_nagarjuna_sagar_1998" in report.invalid_snapshot_digest_case_ids
    assert report.baseline_set_digest_match is False
    assert report.issues


def test_current_jpl_engine_matches_all_committed_baselines() -> None:
    report = verify_current_jpl_baselines()

    assert report.passed is True
    assert report.case_count == 12
    assert report.matched_case_count == 12
    assert report.mismatched_case_count == 0
    assert all(case.matched for case in report.cases)
    assert all(case.mismatched_field_paths == [] for case in report.cases)
    assert report.external_reference_validation_complete is False


def test_jpl_baseline_routes_are_public_and_truthful() -> None:
    manifest = client.get(f"{BASE_PATH}/manifest")
    integrity = client.get(f"{BASE_PATH}/integrity")
    case = client.get(f"{BASE_PATH}/cases/gc_india_nagarjuna_sagar_1998")
    missing = client.get(f"{BASE_PATH}/cases/missing_case")

    assert manifest.status_code == 200, manifest.json()
    assert manifest.json()["baseline_set_digest"] == EXPECTED_BASELINE_SET_DIGEST
    assert integrity.status_code == 200, integrity.json()
    assert integrity.json()["verified"] is True
    assert case.status_code == 200, case.json()
    assert case.json()["external_reference_validation_complete"] is False
    assert missing.status_code == 404

    paths = client.get("/openapi.json").json()["paths"]
    assert f"{BASE_PATH}/manifest" in paths
    assert f"{BASE_PATH}/integrity" in paths
    assert f"{BASE_PATH}/cases/{{case_id}}" in paths
    assert f"{BASE_PATH}/verify-current" in paths
