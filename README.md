# Jyothisyam API

Commercial-grade Vedic and South Indian astrology API.

## Current milestone

The repository currently provides:

- FastAPI application factory
- `GET /`
- `GET /health` process liveness
- `GET /health/ephemeris` calculation readiness
- `POST /v1/positions`
- `POST /v1/charts/d1`
- `POST /v1/charts/d9`
- `POST /v1/panchanga`
- `POST /v1/dashas/vimshottari`
- `POST /v1/dashas/vimshottari/current`
- `GET /v1/classical/varahamihira_v1/profile`
- `GET /v1/classical/varahamihira_v1/rules`
- `GET /v1/classical/varahamihira_v1/rashis`
- `GET /v1/classical/varahamihira_v1/grahas`
- `POST /v1/classical/varahamihira_v1/conditions`
- `POST /v1/classical/varahamihira_v1/aspects`
- `POST /v1/classical/varahamihira_v1/career`
- `POST /v1/classical/varahamihira_v1/ashtakavarga`
- `POST /v1/classical/varahamihira_v1/relationships`
- `POST /v1/classical/varahamihira_v1/strength`
- `POST /v1/classical/varahamihira_v1/dasha/current`
- Lahiri sidereal planetary positions and ascendant
- D1 Rasi and D9 Navamsa divisional charts
- Fixed South Indian 4-by-4 sign-grid metadata
- Rashi, Nakshatra, Pada and whole-sign houses
- Sunrise-based Vara, Tithi, Nakshatra, Yoga and Karana
- Hindu sunrise and sunset in local and UTC time
- Vimshottari birth balance and one complete 120-year Mahadasha cycle
- Nine proportional Antardashas inside every Mahadasha
- Nine proportional Pratyantardashas inside every Antardasha
- Optional Sookshma Dasha expansion with 6,561 fourth-level periods
- Compact active Mahadasha-to-Sookshma chain lookup for any supported instant
- Varahamihira v1 source profile and rule registry
- Deterministic Chapter 1 Rashi and Chapter 2 Graha reference data
- Evidence-bearing dignity, Vargottama, Moon-phase, and Mercury-condition evaluation
- Brihat Jataka 2.13 fractional and special full Graha aspects
- Same-sign conjunction records and twelve whole-sign house-influence summaries
- Chapter 10 Karmājīva channels from Lagna, Moon, and Sun
- Unweighted vocation themes, income-source indications, and supporting facts
- Chapter 9 raw Bhinnashtakavarga contributor rows and planetary bindu arrays
- Twelve-sign Sarvashtakavarga totals with a fixed total of 337
- Chapter 2 natural, temporary, and compound seven-Graha relationships
- Transparent unweighted strength-factor inventories for all seven classical Grahas
- Source-strict cancellation boundaries without importing unregistered rules
- Active Vimshottari timing annotated with ownership, condition, aspect, bindu, career, and relationship facts
- Explicit neutral Rahu and Ketu coverage without invented classical dignity rules
- True Rahu and opposite Ketu
- Timezone, ambiguous-time and coordinate validation
- Explicit Swiss Ephemeris source reporting
- Production guard against silent low-precision fallback
- Automated linting and tests
- Docker and Google Cloud Run-ready configuration

## Local setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- Ephemeris readiness: http://127.0.0.1:8000/health/ephemeris
- Documentation: http://127.0.0.1:8000/docs

## Divisional charts

Use these endpoints for chart-ready South Indian sign grids:

```http
POST /v1/charts/d1
POST /v1/charts/d9
```

D1 uses the source Lahiri sidereal positions directly. D9 applies the standard
Parashari ninefold Navamsa mapping and returns the divisional degree, sign,
house from Navamsa Lagna, and fixed chart-grid coordinates.

## Varahamihira profile

The classical source layer is available through:

```http
GET /v1/classical/varahamihira_v1/profile
GET /v1/classical/varahamihira_v1/rules
GET /v1/classical/varahamihira_v1/rashis
GET /v1/classical/varahamihira_v1/grahas
POST /v1/classical/varahamihira_v1/conditions
POST /v1/classical/varahamihira_v1/aspects
POST /v1/classical/varahamihira_v1/career
POST /v1/classical/varahamihira_v1/ashtakavarga
POST /v1/classical/varahamihira_v1/relationships
POST /v1/classical/varahamihira_v1/strength
POST /v1/classical/varahamihira_v1/dasha/current
```

The profile pins a public-domain 1905 English edition of *Brihat Jataka* and
covers Chapter 1 Rashi and Chapter 2 Graha reference data. The condition
endpoint combines those immutable tables with the existing D1/D9 longitudes to
report own sign, exaltation, debilitation, exact deep dignity points,
Vargottama, Moon phase, and a versioned Mercury association result.

