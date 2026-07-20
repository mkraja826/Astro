# Swiss Ephemeris production deployment

Jyothisyam API uses the Swiss Ephemeris calculation engine through `pysweph`.
Before activating a public service, the project owner must choose and comply with
one of the licensing paths offered by Astrodienst:

1. GNU Affero General Public License (AGPL), including its source-disclosure
   obligations for network services; or
2. Swiss Ephemeris Professional License.

Official licensing and download pages:

- https://www.astro.com/swisseph/swisseph.htm
- https://www.astro.com/swisseph/swedownload_e.htm

This repository does not declare a license choice on the owner's behalf and does
not redistribute the binary ephemeris data files.

## Required v1 data

The current planetary profile expects these files for the standard modern-date
Swiss Ephemeris segment:

- `sepl_18.se1`
- `semo_18.se1`

Place them in `app/data/ephe`, or mount a read-only directory and set
`JYOTHISYAM_EPHEMERIS_PATH` to that location.

## Production environment

```text
APP_ENV=production
JYOTHISYAM_SWISS_LICENSE_MODE=professional
JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS=true
JYOTHISYAM_EPHEMERIS_PATH=/app/app/data/ephe
```

Use `agpl` instead of `professional` only when the whole service is being
operated in compliance with the AGPL obligations.

## Readiness verification

The process liveness endpoint remains:

```text
GET /health
```

The calculation-readiness endpoint is:

```text
GET /health/ephemeris
```

It returns HTTP `200` only when a license mode is declared and the required data
files are detected. Otherwise it returns HTTP `503` with explicit issues.

Even after file detection succeeds, every calculation checks the source flags
returned by the native engine. When strict mode is enabled, the request fails
with HTTP `503` if the engine silently falls back to Moshier or another source.
This second check prevents a placeholder or corrupt file from being treated as a
production-ready ephemeris installation.
