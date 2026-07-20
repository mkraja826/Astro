# Jyothisyam API

Commercial-grade Vedic and South Indian astrology API.

## Current milestone

The repository currently provides the first API foundation:

- FastAPI application factory
- `GET /`
- `GET /health`
- OpenAPI documentation at `/docs`
- Automated health endpoint tests
- Docker and Google Cloud Run-ready configuration

Astrology calculations will be added only after the API foundation and calculation standards are stable.

## Local setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- Documentation: http://127.0.0.1:8000/docs

## Tests

```bash
pytest
```

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
