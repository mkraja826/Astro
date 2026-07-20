# Jyothisyam API

Commercial-grade Vedic and South Indian astrology calculation API built with
FastAPI.

## Current capabilities

### System and astronomy

- `GET /`
- `GET /health`
- `GET /health/ephemeris` — Swiss Ephemeris readiness
- `GET /health/ephemeris/jpl` — local Skyfield/JPL DE440s readiness
- `POST /v1/positions`
- `POST /v1/positions/providers/compare`
- `POST /v1/charts/d1`
- `POST /v1/charts/d9`
- `POST /v1/panchanga`
- `POST /v1/dashas/vimshottari`
- `POST /v1/dashas/vimshottari/current`

### Classical Varahamihira profile

- `GET /v1/classical/varahamihira_v1/profile`
- `GET /v1/classical/varahamihira_v1/rules`
- `GET /v1/classical/varahamihira_v1/rashis`
- `GET /v1/classical/varahamihira_v1/grahas`
- `POST /v1/classical/varahamihira_v1/conditions`
- `POST /v1/classical/varahamihira_v1/aspects`
- `POST /v1/classical/varahamihira_v1/ashtakavarga`
- `POST /v1/classical/varahamihira_v1/relationships`
- `POST /v1/classical/varahamihira_v1/strength`
- `POST /v1/classical/varahamihira_v1/strength/weighted`
- `POST /v1/classical/varahamihira_v1/career`
- `POST /v1/classical/varahamihira_v1/career/weighted`
- `POST /v1/classical/varahamihira_v1/dasha/current`
- `POST /v1/classical/varahamihira_v1/dasha/current/weighted`
- `GET /v1/classical/varahamihira_v1/weighting/profile`
- `GET /v1/classical/varahamihira_v1/validation/profile`
- `GET /v1/classical/varahamihira_v1/validation/cases`
- `POST /v1/classical/varahamihira_v1/validation/compare`

### Calculation features

- Lahiri sidereal planetary positions and Lagna
- True Rahu and opposite Ketu
- Rashi, Nakshatra, Pada, and whole-sign houses
- D1 Rasi and D9 Navamsa charts
- Fixed South Indian 4-by-4 sign-grid metadata
- Sunrise-based Vara, Tithi, Nakshatra, Yoga, and Karana
- Vimshottari Mahadasha, Antardasha, Pratyantardasha, and optional Sookshma
- Compact active Mahadasha-to-Sookshma lookup
- Chapter 1 Rashi and Chapter 2 Graha reference data
- Dignity, Vargottama, Moon-phase, and Mercury-condition evidence
- Fractional and special full Graha aspects
- Same-sign conjunctions and whole-sign house influence
- Chapter 9 Bhinnashtakavarga and Sarvashtakavarga
- Natural, temporary, and compound Graha relationships
- Chapter 10 Karmājīva vocation channels
- Transparent unweighted strength evidence
- Separately versioned controlled strength weighting
- Twelve frozen external-validation chart inputs
- Partial snapshot comparison with field-specific tolerances

## Astronomical providers

### Existing Swiss profile

```text
south_indian_drik_lahiri_v1
```

This remains the default profile. A public closed-source service using Swiss
Ephemeris must satisfy the applicable Swiss Ephemeris licensing requirements and
deploy the required data files. The API prevents silent low-precision fallback
when strict production mode is enabled.

### Skyfield/JPL migration profile

```text
south_indian_drik_lahiri_skyfield_de440s_v1
```

This optional profile uses:

- Skyfield
- NumPy
- a local JPL DE440s SPK kernel
- an apparent Spica-based Chitrapaksha ayanamsha convention
- an osculating lunar ascending node for Rahu
- a locally calculated true-ecliptic Lagna

The service never downloads the JPL kernel during a request. Missing data returns
HTTP 503 with a clear readiness error.

Swiss remains the production default until all frozen golden charts and boundary
cases are reviewed. Panchanga sunrise and sunset have not yet been migrated;
`POST /v1/panchanga` rejects the Skyfield profile rather than silently using the
Swiss implementation.

## Local setup

Python 3.12 is recommended.

```powershell
cd C:\Astro
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
python -m ruff check .
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- General health: `http://127.0.0.1:8000/health`
- Swiss readiness: `http://127.0.0.1:8000/health/ephemeris`
- JPL readiness: `http://127.0.0.1:8000/health/ephemeris/jpl`

## Install the local DE440s kernel

Create the data directory:

```powershell
New-Item -ItemType Directory -Force app\data\jpl
```

Download the official JPL kernel:

```powershell
Invoke-WebRequest `
  -Uri "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp" `
  -OutFile "app\data\jpl\de440s.bsp"
```

The default path is:

```text
app/data/jpl/de440s.bsp
```

An absolute path can be selected with:

```powershell
$env:JYOTHISYAM_JPL_EPHEMERIS_PATH = "C:\ephemeris\de440s.bsp"
```

