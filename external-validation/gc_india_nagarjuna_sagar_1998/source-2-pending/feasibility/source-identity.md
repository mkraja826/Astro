# Source identity and independence assessment

Access date for all sources: `2026-07-21`.

| Component | Identity and version | Official source | License or terms | Purpose in this investigation |
|---|---|---|---|---|
| JPL Horizons system | Version `4.98d` (2025-11-21) | [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html) | The API/manual do not state a Horizons dataset license. JPL/Caltech [site policies and notices](https://www.jpl.nasa.gov/caltechjpl-privacy-policies-and-important-notices/) apply; no broader public-domain claim is made here. | External apparent geocentric planetary positions and an exploratory lunar osculating-element request. |
| Horizons API documentation | Documentation version `1.3` (2025-06); retained JSON responses self-identify API version `1.2` | [Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons.html) | Same conservative JPL terms statement as above. | Reproducible HTTP request interface and parameter definitions. |
| IAU SOFA | Issue `2023-10-11`, nineteenth release | [Current SOFA software](https://www.iausofa.org/current-software) | [IAU SOFA Software License](https://www.iausofa.org/terms-and-conditions) | Authoritative IAU 2006 precession and IAU 2000A nutation routines represented through ERFA. |
| ERFA | `2.0.1`, based on SOFA `20231011` | [ERFA project](https://github.com/liberfa/erfa) and [release](https://github.com/liberfa/erfa/releases/tag/v2.0.1) | BSD 3-Clause | Independent C implementation/binding target for time scales, Earth rotation, precession, nutation, and astrometric transformations. |
| PyERFA | `2.0.1.5` with bundled ERFA `2.0.1` / SOFA `20231011` | [PyERFA on PyPI](https://pypi.org/project/pyerfa/) | BSD 3-Clause | Python binding only; no astronomy or astrology values are copied from Jyothisyam. |
| IERS finals2000A | Standard rapid EOP series; retained file retrieved 2026-07-21 | [IERS product metadata](https://datacenter.iers.org/versionMetadata.php?filename=latestVersionMeta%2F10_FINALS.DATA_IAU2000_V2013_0110.txt) | No separate license conclusion is asserted here. | Historical UT1-UTC and polar-motion values for the ascendant experiment. |
| CDS SIMBAD | Spica / alpha Virginis / HIP 65474 object record retrieved 2026-07-21 | [SIMBAD Spica record](https://simbad.cds.unistra.fr/simbad/sim-basic?Ident=Spica) | No separate redistribution conclusion is asserted here; the unchanged response is retained solely as validation provenance. | Catalogue astrometry for the experimental True Chitra path. |

## Independence dimensions

| Dimension | Assessment | Reason |
|---|---|---|
| Independent implementation | Yes, with qualification | Horizons is queried directly and local transformations use ERFA. Skyfield and the Jyothisyam engine are not imported. |
| Independent astronomical dataset | No | This is not an independently observed planetary ephemeris. Horizons and Jyothisyam both rely on the JPL Development Ephemeris ecosystem. The retained responses identify DE441 for the Earth center and several bodies, plus JPL system kernels for Mars, Jupiter, and Saturn. Jyothisyam uses Skyfield with DE440s. The versions/files are not identical, but the dataset lineage overlaps. |
| Independent astrology application | No | Horizons and SOFA/ERFA are astronomical infrastructure. The Jyotisha conventions and classifications would be assembled by the local feasibility scripts, not supplied by an independent astrology product. |
| Independent from Skyfield software | Yes | No Skyfield package, API, or Jyothisyam calculation path is used by this workspace. |
| Independent from Swiss Ephemeris | Yes | No Swiss Ephemeris, PySwissEph, or Swiss-derived astrology package is installed or invoked. |
| Same underlying JPL planetary dataset | Partly/overlapping | The candidate uses Horizons' JPL ephemerides, including DE441 and system kernels. Production uses a different JPL file/version through Skyfield, so this is an implementation cross-check but not a wholly independent astronomical dataset. |

This candidate can test implementation differences, request conventions, time
handling, and local transformations. It cannot be described as an independent
observational ephemeris or as a second independent astrology application.
