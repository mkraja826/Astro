# Skyfield/JPL provider v1

## Purpose

This provider is the first licence-independent astronomical backend for Jyothisyam.
It runs alongside the existing Swiss-backed profile and does not change the default.

Profile identifier:

```text
south_indian_drik_lahiri_skyfield_de440s_v1
```

## Runtime components

- Skyfield 1.51 or later
- NumPy
- Local JPL DE440s SPK kernel
- Skyfield bundled time tables (`builtin=True`)

No network request is performed while calculating a chart. The server fails with
HTTP 503 when the configured `.bsp` file is unavailable.

Default kernel path:

```text
app/data/jpl/de440s.bsp
```

Optional override:

```text
JYOTHISYAM_JPL_EPHEMERIS_PATH
```

Official kernel location:

```text
https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
```

## Calculation model

### Planetary positions

The provider observes the Sun, Moon, and planetary targets from the geocentre and
uses Skyfield apparent positions in the true ecliptic and equinox of date.

DE440s provides planetary barycentres for several planets. The provider therefore
uses JPL target identifiers 1, 2, 4, 5, and 6 for Mercury through Saturn where
appropriate. This convention is explicit in comparison output.

### Chitrapaksha ayanamsha

The provider stores the SIMBAD ICRS J2000 position and proper motion of Spica
(alpha Virginis, Chitra). At each requested instant it computes Spica's apparent
true-ecliptic longitude and defines:

```text
ayanamsha = tropical_longitude(Spica) - 180 degrees
sidereal_longitude = tropical_longitude - ayanamsha
```

This is versioned as:

```text
lahiri_chitrapaksha_spica_apparent_v1
```

It is not claimed to reproduce every historical tabulation or every Swiss
Ephemeris Lahiri variant until golden-chart comparison is complete.

### Ascendant

Lagna is the eastern intersection of the true ecliptic of date and the local
horizon. The implementation uses:

- Skyfield local apparent sidereal time
- true equator and equinox of date
- true ecliptic and equinox of date
- observer latitude and longitude

Whole-sign houses continue to be derived from the resulting sidereal Lagna.

### Rahu and Ketu

Rahu is the instantaneous osculating ascending node derived from the Moon's JPL
geocentric position and velocity in the true ecliptic frame. Ketu is exactly 180
degrees opposite. Node speed is calculated by a symmetric finite difference.

This convention is returned as:

```text
true_osculating
```

## Public endpoints

Readiness:

```http
GET /health/ephemeris/jpl
```

Calculate with Skyfield/JPL:

```http
POST /v1/positions
```

using:

```json
{
  "birth": {
    "local_datetime": "1998-10-26T10:28:00",
    "timezone": "Asia/Kolkata",
    "latitude": 16.575,
    "longitude": 79.312,
    "altitude_meters": 120
  },
  "calculation_profile": "south_indian_drik_lahiri_skyfield_de440s_v1"
}
```

Compare providers:

```http
POST /v1/positions/providers/compare
```

The comparison reports ayanamsha, Lagna, longitude, sign, and retrograde
differences for every supported point. It never changes the production default.

## Current scope boundary

Supported through the shared positions engine:

- positions
- D1 and D9
- Vimshottari timing
- classical evaluators that depend on D1/D9 positions

Not yet migrated:

- Panchanga sunrise and sunset
- direct Skyfield solar-event calculations
- production default selection
- approved external parity snapshots

`POST /v1/panchanga` rejects the Skyfield profile rather than silently using Swiss.

## Migration gate

The Swiss profile remains the default until:

1. DE440s is installed locally and in CI validation infrastructure.
2. All twelve frozen golden charts are compared.
3. Longitude, sign, Lagna, node, and boundary differences are reviewed.
4. Panchanga solar events are migrated.
5. The Skyfield profile is version-frozen after external validation.

## Source references

- Skyfield planetary ephemeris API:
  `https://rhodesmill.org/skyfield/api-ephemeris.html`
- Skyfield coordinate frames:
  `https://rhodesmill.org/skyfield/coordinates.html`
- JPL DE440 and DE441 description:
  `https://ssd.jpl.nasa.gov/doc/de440_de441.html`
- JPL generic planetary kernels:
  `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/`
- SIMBAD Spica record:
  `https://simbad.cds.unistra.fr/simbad/sim-basic?Ident=Spica`
