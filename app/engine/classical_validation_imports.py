"""Normalize external Jyotisha exports into the golden-chart snapshot contract."""

from __future__ import annotations

import re
from math import isfinite
from typing import Any, Callable

from pydantic import ValidationError

from app.engine.classical_reference import PROFILE_ID
from app.schemas.classical_validation import (
    GoldenChartSnapshot,
    ValidationSourceKind,
)
from app.schemas.classical_validation_imports import (
    ExternalSnapshotImportRequest,
    ExternalSnapshotImportResponse,
)

NORMALIZATION_PROFILE = "jyothisyam_external_snapshot_normalizer_v1"

_POINT_ALIASES = {
    "asc": "ascendant",
    "ascendant": "ascendant",
    "lagna": "ascendant",
    "lagnam": "ascendant",
    "sun": "sun",
    "surya": "sun",
    "ravi": "sun",
    "moon": "moon",
    "chandra": "moon",
    "soma": "moon",
    "mars": "mars",
    "mangala": "mars",
    "kuja": "mars",
    "mercury": "mercury",
    "budha": "mercury",
    "jupiter": "jupiter",
    "guru": "jupiter",
    "brihaspati": "jupiter",
    "venus": "venus",
    "shukra": "venus",
    "sukra": "venus",
    "saturn": "saturn",
    "shani": "saturn",
    "sani": "saturn",
    "rahu": "rahu",
    "north_node": "rahu",
    "ascending_node": "rahu",
    "true_node": "rahu",
    "mean_node": "rahu",
    "ketu": "ketu",
    "south_node": "ketu",
    "descending_node": "ketu",
}

_SIGN_ALIASES = {
    "aries": 1,
    "mesha": 1,
    "taurus": 2,
    "vrishabha": 2,
    "rishabha": 2,
    "gemini": 3,
    "mithuna": 3,
    "cancer": 4,
    "karka": 4,
    "kataka": 4,
    "leo": 5,
    "simha": 5,
    "virgo": 6,
    "kanya": 6,
    "libra": 7,
    "tula": 7,
    "scorpio": 8,
    "vrischika": 8,
    "vrishchika": 8,
    "sagittarius": 9,
    "dhanu": 9,
    "capricorn": 10,
    "makara": 10,
    "aquarius": 11,
    "kumbha": 11,
    "pisces": 12,
    "meena": 12,
    "mina": 12,
}

_GROUP_ALIASES = {
    "ayanamsha": "ayanamsha_degrees",
    "ayanamsa": "ayanamsha_degrees",
    "ayanamsha_degrees": "ayanamsha_degrees",
    "ayanamsa_degrees": "ayanamsha_degrees",
    "ascendant_longitude": "ascendant_longitude",
    "lagna_longitude": "ascendant_longitude",
    "planet_longitudes": "point_longitudes",
    "planetary_longitudes": "point_longitudes",
    "point_longitudes": "point_longitudes",
    "longitudes": "point_longitudes",
    "planets": "point_longitudes",
    "d1": "d1_signs",
    "d1_signs": "d1_signs",
    "rasi": "d1_signs",
    "rasi_signs": "d1_signs",
    "rashi": "d1_signs",
    "rashi_signs": "d1_signs",
    "d9": "d9_signs",
    "d9_signs": "d9_signs",
    "navamsa": "d9_signs",
    "navamsa_signs": "d9_signs",
    "navamsha": "d9_signs",
    "navamsha_signs": "d9_signs",
    "dignities": "dignity",
    "dignity": "dignity",
    "vargottama": "vargottama",
    "compound_relationships": "compound_relationships",
    "relationships": "compound_relationships",
    "bhinnashtakavarga": "bhinnashtakavarga",
    "bav": "bhinnashtakavarga",
    "sarvashtakavarga": "sarvashtakavarga",
    "sav": "sarvashtakavarga",
    "weighted_scores": "weighted_scores",
    "strength_scores": "weighted_scores",
    "weighted_ranks": "weighted_ranks",
    "strength_ranks": "weighted_ranks",
}

_DIGNITY_ALIASES = {
    "exalted": "exaltation_sign",
    "exaltation": "exaltation_sign",
    "exaltation_sign": "exaltation_sign",
    "own": "own_sign",
    "own_sign": "own_sign",
    "debilitated": "debilitation_sign",
    "debilitation": "debilitation_sign",
    "debilitation_sign": "debilitation_sign",
    "ordinary": "ordinary",
    "neutral": "ordinary",
}

_RELATIONSHIP_ALIASES = {
    "great_friend": "great_friend",
    "best_friend": "great_friend",
    "friend": "friend",
    "neutral": "neutral",
    "enemy": "enemy",
    "great_enemy": "great_enemy",
    "bitter_enemy": "great_enemy",
}

_WRAPPER_KEYS = ("snapshot", "reference_snapshot", "chart", "data")
_NODE_CONVENTION_ALIASES = {"true_node", "mean_node"}


class ExternalSnapshotNormalizationError(ValueError):
    """Raised when an external payload cannot be normalized safely."""


