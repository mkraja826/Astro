# Feasibility methodology

## Frozen input

- Gregorian local civil time: `1998-10-26 10:28:00`
- Timezone: `Asia/Kolkata` / `UTC+05:30`
- UTC instant: `1998-10-26T04:58:00Z`
- Latitude: `16.575` degrees north
- Longitude: `79.312` degrees east
- Altitude: `120` metres
- Required positions: apparent, geocentric, airless
- Required sidereal convention: True Lahiri/Chitrapaksha based on Spica
- Required lunar node: true node

No internal expected output, Source 1 output, or formal comparison was read by
the feasibility scripts.

## Horizons apparent planetary positions

`scripts/fetch_external_data.py` made one request per body for Sun, Moon,
Mercury, Venus, Mars, Jupiter, and Saturn. Every request used:

- endpoint `https://ssd.jpl.nasa.gov/api/horizons.api`;
- target IDs recorded individually in `raw-responses/request-manifest.json`;
- observer ephemeris type;
- center `500@399`, which the retained response identifies as the Earth
  geocenter;
- the single Gregorian UTC epoch `1998-10-26 04:58:00`;
- `TIME_TYPE=UT` and `TIME_ZONE=+00:00`;
- `REF_SYSTEM=ICRF`;
- quantity `31` in decimal degrees with extra output precision; and
- `APPARENT=AIRLESS`, disabling atmospheric refraction.

The [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html) defines
quantity 31 as observer-centered IAU 1976/1980 ecliptic-of-date longitude and
latitude of the apparent target position, including light-time, gravitational
deflection, and stellar aberration, with optional atmospheric refraction. The
[API documentation](https://ssd-api.jpl.nasa.gov/doc/horizons.html) identifies
`AIRLESS` as the non-refracted setting and supports Gregorian-only calendar
selection. The manual also states that `UT` after 1962 means UTC.

The exact endpoint, encoded query parameters, target/center IDs, requested
epoch, response metadata, byte size, and SHA-256 digest are retained in
`raw-responses/request-manifest.json`. `scripts/parse_horizons.py` reads only
the retained response bytes and writes `parsed-horizons.json`. Narrative files
do not manually reproduce the returned planetary numbers.

## Lunar true-node investigation

The Moon elements request uses:

- target `301` relative to Earth center `500@399`;
- an epoch converted from frozen UTC to TDB with ERFA and supplied as JDTDB;
- `EPHEM_TYPE=ELEMENTS`;
- `REF_PLANE=ECLIPTIC` and `REF_SYSTEM=ICRF`;
- `OUT_UNITS=AU-D`; and
- CSV labels enabled.

The retained response identifies the selected plane as the ecliptic of J2000.
The [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html) describes
element tables as instantaneous osculating elements and defines `OM` as the
longitude of ascending node relative to the selected ecliptic/equinox. Element
epochs are TDB. This is a geometric osculating state representation, not an
observer apparent coordinate; the observer-table light-time, aberration, and
deflection corrections do not make `OM` an apparent node.

No authoritative evidence found in this investigation establishes that this
J2000 osculating `OM` is equivalent to the profile's apparent/of-date Jyotisha
true Rahu. `parsed-horizons.json` therefore records
`true_node_status: unresolved`, and Ketu is not derived.

## True Chitra ayanamsha investigation

The unchanged SIMBAD Spica page is retained as `raw-responses/simbad-spica.html`.
`scripts/spica_erfa.py` parses its ICRS J2000 coordinates, proper motion,
parallax, and radial velocity rather than embedding those catalogue values in
the script. The generated `spica-feasibility.json` records all parsed catalogue
inputs and the transformation output.

The experiment uses ERFA `dtf2d`, `utctai`, `taitt`, `atci13`, `obl06`, and
`nut06a`. The `atci13` path applies catalogue proper motion, parallax, radial
velocity, light deflection, aberration, and IAU precession-nutation to obtain a
CIRS direction. The experiment then forms an equinox-based apparent direction
and rotates it to an experimental true ecliptic of date.

The experiment deliberately does not establish an ayanamsha. No authoritative
normative source was found that fixes all of these choices for “True
Lahiri/Chitrapaksha”: apparent versus mean star place, true versus mean
ecliptic/equinox, exact 180-degree anchor definition, and the astrometric
treatment of the Spica multiple system. The generated file therefore records
`ayanamsha_status: unresolved` and `accepted_for_formal_capture: false`.

The [SIMBAD Spica record](https://simbad.cds.unistra.fr/simbad/sim-basic?Ident=Spica)
is the catalogue source. The transformations are based on ERFA `2.0.1`, which
tracks SOFA `20231011`; the [SOFA release page](https://www.iausofa.org/current-software)
documents IAU 2006 precession with IAU 2000A nutation.

## Independent ascendant investigation

`scripts/ascendant_erfa.py` contains its own geometric construction and imports
no production code. It converts UTC to TAI and TT, applies retained IERS
UT1-UTC, computes Greenwich apparent sidereal time with `gst06a`, computes true
obliquity from `obl06` and `nut06a`, and includes polar motion through `sp00`
and `pom00`.

The geometric formula is:

1. Let `p` be the true-ecliptic north pole and `z` the local unrefracted zenith.
2. A horizon/ecliptic intersection `r` must satisfy `r · p = 0` and `r · z = 0`.
3. Thus `r = ±normalize(p × z)`.
4. Choose the solution with `r · east > 0` and rotate it from equatorial to
   true-ecliptic coordinates.

The historical IERS finals2000A file supplies adjacent daily Bulletin B final
UT1-UTC and polar-motion values; the script linearly interpolates them to the
frozen UTC instant. Bulletin A formal-error columns are retained for a DUT1
sensitivity check. The [IERS metadata](https://datacenter.iers.org/versionMetadata.php?filename=latestVersionMeta%2F10_FINALS.DATA_IAU2000_V2013_0110.txt)
documents daily x/y pole and UT1-UTC values since 1992.

Assumptions and limitations:

- latitude and longitude are treated as geodetic coordinates;
- altitude does not change the normal of the unrefracted geodetic horizon
  plane, so it is recorded but does not alter this direction-only calculation;
- atmospheric refraction is not applied;
- IAU 2006/2000A model nutation is used; finals2000A celestial-pole `dX/dY`
  observed offsets are not applied in this feasibility experiment;
- the output includes sensitivity to removal of polar motion and to the
  interpolated formal DUT1 error; and
- equivalence to every convention in the target calculation profile still
  requires human methodological review.

For those reasons, `ascendant-feasibility.json` is
`provisionally_proven`, not accepted formal evidence.

## Deterministic Jyotisha classifications

`scripts/classifications.py` independently implements half-open interval
classification for D1, D9, nakshatra, and pada using `Decimal`. It imports no
production code. `scripts/test_classifications.py` covers:

- zero and 360-degree wrapping, including a negative epsilon;
- 30-degree D1 boundaries;
- 3 degrees 20 minutes D9 boundaries;
- 13 degrees 20 minutes nakshatra boundaries; and
- 3 degrees 20 minutes pada boundaries.

The algorithm is proven as a deterministic local step, but actual sidereal D1,
D9, nakshatra, and pada values remain unresolved until an accepted ayanamsha
and accepted Rahu/Ketu longitudes exist. No classifications are compared with
Source 1 in this phase.
