# Current Vimshottari Chain Contract v1

## Endpoint

`POST /v1/dashas/vimshottari/current`

## Purpose

This endpoint returns only the Vimshottari periods active at one requested
instant. It is intended for dashboards, mobile applications and daily readings
that do not need the complete 120-year nested timeline.

The response contains exactly one active period at each level:

1. Mahadasha
2. Antardasha
3. Pratyantardasha
4. Sookshma Dasha

## Request time handling

The birth time and requested `as_of` time are both supplied as naive local civil
timestamps with separate IANA timezone identifiers. Ambiguous clock-change times
require an explicit `fold` value of `0` or `1`. Nonexistent local times are
rejected.

The requested instant must be at or after birth and before the end of the first
120-year Vimshottari cycle. Requests outside that interval return HTTP `422`.

## Calculation basis

- Sidereal zodiac
- Lahiri ayanamsha
- Birth Moon evaluated at the normalized UTC birth instant
- One Dasha year fixed at 365.25 days
- UTC is the canonical period timeline
- Every child duration is proportional to its traditional lord duration
- Final child boundaries are pinned to the exact parent end timestamp

## Response guarantees

Each active period returns:

- canonical lord
- sequence number inside its parent
- traditional proportional duration in years
- UTC start and end timestamps
- elapsed years at the requested instant
- remaining years at the requested instant
- progress percentage

The four returned periods are strictly nested and all contain the normalized
requested UTC instant.

## Performance behavior

The engine selects one period at each level directly. It does not construct the
729-period Pratyantardasha tree or the 6,561-period Sookshma tree before choosing
the active chain.

## Production safeguards

The endpoint inherits the Swiss Ephemeris licensing, data-readiness and strict
source checks used by the planetary and full Vimshottari engines.
