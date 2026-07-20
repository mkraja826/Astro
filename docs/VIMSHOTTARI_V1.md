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

## Response guarantees

- Exactly nine Mahadasha periods
- Exactly nine Antardashas inside every Mahadasha
- Mahadasha and Antardasha periods are ordered and contiguous
- Exactly one Mahadasha and one Antardasha are active at birth
- Elapsed plus remaining years equals the active period's full duration
- Antardasha durations sum to their parent Mahadasha duration
- Period source and Lahiri provenance are returned
- Ambiguous civil times require an explicit `fold`
- Production strict-source and licensing safeguards are inherited from the
  planetary engine

## Scope

This version returns Mahadasha and Antardasha timelines. Pratyantardasha and
deeper subdivisions remain outside v1.
