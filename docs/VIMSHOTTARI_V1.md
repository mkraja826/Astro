# Vimshottari Dasha Contract v1

## Endpoint

`POST /v1/dashas/vimshottari`

## Calculation basis

- Sidereal zodiac
- Lahiri ayanamsha
- Birth Moon evaluated at the normalized UTC instant
- 27 equal Nakshatras of 13°20′ each
- Birth Mahadasha lord selected by the repeating nine-lord Nakshatra sequence
- Birth balance proportional to the untraversed part of the Moon's Nakshatra
- One Dasha year fixed at 365.25 days
- UTC is the canonical period timeline

## Canonical sequence

| Lord | Years |
| --- | ---: |
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |

The complete cycle is 120 years.

## Response depth

The request accepts an optional `depth` field:

- `pratyantardasha` — default; preserves the existing three-level response
- `sookshma` — includes all fourth-level Sookshma Dasha periods

A Sookshma response contains 6,561 fourth-level periods, so clients should request
that depth only when the full detailed timeline is required.

## Birth balance

For the Moon's birth Nakshatra:

```text
progress_fraction = degrees_traversed_in_nakshatra / 13°20′
elapsed_years = lord_duration_years × progress_fraction
remaining_years = lord_duration_years − elapsed_years
```

The first returned Mahadasha includes its theoretical start before birth and its
end after birth. The following eight periods are contiguous and complete the
same 120-year cycle.

## Antardasha subdivision

Every Mahadasha contains exactly nine Antardashas. Their sequence begins with
the Mahadasha lord and then follows the canonical nine-lord cycle.

```text
antardasha_years = mahadasha_years × antardasha_lord_years / 120
```

Each set of nine Antardashas is contiguous, starts at its parent Mahadasha start,
and ends exactly at its parent Mahadasha end. The final boundary is pinned to
the parent end timestamp to prevent accumulated floating-point drift.

## Pratyantardasha subdivision

Every Antardasha contains exactly nine Pratyantardashas. Their sequence begins
with the Antardasha lord and then follows the same canonical nine-lord cycle.

```text
pratyantardasha_years = antardasha_years × pratyantardasha_lord_years / 120
```

Each set of nine Pratyantardashas is contiguous, starts at its parent
Antardasha start, and ends exactly at its parent Antardasha end.

## Sookshma Dasha subdivision

When `depth` is `sookshma`, every Pratyantardasha contains exactly nine
Sookshma Dashas. Their sequence begins with the Pratyantardasha lord.

```text
sookshma_years = pratyantardasha_years × sookshma_lord_years / 120
```

Each set of nine Sookshma Dashas starts at its parent Pratyantardasha start and
ends exactly at its parent end. The final child boundary is pinned to the parent
end timestamp to prevent cumulative floating-point drift.

## Response guarantees

- Exactly nine Mahadasha periods
- Exactly nine Antardashas inside every Mahadasha
- Exactly nine Pratyantardashas inside every Antardasha
- With `depth: sookshma`, exactly nine Sookshma Dashas inside every Pratyantardasha
- 81 Antardashas, 729 Pratyantardashas and optionally 6,561 Sookshma Dashas
- Every returned level is ordered and contiguous
- Exactly one period at each returned level is active at birth
- Elapsed plus remaining years equals the active period's full duration
- Child-period durations sum to their parent-period duration
- Period source and Lahiri provenance are returned
- Ambiguous civil times require an explicit `fold`
- Production strict-source and licensing safeguards are inherited from the
  planetary engine

## Scope

This version returns Mahadasha, Antardasha and Pratyantardasha timelines by
default, with optional Sookshma Dasha expansion. Prana Dasha and deeper
subdivisions remain outside v1.
