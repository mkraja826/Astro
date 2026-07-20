# Swiss Ephemeris data directory

This directory is intentionally committed without binary ephemeris data.

For the v1 planetary-position profile, deployment expects these official Swiss
Ephemeris files:

- `sepl_18.se1`
- `semo_18.se1`

Do not activate a public service until the project has explicitly chosen either
the AGPL license path or the Swiss Ephemeris Professional License. Download data
only from the official Astrodienst Swiss Ephemeris distribution and preserve all
required license and copyright notices.

The API configures this directory by default. A deployment may instead set
`JYOTHISYAM_EPHEMERIS_PATH` to a mounted read-only data directory.