The `.bsp` kernel is intentionally ignored by Git and must be mounted or copied
into each deployment separately.

## Calculate with Skyfield/JPL

```http
POST /v1/positions
```

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

The same profile can flow through D1, D9, Vimshottari, and classical evaluators
that depend on the shared positions engine.

## Compare Swiss and Skyfield

```http
POST /v1/positions/providers/compare
```

```json
{
  "birth": {
    "local_datetime": "1998-10-26T10:28:00",
    "timezone": "Asia/Kolkata",
    "latitude": 16.575,
    "longitude": 79.312,
    "altitude_meters": 120
  },
  "longitude_tolerance_degrees": 0.05,
  "ascendant_tolerance_degrees": 0.1,
  "ayanamsha_tolerance_degrees": 0.02
}
```

The response reports:

- signed and absolute ayanamsha difference
- signed and absolute Lagna difference
- longitude differences for all supported planets and nodes
- sign agreement
- retrograde agreement
- per-field tolerance results
- `production_default_changed: false`

The comparison endpoint never changes configuration or chooses a winner.

## Divisional charts

```http
POST /v1/charts/d1
POST /v1/charts/d9
```

D1 uses source sidereal positions directly. D9 applies the versioned Parashari
ninefold Navamsa mapping and returns divisional degrees, signs, houses from
Navamsa Lagna, and fixed South Indian grid coordinates.

## Vimshottari response depth

The default Vimshottari response ends at Pratyantardasha. Request the complete
fourth-level timeline with:

```json
{
  "depth": "sookshma"
}
```

A full response contains 6,561 Sookshma periods and should only be requested by
clients that need the expanded timeline.

## Classical-source boundaries

The Varahamihira profile pins a public-domain 1905 English edition of *Brihat
Jataka*. Classical facts retain source and rule identifiers. Controlled numeric
weights are an API convention, not a textual Varahamihira rule.

The API does not silently import unsupported debilitation-cancellation formulas,
node dignities, or guaranteed event predictions. Sensitive birth-risk and
longevity judgments remain outside the implemented scope.

## Calculation contracts

- [`docs/CALCULATION_PROFILE_V1.md`](docs/CALCULATION_PROFILE_V1.md)
- [`docs/SKYFIELD_JPL_PROVIDER_V1.md`](docs/SKYFIELD_JPL_PROVIDER_V1.md)
- [`docs/EPHEMERIS_DEPLOYMENT.md`](docs/EPHEMERIS_DEPLOYMENT.md)
- [`docs/CHARTS_D1_D9_V1.md`](docs/CHARTS_D1_D9_V1.md)
- [`docs/PANCHANGA_V1.md`](docs/PANCHANGA_V1.md)
- [`docs/VIMSHOTTARI_V1.md`](docs/VIMSHOTTARI_V1.md)
- [`docs/VIMSHOTTARI_CURRENT_V1.md`](docs/VIMSHOTTARI_CURRENT_V1.md)
- [`docs/VARAHAMIHIRA_REFERENCE_V1.md`](docs/VARAHAMIHIRA_REFERENCE_V1.md)
- [`docs/CLASSICAL_CONDITIONS_V1.md`](docs/CLASSICAL_CONDITIONS_V1.md)
- [`docs/CLASSICAL_ASPECTS_V1.md`](docs/CLASSICAL_ASPECTS_V1.md)
- [`docs/CLASSICAL_CAREER_V1.md`](docs/CLASSICAL_CAREER_V1.md)
- [`docs/ASHTAKAVARGA_V1.md`](docs/ASHTAKAVARGA_V1.md)
- [`docs/CLASSICAL_DASHA_CONTEXT_V1.md`](docs/CLASSICAL_DASHA_CONTEXT_V1.md)
- [`docs/CLASSICAL_RELATIONSHIPS_V1.md`](docs/CLASSICAL_RELATIONSHIPS_V1.md)
- [`docs/CLASSICAL_STRENGTH_V1.md`](docs/CLASSICAL_STRENGTH_V1.md)
- [`docs/CONTROLLED_STRENGTH_WEIGHTING_V1.md`](docs/CONTROLLED_STRENGTH_WEIGHTING_V1.md)
- [`docs/GOLDEN_CHART_VALIDATION_V1.md`](docs/GOLDEN_CHART_VALIDATION_V1.md)
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

## Docker

```bash
docker build -t jyothisyam-api .
docker run --rm -p 8080:8080 jyothisyam-api
```

For the Skyfield profile, mount the kernel and set its absolute path in the
container. Do not bake an unreviewed third-party kernel into a public image.

## Project direction

1. Validate Skyfield/JPL positions against all frozen golden charts.
2. Review ayanamsha, Lagna, node, sign-boundary, and retrograde differences.
3. Migrate Hindu sunrise and sunset calculations.
4. Freeze a validated Skyfield calculation profile.
5. Switch production only after the migration gate passes.
6. Add authentication, metering, and commercial API plans.