The aspects endpoint implements Chapter 2, stanza 13 at verse precision. It
retains quarter, half, three-quarter, and full aspect strengths for all seven
classical Grahas, then applies the special full aspects of Mars, Jupiter, and
Saturn. It also reports same-sign conjunction pairs, house lords, lord
placements, occupants, and all aspect rays received by each whole-sign house.

The career endpoint implements Chapter 10, verses 10.1–10.4. It returns all
three Karmājīva derivations from Lagna, Moon, and Sun; tenth-house occupants and
income-source relations; the Navamsa lord of each tenth lord; classical vocation
themes; unweighted dignity, conjunction, and aspect facts; and the directional
relationship from each tenth lord to its derived indicator.

The Ashtakavarga endpoint implements the raw Chapter 9 contributor tables. It
returns eight contributor rows for each of the seven planetary
Bhinnashtakavargas, twelve bindu and rekha values per Graha, and the sign-wise
Sarvashtakavarga sum. The fixed planetary totals are 48, 49, 39, 54, 56, 52,
and 39, producing a raw Sarvashtakavarga total of 337.

The relationship endpoint implements Chapter 2, verses 2.16–2.18. It returns 42
directed natural and compound relationships plus 21 mutual temporary-pair
summaries. Natural and compound relations remain directional; temporary
friendship is derived from whole-sign natal separation. Rahu and Ketu are not
inserted into the seven-Graha table, and no numeric score is applied.

The strength endpoint assembles dignity, Vargottama, retrograde, sign-lord
relationship, raw bindu, aspect, and conjunction facts for each classical
Graha. Every factor is categorized but unweighted. The endpoint returns no
strongest-planet ranking and refuses to cancel debilitation without a registered
source rule.

The classical Dasha endpoint preserves the existing current Vimshottari timing
response and annotates each active lord with D1 placement, house ownership,
dignity, Vargottama, aspects, conjunctions, raw Chapter 9 bindus, matching
Karmājīva channels, and all directed relationships among the four active level
lords. Vimshottari supplies timing; the API does not claim that *Brihat Jataka*
defines that timing system. Rahu and Ketu receive neutral natal placement and
aggregate sign context without invented dignity or friendship rules.

The evaluators do not modify D1, D9, Panchanga, or Vimshottari results. Career
output is plural and non-exclusive: `primary_indicator` remains null until a
separately validated weighting system exists. Ashtakavarga returns raw
arithmetic only. Relationship labels and strength factors remain categorical.
Classical Dasha output applies no event prediction, threshold, cancellation, or
final strength score.

## Vimshottari response depth

The default Dasha response ends at Pratyantardasha to preserve the existing API
size and behavior. Add this field when the complete fourth-level timeline is
required:

```json
{
  "depth": "sookshma"
}
```

That response contains 6,561 Sookshma Dasha periods, so it should be requested
only by clients that need the expanded timeline.

## Current Vimshottari chain

Use the compact endpoint when an application needs only the periods active at a
specific instant:

```http
POST /v1/dashas/vimshottari/current
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
  "as_of": {
    "local_datetime": "2026-07-20T12:00:00",
    "timezone": "Asia/Kolkata"
  },
  "calculation_profile": "south_indian_drik_lahiri_v1"
}
```

The response contains one Mahadasha, Antardasha, Pratyantardasha and Sookshma
period, including UTC boundaries, elapsed time, remaining time and progress.

## Tests

```bash
python -m pytest
python -m ruff check .
```

## Swiss Ephemeris production requirement

Local development may use the native engine fallback while the API contract is
being built. A public production service must declare its Swiss Ephemeris
license mode, deploy the required data files and enable strict source checking.
The API then fails instead of silently accepting a fallback source.

See [`docs/EPHEMERIS_DEPLOYMENT.md`](docs/EPHEMERIS_DEPLOYMENT.md).

## Calculation contracts

- [`docs/CALCULATION_PROFILE_V1.md`](docs/CALCULATION_PROFILE_V1.md)
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

## Docker

```bash
docker build -t jyothisyam-api .
docker run --rm -p 8080:8080 jyothisyam-api
```

Then open http://127.0.0.1:8080/health.

## Project direction

The engine will be developed in layers:

1. API and deployment foundation
2. Time and location normalization
3. Astronomical positions
4. Sidereal and ayanamsha profiles
5. Rasi, Lagna, Nakshatra and Panchanga
6. Vargas, Vimshottari Dasha and classical/regional rule layers
7. Authentication, metering and commercial API plans
