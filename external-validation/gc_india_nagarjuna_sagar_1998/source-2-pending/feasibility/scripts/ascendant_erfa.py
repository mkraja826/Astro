"""Independent ERFA ascendant feasibility calculation.

The geometric construction intersects the eastern astronomical horizon with
the true ecliptic of date. Earth rotation and obliquity use ERFA's IAU
2006/2000A routines. Historical DUT1 and polar motion are parsed from the
retained IERS finals2000A file. No production Astro code is imported.

The construction is explicit vector geometry: a direction ``r`` on both the
ecliptic and horizon satisfies ``r dot p = 0`` and ``r dot z = 0``, where
``p`` is the true-ecliptic north pole and ``z`` is the local zenith. Therefore
``r = +/- normalize(p cross z)``; the sign with ``r dot east > 0`` is the
ascendant. The ERFA routines implement the IAU standards documented at
https://www.iausofa.org/current-software, and the retained Earth-orientation
fields follow the IERS finals2000A description at
https://datacenter.iers.org/versionMetadata.php?filename=latestVersionMeta%2F10_FINALS.DATA_IAU2000_V2013_0110.txt.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import erfa
import numpy as np

FEASIBILITY_DIRECTORY = Path(__file__).resolve().parents[1]
EOP_PATH = FEASIBILITY_DIRECTORY / "raw-responses" / "iers-finals2000A.all"
UTC_COMPONENTS = (1998, 10, 26, 4, 58, 0.0)
LONGITUDE_EAST_DEGREES = 79.312
LATITUDE_NORTH_DEGREES = 16.575


@dataclass(frozen=True)
class EopRecord:
    """One daily IERS finals2000A record."""

    mjd: float
    xp_arcseconds: float
    yp_arcseconds: float
    dut1_seconds: float
    xp_error_arcseconds: float
    yp_error_arcseconds: float
    dut1_error_seconds: float


def parse_record(line: str) -> EopRecord:
    """Parse Bulletin B values plus Bulletin A formal errors from fixed columns."""

    return EopRecord(
        mjd=float(line[7:15]),
        xp_arcseconds=float(line[134:144]),
        yp_arcseconds=float(line[144:154]),
        dut1_seconds=float(line[154:165]),
        xp_error_arcseconds=float(line[27:36]),
        yp_error_arcseconds=float(line[46:55]),
        dut1_error_seconds=float(line[68:78]),
    )


def interpolated_eop(path: Path, target_mjd: float) -> EopRecord:
    """Linearly interpolate adjacent daily final EOP records."""

    records = []
    for line in path.read_text(encoding="ascii").splitlines():
        try:
            record = parse_record(line)
        except (ValueError, IndexError):
            continue
        if math.floor(target_mjd) <= record.mjd <= math.floor(target_mjd) + 1:
            records.append(record)
    if len(records) != 2:
        raise RuntimeError(f"Expected two adjacent EOP records, found {len(records)}")
    lower, upper = sorted(records, key=lambda record: record.mjd)
    fraction = (target_mjd - lower.mjd) / (upper.mjd - lower.mjd)

    def linear(first: float, second: float) -> float:
        return first + fraction * (second - first)

    return EopRecord(
        mjd=target_mjd,
        xp_arcseconds=linear(lower.xp_arcseconds, upper.xp_arcseconds),
        yp_arcseconds=linear(lower.yp_arcseconds, upper.yp_arcseconds),
        dut1_seconds=linear(lower.dut1_seconds, upper.dut1_seconds),
        xp_error_arcseconds=linear(
            lower.xp_error_arcseconds, upper.xp_error_arcseconds
        ),
        yp_error_arcseconds=linear(
            lower.yp_error_arcseconds, upper.yp_error_arcseconds
        ),
        dut1_error_seconds=linear(lower.dut1_error_seconds, upper.dut1_error_seconds),
    )


def east_horizon_ecliptic_longitude(
    *,
    gast: float,
    true_obliquity: float,
    longitude: float,
    latitude: float,
    xp: float,
    yp: float,
    tt1: float,
    tt2: float,
) -> float:
    """Return the eastern horizon/ecliptic intersection in radians.

    The ITRS geodetic surface normal is rotated back through the IERS polar
    motion matrix to obtain an effective TIRS longitude and latitude. The
    equatorial horizon normal and true-ecliptic pole define the intersection.
    The antipode having positive projection on the local east vector is chosen.
    """

    surface_normal_itrs = np.array(
        [
            math.cos(latitude) * math.cos(longitude),
            math.cos(latitude) * math.sin(longitude),
            math.sin(latitude),
        ]
    )
    tio_locator = erfa.sp00(tt1, tt2)
    polar_motion = erfa.pom00(xp, yp, tio_locator)
    surface_normal_tirs = polar_motion.T @ surface_normal_itrs
    effective_longitude = math.atan2(
        surface_normal_tirs[1], surface_normal_tirs[0]
    )
    effective_latitude = math.atan2(
        surface_normal_tirs[2],
        math.hypot(surface_normal_tirs[0], surface_normal_tirs[1]),
    )

    local_apparent_sidereal_angle = erfa.anp(gast + effective_longitude)
    zenith = np.array(
        [
            math.cos(effective_latitude)
            * math.cos(local_apparent_sidereal_angle),
            math.cos(effective_latitude)
            * math.sin(local_apparent_sidereal_angle),
            math.sin(effective_latitude),
        ]
    )
    ecliptic_north = np.array(
        [0.0, -math.sin(true_obliquity), math.cos(true_obliquity)]
    )
    intersection = np.cross(ecliptic_north, zenith)
    intersection /= np.linalg.norm(intersection)
    east = np.array(
        [
            -math.sin(local_apparent_sidereal_angle),
            math.cos(local_apparent_sidereal_angle),
            0.0,
        ]
    )
    if float(np.dot(intersection, east)) < 0:
        intersection *= -1

    x_equatorial, y_equatorial, z_equatorial = intersection
    x_ecliptic = x_equatorial
    y_ecliptic = (
        math.cos(true_obliquity) * y_equatorial
        + math.sin(true_obliquity) * z_equatorial
    )
    return erfa.anp(math.atan2(y_ecliptic, x_ecliptic))


def calculate(*, dut1: float, xp: float, yp: float) -> float:
    """Calculate the tropical ascendant in degrees for supplied EOP values."""

    utc1, utc2 = erfa.dtf2d("UTC", *UTC_COMPONENTS)
    tai1, tai2 = erfa.utctai(utc1, utc2)
    tt1, tt2 = erfa.taitt(tai1, tai2)
    ut11, ut12 = erfa.utcut1(utc1, utc2, dut1)
    gast = erfa.gst06a(ut11, ut12, tt1, tt2)
    mean_obliquity = erfa.obl06(tt1, tt2)
    _, nutation_obliquity = erfa.nut06a(tt1, tt2)
    true_obliquity = mean_obliquity + nutation_obliquity
    longitude = math.radians(LONGITUDE_EAST_DEGREES)
    latitude = math.radians(LATITUDE_NORTH_DEGREES)
    ascendant = east_horizon_ecliptic_longitude(
        gast=gast,
        true_obliquity=true_obliquity,
        longitude=longitude,
        latitude=latitude,
        xp=xp,
        yp=yp,
        tt1=tt1,
        tt2=tt2,
    )
    return math.degrees(ascendant)


def circular_difference_degrees(first: float, second: float) -> float:
    """Return the signed shortest angular difference."""

    return (first - second + 180.0) % 360.0 - 180.0


def main() -> None:
    """Write a generated, non-comparison ascendant feasibility result."""

    utc1, utc2 = erfa.dtf2d("UTC", *UTC_COMPONENTS)
    target_mjd = float(utc1 + utc2 - 2400000.5)
    eop = interpolated_eop(EOP_PATH, target_mjd)
    arcseconds_to_radians = erfa.DAS2R
    xp = eop.xp_arcseconds * arcseconds_to_radians
    yp = eop.yp_arcseconds * arcseconds_to_radians
    ascendant = calculate(dut1=eop.dut1_seconds, xp=xp, yp=yp)
    without_polar_motion = calculate(dut1=eop.dut1_seconds, xp=0.0, yp=0.0)
    dut1_high = calculate(
        dut1=eop.dut1_seconds + eop.dut1_error_seconds,
        xp=xp,
        yp=yp,
    )

    result = {
        "schema_version": "1.0.0",
        "purpose": "source_2_ascendant_feasibility",
        "comparison_performed": False,
        "utc_instant": "1998-10-26T04:58:00Z",
        "geographic_input": {
            "longitude_degrees_east": LONGITUDE_EAST_DEGREES,
            "latitude_degrees_north": LATITUDE_NORTH_DEGREES,
            "altitude_meters": 120,
            "altitude_effect": (
                "No effect on the unrefracted geodetic horizon-plane normal."
            ),
        },
        "earth_orientation": {
            "source_file": EOP_PATH.name,
            "series": "IERS finals2000A",
            "value_columns": "Bulletin B final",
            "error_columns": "Bulletin A formal errors",
            "interpolation": "linear between adjacent daily records",
            "target_mjd_utc": target_mjd,
            "xp_arcseconds": eop.xp_arcseconds,
            "yp_arcseconds": eop.yp_arcseconds,
            "dut1_seconds": eop.dut1_seconds,
            "xp_error_arcseconds": eop.xp_error_arcseconds,
            "yp_error_arcseconds": eop.yp_error_arcseconds,
            "dut1_error_seconds": eop.dut1_error_seconds,
        },
        "erfa_routines": [
            "dtf2d",
            "utctai",
            "taitt",
            "utcut1",
            "gst06a",
            "obl06",
            "nut06a",
            "sp00",
            "pom00",
        ],
        "models": ["IAU 2006 precession", "IAU 2000A nutation"],
        "atmospheric_refraction": False,
        "tropical_ascendant_degrees": ascendant,
        "sensitivity": {
            "polar_motion_effect_arcseconds": abs(
                circular_difference_degrees(ascendant, without_polar_motion)
            )
            * 3600,
            "plus_formal_dut1_error_effect_arcseconds": abs(
                circular_difference_degrees(dut1_high, ascendant)
            )
            * 3600,
        },
        "status": "provisionally_proven",
        "limitation": (
            "The geometric method and EOP handling are reproducible, but exact "
            "equivalence to the target calculation profile must be reviewed "
            "before formal capture."
        ),
    }
    (FEASIBILITY_DIRECTORY / "ascendant-feasibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
