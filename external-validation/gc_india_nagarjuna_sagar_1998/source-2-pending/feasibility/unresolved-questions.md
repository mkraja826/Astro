# Unresolved questions

## True Chitra / Lahiri ayanamsha

1. Which authoritative specification defines “True Lahiri/Chitrapaksha” with
   enough detail to reproduce it numerically?
2. Is Spica to be propagated as an astrometric, apparent, or another defined
   place, and is the reference an apparent, true, or mean ecliptic/equinox?
3. Is the sidereal anchor exactly the middle of Chitra at 180 degrees, and at
   what reference epoch/frame is that statement normative?
4. Which astrometric component or photocentre convention is required for the
   Spica multiple system?
5. Are the retained SIMBAD catalogue fields and their mixed references
   sufficient, or is a single authoritative astrometric solution required?

Until these questions are answered from an authoritative source, the Spica
experiment cannot be promoted to a formal ayanamsha value.

## Lunar true node

1. What exact mathematical definition does the calculation profile use for
   “true lunar node” (instantaneous osculating orbit, apparent/of-date node, or
   another prescribed lunar theory)?
2. Which ecliptic and equinox are required?
3. What transformations would make a Horizons J2000 osculating `OM` equivalent
   to that definition, if equivalence exists?
4. Do light-time, aberration, nutation, or other apparent-place corrections
   apply to the node definition?
5. What authoritative reference and independent implementation can validate
   the transformation?

Ketu remains blocked until Rahu is accepted; no 180-degree derivation should be
performed before then.

## Ascendant

1. Should finals2000A celestial-pole offsets `dX/dY` be applied in addition to
   the IAU 2006/2000A model for the formal profile?
2. Does the target profile define the ecliptic as true ecliptic/equinox of date
   in precisely the same way as the ERFA construction?
3. Is geodetic latitude the intended interpretation of the frozen latitude?
4. Is the documented no-refraction geometric horizon sufficient for formal
   profile equivalence?

The retained historical DUT1 and polar-motion data are available, and the
feasibility result exposes sensitivity rather than hiding these inputs.

## Independence and acceptance policy

1. Is an independent implementation using overlapping JPL Development
   Ephemeris lineage acceptable as Source 2, or must the astronomical dataset
   also be independent?
2. Is a locally assembled astronomy-to-Jyotisha pipeline acceptable, given that
   it is not an independent astrology application?
3. What licensing/retention policy should govern JPL Horizons responses, since
   no Horizons-specific data license was identified in the official API/manual?

These policy questions must be answered before formal-source selection even if
the technical ayanamsha and node blockers are resolved.
