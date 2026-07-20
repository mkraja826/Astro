# Skyfield/JPL production provider v1

Jyothisyam API now uses Skyfield with a local JPL DE440s kernel as its sole
astronomical runtime.

Canonical profile:

```text
south_indian_drik_lahiri_jpl_de440s_v1
```

The earlier profile strings remain accepted for client compatibility, but all
accepted profiles resolve to the same JPL calculation engine.

## Runtime

- Skyfield 1.51 or later
- NumPy
- local `de440s.bsp`
- bundled Skyfield time tables

The application never downloads ephemeris data during a request. Missing kernel
data returns HTTP 503.

Default path:

```text
app/data/jpl/de440s.bsp
```

Override:

```text
JYOTHISYAM_JPL_EPHEMERIS_PATH
```

## Calculation conventions

Planetary positions are apparent geocentric positions in the true ecliptic of
date. Chitrapaksha ayanamsha anchors apparent Spica at sidereal longitude 180°.
Lagna is the eastern true-ecliptic intersection with the local horizon. Rahu is
the instantaneous osculating lunar ascending node and Ketu is exactly opposite.

Panchanga sunrise and sunset use the geometric center of the Sun crossing local
altitude 0°, with no atmospheric refraction and no upper-limb correction. Sun and
Moon sidereal longitudes are evaluated geocentrically at sunrise. Dates without
a real sunrise or sunset return a clear 422 response.

## Public routes

```http
GET  /health/ephemeris
GET  /health/ephemeris/jpl
POST /v1/positions
POST /v1/panchanga
```

The earlier provider-comparison route is retired because there is only one
production astronomical provider.

## Supported layers

The JPL positions engine supplies positions, D1, D9, Panchanga, Vimshottari,
classical evaluators, weighted context, and golden-chart snapshots.

## Remaining validation

1. Freeze JPL output for all twelve golden cases.
2. Add two independently produced external snapshots per case.
3. Review sign, Nakshatra, Pada, Navamsha, Lagna, and node boundaries.
4. Version any future change to ayanamsha, node, or solar-event conventions.

## References

- Skyfield ephemeris API: `https://rhodesmill.org/skyfield/api-ephemeris.html`
- Skyfield almanac API: `https://rhodesmill.org/skyfield/api-almanac.html`
- Skyfield almanac guide: `https://rhodesmill.org/skyfield/almanac.html`
- JPL planetary kernels: `https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/`
