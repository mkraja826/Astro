# Jyothisyam API

Commercial-grade Vedic and South Indian astrology API.

## Current milestone

The repository currently provides:

- FastAPI application factory
- `GET /`
- `GET /health` process liveness
- `GET /health/ephemeris` calculation readiness
- `POST /v1/positions`
- Lahiri sidereal planetary positions and ascendant
- Rashi, Nakshatra, Pada and whole-sign houses
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
6. Vargas, Vimshottari Dasha and regional South Indian rules
7. Authentication, metering and commercial API plans
