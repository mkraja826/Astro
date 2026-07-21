"""Fetch immutable external inputs for the Source 2 feasibility investigation.

Run only from the isolated ``.source2-venv``. The script uses the JPL Horizons
API, the IERS Rapid Service data file, and the CDS SIMBAD public object page. It
writes response bytes without transformation and records exact requests plus
SHA-256 digests in a separate manifest.
"""

from __future__ import annotations

import hashlib
import json
import ssl
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi
import erfa

UTC_COMPONENTS = (1998, 10, 26, 4, 58, 0.0)
HORIZONS_ENDPOINT = "https://ssd.jpl.nasa.gov/api/horizons.api"
IERS_ENDPOINT = "https://datacenter.iers.org/data/9/finals2000A.all"
SIMBAD_ENDPOINT = "https://simbad.cds.unistra.fr/simbad/sim-basic"
RAW_DIRECTORY = Path(__file__).resolve().parents[1] / "raw-responses"
TLS_CONTEXT = ssl.create_default_context(cafile=certifi.where())

TARGETS = {
    "sun": "10",
    "moon": "301",
    "mercury": "199",
    "venus": "299",
    "mars": "499",
    "jupiter": "599",
    "saturn": "699",
}


def quoted(value: str) -> str:
    """Use Horizons' documented quoted parameter form."""

    return f"'{value}'"


def frozen_tdb_julian_date() -> float:
    """Convert the frozen UTC instant to TDB with ERFA time-scale routines."""

    utc1, utc2 = erfa.dtf2d("UTC", *UTC_COMPONENTS)
    tai1, tai2 = erfa.utctai(utc1, utc2)
    tt1, tt2 = erfa.taitt(tai1, tai2)
    utc_fraction = (UTC_COMPONENTS[3] * 3600 + UTC_COMPONENTS[4] * 60) / 86400
    tdb_minus_tt = erfa.dtdb(tt1, tt2, utc_fraction, 0.0, 0.0, 0.0)
    tdb1, tdb2 = erfa.tttdb(tt1, tt2, tdb_minus_tt)
    return float(tdb1 + tdb2)


def observer_parameters(target_id: str) -> dict[str, str]:
    """Return the exact airless geocentric observer-table request."""

    return {
        "format": "json",
        "COMMAND": quoted(target_id),
        "OBJ_DATA": quoted("YES"),
        "MAKE_EPHEM": quoted("YES"),
        "EPHEM_TYPE": quoted("OBSERVER"),
        "CENTER": quoted("500@399"),
        "TLIST": quoted("1998-10-26 04:58:00"),
        "TLIST_TYPE": quoted("CAL"),
        "TIME_TYPE": quoted("UT"),
        "TIME_ZONE": quoted("+00:00"),
        "TIME_DIGITS": quoted("SECONDS"),
        "CAL_FORMAT": quoted("BOTH"),
        "CAL_TYPE": quoted("GREGORIAN"),
        "QUANTITIES": quoted("31"),
        "REF_SYSTEM": quoted("ICRF"),
        "ANG_FORMAT": quoted("DEG"),
        "APPARENT": quoted("AIRLESS"),
        "CSV_FORMAT": quoted("YES"),
        "EXTRA_PREC": quoted("YES"),
        "ELEV_CUT": quoted("-90"),
        "SKIP_DAYLT": quoted("NO"),
    }


def lunar_element_parameters(tdb_jd: float) -> dict[str, str]:
    """Return the exact Moon-relative-to-Earth osculating-element request."""

    return {
        "format": "json",
        "COMMAND": quoted("301"),
        "OBJ_DATA": quoted("YES"),
        "MAKE_EPHEM": quoted("YES"),
        "EPHEM_TYPE": quoted("ELEMENTS"),
        "CENTER": quoted("500@399"),
        "TLIST": quoted(f"{tdb_jd:.12f}"),
        "TLIST_TYPE": quoted("JD"),
        "TIME_TYPE": quoted("TDB"),
        "CAL_TYPE": quoted("GREGORIAN"),
        "REF_SYSTEM": quoted("ICRF"),
        "REF_PLANE": quoted("ECLIPTIC"),
        "OUT_UNITS": quoted("AU-D"),
        "CSV_FORMAT": quoted("YES"),
        "ELEM_LABELS": quoted("YES"),
    }


def fetch_response(
    *, name: str, endpoint: str, parameters: dict[str, str]
) -> dict[str, Any]:
    """Fetch one URL and save the exact returned bytes."""

    url = f"{endpoint}?{urlencode(parameters)}"
    request = Request(
        url,
        headers={"User-Agent": "Jyothisyam-Source2-Feasibility/1.0"},
    )
    with urlopen(
        request,
        timeout=120,
        context=TLS_CONTEXT,
    ) as response:  # noqa: S310 - fixed HTTPS URLs
        body = response.read()
        final_url = response.geturl()
        status = response.status
        content_type = response.headers.get("Content-Type")

    output_path = RAW_DIRECTORY / name
    output_path.write_bytes(body)
    return {
        "endpoint": endpoint,
        "query_parameters": parameters,
        "request_url": url,
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "response_filename": name,
        "response_byte_size": len(body),
        "response_sha256": hashlib.sha256(body).hexdigest(),
    }


def fetch_document(*, name: str, endpoint: str, parameters: dict[str, str]) -> dict[str, Any]:
    """Fetch a non-Horizons authoritative input using the same retention rule."""

    return fetch_response(name=name, endpoint=endpoint, parameters=parameters)


def main() -> None:
    """Fetch all feasibility inputs and write an exact request manifest."""

    RAW_DIRECTORY.mkdir(parents=True, exist_ok=True)
    accessed_at = datetime.now(UTC).isoformat()
    requests: list[dict[str, Any]] = []

    for body_name, target_id in TARGETS.items():
        requests.append(
            {
                "request_name": f"horizons_observer_{body_name}",
                "target_name": body_name,
                "target_id": target_id,
                **fetch_response(
                    name=f"horizons-observer-{body_name}.json",
                    endpoint=HORIZONS_ENDPOINT,
                    parameters=observer_parameters(target_id),
                ),
            }
        )

    tdb_jd = frozen_tdb_julian_date()
    requests.append(
        {
            "request_name": "horizons_elements_moon",
            "target_name": "moon",
            "target_id": "301",
            "requested_epoch_source": "1998-10-26T04:58:00Z converted with ERFA",
            "requested_epoch_jd_tdb": f"{tdb_jd:.12f}",
            **fetch_response(
                name="horizons-elements-moon.json",
                endpoint=HORIZONS_ENDPOINT,
                parameters=lunar_element_parameters(tdb_jd),
            ),
        }
    )

    requests.append(
        {
            "request_name": "iers_finals2000a",
            **fetch_document(
                name="iers-finals2000A.all",
                endpoint=IERS_ENDPOINT,
                parameters={},
            ),
        }
    )
    requests.append(
        {
            "request_name": "simbad_spica",
            "catalogue_identifier": "HIP 65474",
            **fetch_document(
                name="simbad-spica.html",
                endpoint=SIMBAD_ENDPOINT,
                parameters={"Ident": "Spica"},
            ),
        }
    )

    manifest = {
        "schema_version": "1.0.0",
        "purpose": "source_2_feasibility_external_request_record",
        "accessed_at_utc": accessed_at,
        "frozen_utc_instant": "1998-10-26T04:58:00Z",
        "requests": requests,
    }
    (RAW_DIRECTORY / "request-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
