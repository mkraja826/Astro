# Jyothisyam API

Commercial-grade Vedic and South Indian astrology calculation API built with
FastAPI, Skyfield, and JPL DE440s.

## Production astronomy engine

Jyothisyam now uses a single astronomical runtime:

```text
Skyfield + local JPL DE440s
```

Canonical calculation profile:

```text
south_indian_drik_lahiri_jpl_de440s_v1
```

The earlier profile strings remain accepted for client compatibility, but they
resolve to the same JPL engine. The runtime contains no Swiss Ephemeris package,
data files, license switch, comparison route, or fallback path.

## Current capabilities

### System and astronomy

- `GET /`
- `GET /health`
- `GET /health/ephemeris`
- `GET /health/ephemeris/jpl`
- `POST /v1/positions`
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

- JPL DE440s apparent geocentric planetary positions
- Chitrapaksha ayanamsha anchored to apparent Spica
- independently calculated sidereal Lagna
- osculating true Rahu and exactly opposite Ketu
- Rashi, Nakshatra, Pada, and whole-sign houses
- D1 Rasi and D9 Navamsa charts
- geometric sunrise and sunset with no atmospheric refraction
- Vara, Tithi, Nakshatra, Yoga, and Karana at sunrise
- Vimshottari Mahadasha through optional Sookshma
- Varahamihira dignity, aspects, Aṣṭakavarga, relationships, career, and strength
- controlled transparent weighting
- twelve frozen golden-chart inputs and discrepancy reporting

## Local setup

Python 3.12 is recommended.

```powershell
cd C:\Astro
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Install JPL DE440s

```powershell
New-Item -ItemType Directory -Force app\data\jpl
Invoke-WebRequest `
  -Uri "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp" `
  -OutFile "app\data\jpl\de440s.bsp"
```

Default path:

```text
app/data/jpl/de440s.bsp
```

Optional absolute-path override:

```powershell
$env:JYOTHISYAM_JPL_EPHEMERIS_PATH = "C:\ephemeris\de440s.bsp"
```

The kernel is ignored by Git. It must be copied or mounted into every deployment.
Application requests never download it automatically.

## Run and verify

```powershell
python -m pytest
python -m ruff check .
python -m uvicorn app.main:app --reload
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- General health: `http://127.0.0.1:8000/health`
- Ephemeris readiness: `http://127.0.0.1:8000/health/ephemeris`

## Positions request

```json
{
  "birth": {
    "local_datetime": "1998-10-26T10:28:00",
    "timezone": "Asia/Kolkata",
    "latitude": 16.575,
    "longitude": 79.312,
    "altitude_meters": 120
  },
  "calculation_profile": "south_indian_drik_lahiri_jpl_de440s_v1"
}
```

## Panchanga convention

`POST /v1/panchanga` searches the requested local calendar date for the Sun's
geometric center crossing local altitude 0°. It applies no atmospheric
refraction and no upper-limb correction. Sun and Moon sidereal longitudes are
evaluated geocentrically at sunrise. Polar dates without a real crossing return
HTTP 422 instead of a fabricated result.

## Docker

The Dockerfile expects the kernel at:

```text
/app/app/data/jpl/de440s.bsp
```

Build after placing the kernel in `app/data/jpl`, or mount it read-only:

```bash
docker build -t jyothisyam-api .
docker run --rm -p 8080:8080 \
  -v /absolute/path/de440s.bsp:/app/app/data/jpl/de440s.bsp:ro \
  jyothisyam-api
```

## Classical-source boundaries

The Varahamihira profile pins a public-domain 1905 English edition of *Brihat
Jataka*. Classical facts retain source and rule identifiers. Controlled numeric
weights are an API convention, not a textual Varahamihira rule.

The API does not silently import unsupported debilitation-cancellation formulas,
node dignities, guaranteed event predictions, birth-risk judgments, or longevity
claims.

## Calculation contracts

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

## Next validation milestone

1. Freeze JPL results for all twelve golden cases.
2. Import two independent external snapshots per case.
3. Review Lagna, node, sign, Nakshatra, Pada, and Navamsa boundaries.
4. Version any future astronomical-convention change instead of silently altering v1.
5. Add authentication, metering, and commercial API plans.
