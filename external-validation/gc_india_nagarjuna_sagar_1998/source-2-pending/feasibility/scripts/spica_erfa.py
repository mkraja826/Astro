"""Experimental ERFA propagation of retained SIMBAD astrometry for Spica.

This experiment intentionally does not accept its provisional angle as a formal
True Chitra ayanamsha. It demonstrates a reproducible transformation path and
records why the exact Jyotisha convention remains unresolved.
"""

from __future__ import annotations

import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path

import erfa

FEASIBILITY_DIRECTORY = Path(__file__).resolve().parents[1]
SIMBAD_PATH = FEASIBILITY_DIRECTORY / "raw-responses" / "simbad-spica.html"
UTC_COMPONENTS = (1998, 10, 26, 4, 58, 0.0)


class TextCollector(HTMLParser):
    """Collect visible text nodes from the retained SIMBAD HTML response."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def retained_simbad_text(path: Path) -> str:
    """Return normalized visible text parsed only from the retained response."""

    parser = TextCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return " ".join(parser.parts)


def required_match(pattern: str, text: str, label: str) -> re.Match[str]:
    """Return a required regex match or fail without substituting a value."""

    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Could not parse {label} from retained SIMBAD response")
    return match


def parse_astrometry(path: Path) -> dict[str, float | str]:
    """Parse the catalogue fields required by ERFA from retained SIMBAD HTML."""

    text = retained_simbad_text(path)
    coordinate = required_match(
        r"ICRS\s+coord\.\s*\(ep=J2000\)\s*:\s*"
        r"(\d+)\s+(\d+)\s+([\d.]+)\s+([+-]\d+)\s+(\d+)\s+([\d.]+)",
        text,
        "ICRS coordinates",
    )
    proper_motion = required_match(
        r"Proper motions mas/yr\s*:\s*([+-]?[\d.]+)\s+([+-]?[\d.]+)",
        text,
        "proper motion",
    )
    parallax = required_match(
        r"Parallaxes \(mas\)\s*:\s*([+-]?[\d.]+)",
        text,
        "parallax",
    )
    radial_velocity = required_match(
        r"V\(km/s\)\s*([+-]?[\d.]+)",
        text,
        "radial velocity",
    )
    return {
        "catalogue_identifier": "HIP 65474",
        "catalogue_name": "Spica / alpha Virginis",
        "catalogue_epoch": "J2000",
        "reference_frame": "ICRS",
        "ra_hours": float(coordinate.group(1)),
        "ra_minutes": float(coordinate.group(2)),
        "ra_seconds": float(coordinate.group(3)),
        "dec_degrees": float(coordinate.group(4)),
        "dec_minutes": float(coordinate.group(5)),
        "dec_seconds": float(coordinate.group(6)),
        "pm_ra_cos_dec_mas_per_year": float(proper_motion.group(1)),
        "pm_dec_mas_per_year": float(proper_motion.group(2)),
        "parallax_mas": float(parallax.group(1)),
        "radial_velocity_km_per_second": float(radial_velocity.group(1)),
    }


def catalog_radians(astrometry: dict[str, float | str]) -> tuple[float, float]:
    """Convert retained sexagesimal ICRS coordinates to radians."""

    ra_hours = (
        float(astrometry["ra_hours"])
        + float(astrometry["ra_minutes"]) / 60
        + float(astrometry["ra_seconds"]) / 3600
    )
    dec_sign = -1 if float(astrometry["dec_degrees"]) < 0 else 1
    dec_degrees = dec_sign * (
        abs(float(astrometry["dec_degrees"]))
        + float(astrometry["dec_minutes"]) / 60
        + float(astrometry["dec_seconds"]) / 3600
    )
    return math.radians(ra_hours * 15), math.radians(dec_degrees)


def main() -> None:
    """Write the provisional Spica transformation and unresolved conclusion."""

    astrometry = parse_astrometry(SIMBAD_PATH)
    catalog_ra, catalog_dec = catalog_radians(astrometry)
    pm_ra = (
        float(astrometry["pm_ra_cos_dec_mas_per_year"])
        * erfa.DAS2R
        / 1000
        / math.cos(catalog_dec)
    )
    pm_dec = (
        float(astrometry["pm_dec_mas_per_year"]) * erfa.DAS2R / 1000
    )
    parallax_arcseconds = float(astrometry["parallax_mas"]) / 1000
    radial_velocity = float(astrometry["radial_velocity_km_per_second"])

    utc1, utc2 = erfa.dtf2d("UTC", *UTC_COMPONENTS)
    tai1, tai2 = erfa.utctai(utc1, utc2)
    tt1, tt2 = erfa.taitt(tai1, tai2)
    cirs_ra, cirs_dec, equation_of_origins = erfa.atci13(
        catalog_ra,
        catalog_dec,
        pm_ra,
        pm_dec,
        parallax_arcseconds,
        radial_velocity,
        tt1,
        tt2,
    )
    apparent_ra = erfa.anp(cirs_ra - equation_of_origins)
    mean_obliquity = erfa.obl06(tt1, tt2)
    _, nutation_obliquity = erfa.nut06a(tt1, tt2)
    true_obliquity = mean_obliquity + nutation_obliquity

    x_equatorial = math.cos(cirs_dec) * math.cos(apparent_ra)
    y_equatorial = math.cos(cirs_dec) * math.sin(apparent_ra)
    z_equatorial = math.sin(cirs_dec)
    x_ecliptic = x_equatorial
    y_ecliptic = (
        math.cos(true_obliquity) * y_equatorial
        + math.sin(true_obliquity) * z_equatorial
    )
    spica_longitude = math.degrees(
        erfa.anp(math.atan2(y_ecliptic, x_ecliptic))
    )
    provisional_ayanamsha = (spica_longitude - 180.0) % 360.0

    result = {
        "schema_version": "1.0.0",
        "purpose": "source_2_true_chitra_feasibility",
        "comparison_performed": False,
        "catalogue_input": astrometry,
        "catalogue_source_file": SIMBAD_PATH.name,
        "utc_instant": "1998-10-26T04:58:00Z",
        "transformation_routines": [
            "dtf2d",
            "utctai",
            "taitt",
            "atci13",
            "obl06",
            "nut06a",
        ],
        "treatments": {
            "proper_motion": "SIMBAD ICRS mu-alpha*cos(delta) and mu-delta",
            "parallax": "SIMBAD catalogue parallax passed to atci13",
            "radial_velocity": "SIMBAD heliocentric radial velocity passed to atci13",
            "aberration": "ERFA atci13 astrometric-to-CIRS transformation",
            "light_deflection": "ERFA atci13 astrometric-to-CIRS transformation",
            "precession": "IAU 2006 through ERFA",
            "nutation": "IAU 2000A through ERFA nut06a",
            "ecliptic": "true obliquity of date, experimental construction",
        },
        "experimental_apparent_spica_longitude_degrees": spica_longitude,
        "experimental_spica_minus_180_degrees": provisional_ayanamsha,
        "ayanamsha_status": "unresolved",
        "unresolved_reasons": [
            (
                "No authoritative specification has yet fixed whether True "
                "Chitra uses this exact apparent-place and true-ecliptic "
                "construction."
            ),
            (
                "SIMBAD combines catalogue measurements; the required "
                "component or photocentre convention for the Spica multiple "
                "system is not formally established for this use."
            ),
            (
                "The sidereal anchor at exactly 180 degrees is plausible from "
                "the middle of Chitra definition but has not yet been tied to "
                "a normative True Lahiri specification."
            ),
        ],
        "accepted_for_formal_capture": False,
    }
    (FEASIBILITY_DIRECTORY / "spica-feasibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
