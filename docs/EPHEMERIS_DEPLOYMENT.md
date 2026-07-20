# Skyfield/JPL production deployment

Jyothisyam API uses Skyfield with a local JPL DE440s SPK kernel. The production
runtime contains no Swiss Ephemeris package, data files, license switch, or
fallback path.

## Required data

Download the official kernel before starting the service:

```powershell
New-Item -ItemType Directory -Force app\data\jpl
Invoke-WebRequest `
  -Uri "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp" `
  -OutFile "app\data\jpl\de440s.bsp"
```

The default path is:

```text
app/data/jpl/de440s.bsp
```

The service never downloads the kernel during a request. The file is ignored by
Git and must be copied into an image or mounted into each deployment.

## Production environment

```text
APP_ENV=production
JYOTHISYAM_JPL_EPHEMERIS_PATH=/app/app/data/jpl/de440s.bsp
```

No Swiss license-related environment variables are recognized or required.

## Docker

The Dockerfile expects the kernel at:

```text
/app/app/data/jpl/de440s.bsp
```

Either download the file into `app/data/jpl` before building the image or mount
it read-only at runtime. Example:

```bash
docker run --rm -p 8080:8080 \
  -v /absolute/path/de440s.bsp:/app/app/data/jpl/de440s.bsp:ro \
  jyothisyam-api
```

## Readiness verification

Process liveness:

```text
GET /health
```

Calculation readiness:

```text
GET /health/ephemeris
```

Compatibility alias:

```text
GET /health/ephemeris/jpl
```

The readiness route returns HTTP `200` only when the configured path points to a
non-empty `.bsp` file. Otherwise it returns HTTP `503` with explicit issues.
Opening and segment validation occurs when Skyfield performs the first
calculation, so deployment smoke tests should call both the health endpoint and
`POST /v1/positions`.

## CI policy

GitHub Actions may download and cache the official kernel before integration
tests. This is a build-time test fixture only; application requests never
initiate network access.
