# Feasibility decision

Decision: `investigation_incomplete`

The candidate is not ready for formal capture. It independently obtains the
seven required apparent geocentric planetary longitudes, retains immutable raw
responses and exact requests, avoids Swiss Ephemeris and Source 1 values, and
implements a reproducible provisional ascendant plus deterministic
classification helpers. However, it does not yet independently reproduce the
exact True Chitra ayanamsha or establish a compatible true-node definition.

## Acceptance-gate audit

| Gate | Result |
|---|---|
| No Swiss Ephemeris dependency | Met |
| No use of Source 1 values | Met |
| Exact frozen input | Met for the retained requests and local calculations |
| All numerical fields independently obtainable | Not met |
| True Chitra ayanamsha reproducible | Not met |
| True-node definition reproducible | Not met |
| Ascendant methodology reproducible | Provisionally met; convention review remains |
| Raw external responses retained | Met |
| Sufficient precision for strict tolerances | Met for displayed planetary longitudes; not established for the complete contract |

No `raw.json` has been populated, no diagnostic or strict comparison has been
performed, and no Source 2 approval is claimed. Further work must resolve the
ayanamsha, node, ascendant-convention, and independence-policy questions before
the source-selection decision can be reconsidered.
