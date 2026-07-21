# Required-field coverage

`proven` means the candidate can obtain the stated raw astronomical field at
the frozen instant without an internal or Source 1 value. It does not mean the
candidate as a whole has been accepted. `provisionally_proven` means the method
is implemented and reproducible but has an identified convention review.

| Required field | Proposed source | Raw or derived | Independently obtainable | Precision | Status | Concern |
|---|---|---|---|---|---|---|
| Ayanamsha | SIMBAD Spica astrometry + ERFA | Derived | Not yet | Experimental double precision only; convention uncertainty dominates | unresolved | Exact normative True Chitra definition and Spica component/place convention are not established. |
| Ascendant | IERS finals2000A + ERFA + independent horizon/ecliptic geometry | Derived | Provisionally | Double precision; retained EOP and sensitivity values | provisionally_proven | Model CIP offsets `dX/dY` are not applied, and exact profile equivalence needs review. |
| Sun longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | IAU76/80 ecliptic-of-date and JPL ephemeris lineage overlap must be documented. |
| Moon longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Same convention/data-lineage limitation as Sun. |
| Mars longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Target response uses a JPL Mars system kernel; not an independent observational dataset. |
| Mercury longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Same convention/data-lineage limitation as Sun. |
| Jupiter longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Target response uses a JPL Jupiter system kernel; not an independent observational dataset. |
| Venus longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Same convention/data-lineage limitation as Sun. |
| Saturn longitude | Horizons observer quantity 31 | Raw | Yes | 7 decimal places in degrees | proven | Target response uses a JPL Saturn system kernel; not an independent observational dataset. |
| Rahu longitude | Horizons Moon osculating `OM` investigation | Raw candidate requiring convention transformation | Not rigorously | Raw element has high numeric precision; semantic uncertainty dominates | unresolved | J2000 osculating `OM` is not proven equivalent to required apparent/of-date Jyotisha true Rahu. |
| Ketu longitude | Accepted Rahu + 180 degrees | Derived | Not yet | Blocked by Rahu | unresolved | Must not be derived until Rahu is accepted. |
| D1 Lagna sign | Accepted sidereal ascendant + local classifier | Derived | Not yet | Exact classification once longitude is accepted | unresolved | Ayanamsha unresolved; ascendant provisional. |
| D1 Sun sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Moon sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Mars sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Mercury sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Jupiter sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Venus sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Saturn sign | Horizons longitude − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ayanamsha unresolved. |
| D1 Rahu sign | Accepted Rahu − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Rahu and ayanamsha unresolved. |
| D1 Ketu sign | Accepted Ketu − accepted ayanamsha + local classifier | Derived | Not yet | Exact classification once inputs are accepted | unresolved | Ketu and ayanamsha unresolved. |
| D9 Lagna sign | Accepted sidereal ascendant + local classifier | Derived | Not yet | Exact classification once longitude is accepted | unresolved | Ayanamsha unresolved; ascendant provisional. |
| D9 Sun sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Moon sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Mars sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Mercury sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Jupiter sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Venus sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Saturn sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ayanamsha unresolved. |
| D9 Rahu sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Rahu and ayanamsha unresolved. |
| D9 Ketu sign | Accepted sidereal longitude + local classifier | Derived | Not yet | Exact classification once input is accepted | unresolved | Ketu and ayanamsha unresolved. |
| Nakshatra for all ten points | Accepted sidereal longitudes + local classifier | Derived | Not yet | Exact 13°20′ bins after accepted inputs | unresolved | Ayanamsha and node values unresolved; ascendant provisional. |
| Pada for all ten points | Accepted sidereal longitudes + local classifier | Derived | Not yet | Exact 3°20′ bins after accepted inputs | unresolved | Ayanamsha and node values unresolved; ascendant provisional. |

## Coverage summary

- Proven raw fields: seven planetary longitudes.
- Provisionally proven derived field: ascendant.
- Proven deterministic mechanism only: D1, D9, nakshatra, and pada classifier.
- Unresolved contract fields: ayanamsha, Rahu, Ketu, all actual sidereal
  classifications, nakshatras, and padas.

The displayed planetary precision is numerically finer than the existing
strict longitude tolerance, but overall strict-comparison readiness is not
established because the required ayanamsha and node conventions are missing.
