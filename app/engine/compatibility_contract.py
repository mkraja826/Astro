"""Deterministic cache identities for anonymous dual-chart compatibility requests."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.schemas.compatibility import DualChartCompatibilityRequest
from app.schemas.positions import BirthInput, CalculationProfile

BIRTH_FINGERPRINT_VERSION = "birth_input_fingerprint_v1"
PAIR_FINGERPRINT_VERSION = "compatibility_pair_fingerprint_v2"


def _sha256(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _birth_payload(
    birth: BirthInput,
    calculation_profile: CalculationProfile,
) -> dict[str, Any]:
    return {
        "version": BIRTH_FINGERPRINT_VERSION,
        "calculation_profile": calculation_profile.value,
        "local_datetime": birth.local_datetime.isoformat(timespec="microseconds"),
        "timezone": birth.timezone,
        "latitude": birth.latitude,
        "longitude": birth.longitude,
        "altitude_meters": birth.altitude_meters,
        "fold": birth.fold,
    }


def birth_input_fingerprint(
    birth: BirthInput,
    calculation_profile: CalculationProfile,
) -> str:
    """Hash a complete birth-calculation request without accepting identity fields."""

    return _sha256(_birth_payload(birth, calculation_profile))


def compatibility_pair_fingerprint(request: DualChartCompatibilityRequest) -> str:
    """Return an order- and role-sensitive compatibility cache identity."""

    subject = birth_input_fingerprint(request.subject_birth, request.calculation_profile)
    partner = birth_input_fingerprint(request.partner_birth, request.calculation_profile)
    return _sha256(
        {
            "version": PAIR_FINGERPRINT_VERSION,
            "calculation_profile": request.calculation_profile.value,
            "subject_fingerprint": subject,
            "partner_fingerprint": partner,
            "subject_role": request.subject_role.value,
            "partner_role": request.partner_role.value,
        }
    )


def compatibility_request_fingerprints(
    request: DualChartCompatibilityRequest,
) -> tuple[str, str, str]:
    """Return subject, partner, and ordered-pair cache identities."""

    subject = birth_input_fingerprint(request.subject_birth, request.calculation_profile)
    partner = birth_input_fingerprint(request.partner_birth, request.calculation_profile)
    pair = compatibility_pair_fingerprint(request)
    return subject, partner, pair