def _key(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return normalized.strip("_")


def _float(value: Any, path: str) -> float:
    if isinstance(value, bool):
        raise ExternalSnapshotNormalizationError(f"{path} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ExternalSnapshotNormalizationError(f"{path} must be numeric") from exc
    if not isfinite(result):
        raise ExternalSnapshotNormalizationError(f"{path} must be finite")
    return result


def _longitude(value: Any, path: str) -> float:
    return _float(value, path) % 360.0


def _integer(value: Any, path: str) -> int:
    numeric = _float(value, path)
    if not numeric.is_integer():
        raise ExternalSnapshotNormalizationError(f"{path} must be an integer")
    return int(numeric)


def _boolean(value: Any, path: str) -> bool:
    if isinstance(value, bool):
        return value
    normalized = _key(value)
    if normalized in {"true", "yes", "y", "1"}:
        return True
    if normalized in {"false", "no", "n", "0"}:
        return False
    raise ExternalSnapshotNormalizationError(f"{path} must be boolean")


def _sign(value: Any, path: str) -> int:
    if isinstance(value, str) and _key(value) in _SIGN_ALIASES:
        return _SIGN_ALIASES[_key(value)]
    result = _integer(value, path)
    if not 1 <= result <= 12:
        raise ExternalSnapshotNormalizationError(f"{path} must identify sign 1 through 12")
    return result


def _root(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    for wrapper in _WRAPPER_KEYS:
        wrapped = payload.get(wrapper)
        if isinstance(wrapped, dict):
            return wrapped, f"{wrapper}."
    return payload, ""


def _point_name(
    raw_name: Any,
    path: str,
    aliases: dict[str, str],
    ignored: list[str],
    warnings: list[str],
) -> str | None:
    normalized = _key(raw_name)
    point = _POINT_ALIASES.get(normalized)
    if point is None:
        ignored.append(path)
        warnings.append(f"Ignored unknown point name at {path}: {raw_name!r}")
        return None
    aliases[path] = point
    if normalized in _NODE_CONVENTION_ALIASES:
        warnings.append(
            f"Normalized {raw_name!r} to rahu; verify the source node convention "
            "in calculation_notes before approval."
        )
    return point


def _point_items(value: Any, path: str) -> list[tuple[Any, Any, str]]:
    if isinstance(value, dict):
        return [(name, item, f"{path}.{name}") for name, item in value.items()]
    if isinstance(value, list):
        items: list[tuple[Any, Any, str]] = []
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            if not isinstance(item, dict):
                raise ExternalSnapshotNormalizationError(
                    f"{item_path} must be an object with name and longitude"
                )
            name = item.get("name", item.get("body", item.get("graha", item.get("planet"))))
            longitude = item.get("longitude", item.get("degrees", item.get("value")))
            if name is None or longitude is None:
                raise ExternalSnapshotNormalizationError(
                    f"{item_path} must contain name/body and longitude/degrees"
                )
            items.append((name, longitude, item_path))
        return items
    raise ExternalSnapshotNormalizationError(f"{path} must be an object or list")


def _normalize_point_map(
    value: Any,
    path: str,
    aliases: dict[str, str],
    ignored: list[str],
    warnings: list[str],
    converter: Callable[[Any, str], Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for raw_name, raw_value, item_path in _point_items(value, path):
        point = _point_name(raw_name, item_path, aliases, ignored, warnings)
        if point is None:
            continue
        converted = converter(raw_value, item_path)
        if point in result and result[point] != converted:
            raise ExternalSnapshotNormalizationError(
                f"Conflicting values were supplied for normalized point {point!r}"
            )
        result[point] = converted
    return result


def _normalize_label_map(
    value: Any,
    path: str,
    aliases: dict[str, str],
    ignored: list[str],
    warnings: list[str],
    label_aliases: dict[str, str],
) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ExternalSnapshotNormalizationError(f"{path} must be an object")
    result: dict[str, str] = {}
    for raw_name, raw_value in value.items():
        item_path = f"{path}.{raw_name}"
        point = _point_name(raw_name, item_path, aliases, ignored, warnings)
        if point is None:
            continue
        label = label_aliases.get(_key(raw_value))
        if label is None:
            raise ExternalSnapshotNormalizationError(
                f"Unsupported label at {item_path}: {raw_value!r}"
            )
        result[point] = label
    return result


def _normalize_relationships(
    value: Any,
    path: str,
    aliases: dict[str, str],
    ignored: list[str],
    warnings: list[str],
) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ExternalSnapshotNormalizationError(f"{path} must be an object")
    result: dict[str, str] = {}
    for raw_pair, raw_label in value.items():
        item_path = f"{path}.{raw_pair}"
        parts = re.split(r"\s*(?:->|>|:|/)\s*", str(raw_pair), maxsplit=1)
        if len(parts) != 2:
            ignored.append(item_path)
            warnings.append(f"Ignored malformed relationship key: {raw_pair!r}")
            continue
        source = _point_name(parts[0], f"{item_path}.source", aliases, ignored, warnings)
        target = _point_name(parts[1], f"{item_path}.target", aliases, ignored, warnings)
        if source is None or target is None:
            continue
        label = _RELATIONSHIP_ALIASES.get(_key(raw_label))
        if label is None:
            raise ExternalSnapshotNormalizationError(
                f"Unsupported relationship label at {item_path}: {raw_label!r}"
            )
        result[f"{source}>{target}"] = label
    return result


def _normalize_bav(
    value: Any,
    path: str,
    aliases: dict[str, str],
    ignored: list[str],
    warnings: list[str],
) -> dict[str, list[int]]:
    if not isinstance(value, dict):
        raise ExternalSnapshotNormalizationError(f"{path} must be an object")
    result: dict[str, list[int]] = {}
    for raw_name, raw_row in value.items():
        item_path = f"{path}.{raw_name}"
        point = _point_name(raw_name, item_path, aliases, ignored, warnings)
        if point is None:
            continue
        if not isinstance(raw_row, list) or len(raw_row) != 12:
            raise ExternalSnapshotNormalizationError(
                f"{item_path} must contain exactly 12 bindu values"
            )
        result[point] = [
            _integer(item, f"{item_path}[{index}]")
            for index, item in enumerate(raw_row)
        ]
    return result


def _normalize_sav(value: Any, path: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 12:
        raise ExternalSnapshotNormalizationError(
            f"{path} must contain exactly 12 bindu values"
        )
    return [_integer(item, f"{path}[{index}]") for index, item in enumerate(value)]


def normalize_external_snapshot(
    request: ExternalSnapshotImportRequest,
) -> ExternalSnapshotImportResponse:
    """Normalize one generic JSON export without approving or persisting it."""

    if request.source.source_kind == ValidationSourceKind.INTERNAL_BASELINE:
        raise ExternalSnapshotNormalizationError(
            "The external normalizer does not accept internal_baseline provenance"
        )

    root, prefix = _root(request.payload)
    aliases: dict[str, str] = {}
    ignored: list[str] = []
    warnings: list[str] = []
    normalized: dict[str, Any] = {}
    inline_points: dict[str, float] = {}

    for raw_group, value in root.items():
        raw_path = f"{prefix}{raw_group}"
        group_key = _key(raw_group)
        group = _GROUP_ALIASES.get(group_key)
        if group is None and group_key in _POINT_ALIASES:
            point = _point_name(raw_group, raw_path, aliases, ignored, warnings)
            if point is not None:
                inline_points[point] = _longitude(value, raw_path)
            continue
        if group is None:
            ignored.append(raw_path)
            warnings.append(f"Ignored unsupported top-level field: {raw_path}")
            continue
        aliases[raw_path] = group
        if group in normalized:
            raise ExternalSnapshotNormalizationError(
                f"Multiple fields normalize to snapshot group {group!r}"
            )

        if group == "ayanamsha_degrees":
            normalized[group] = _float(value, raw_path)
        elif group == "ascendant_longitude":
            normalized[group] = _longitude(value, raw_path)
        elif group == "point_longitudes":
            normalized[group] = _normalize_point_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _longitude,
            )
        elif group in {"d1_signs", "d9_signs"}:
            normalized[group] = _normalize_point_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _sign,
            )
        elif group == "dignity":
            normalized[group] = _normalize_label_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _DIGNITY_ALIASES,
            )
        elif group == "vargottama":
            normalized[group] = _normalize_point_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _boolean,
            )
        elif group == "compound_relationships":
            normalized[group] = _normalize_relationships(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
            )
        elif group == "bhinnashtakavarga":
            normalized[group] = _normalize_bav(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
            )
        elif group == "sarvashtakavarga":
            normalized[group] = _normalize_sav(value, raw_path)
        elif group == "weighted_scores":
            normalized[group] = _normalize_point_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _float,
            )
        elif group == "weighted_ranks":
            normalized[group] = _normalize_point_map(
                value,
                raw_path,
                aliases,
                ignored,
                warnings,
                _integer,
            )

    if inline_points:
        existing = normalized.setdefault("point_longitudes", {})
        for point, longitude in inline_points.items():
            if point in existing and existing[point] != longitude:
                raise ExternalSnapshotNormalizationError(
                    f"Conflicting values were supplied for normalized point {point!r}"
                )
            existing[point] = longitude

    normalized = {
        group: value
        for group, value in normalized.items()
        if value not in ({}, [])
    }
    try:
        snapshot = GoldenChartSnapshot.model_validate(normalized)
    except ValidationError as exc:
        raise ExternalSnapshotNormalizationError(
            f"Normalized external snapshot is invalid: {exc}"
        ) from exc

    return ExternalSnapshotImportResponse(
        profile_id=PROFILE_ID,
        normalization_profile=NORMALIZATION_PROFILE,
        format=request.format,
        source=request.source,
        snapshot=snapshot,
        normalized_aliases=dict(sorted(aliases.items())),
        ignored_paths=sorted(set(ignored)),
        warnings=sorted(set(warnings)),
    )
