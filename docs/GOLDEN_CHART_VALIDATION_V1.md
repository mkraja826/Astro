# Golden-Chart Validation Harness v1

## Purpose

The validation system has two deliberately separate layers:

1. **Internal JPL regression baselines** freeze Jyothisyam's own deterministic
   Skyfield/JPL outputs so future code or dependency changes cannot alter results
   silently.
2. **External reference validation** compares those calculations with independently
   produced Jyotisha software exports and manual references.

An internal baseline is not independent evidence. It must never increase the
external approval count or make the project claim third-party validation.

## Public endpoints

```http
GET  /v1/classical/varahamihira_v1/validation/profile
GET  /v1/classical/varahamihira_v1/validation/cases
POST /v1/classical/varahamihira_v1/validation/compare

GET  /v1/classical/varahamihira_v1/validation/baseline/manifest
GET  /v1/classical/varahamihira_v1/validation/baseline/integrity
GET  /v1/classical/varahamihira_v1/validation/baseline/cases/{case_id}
POST /v1/classical/varahamihira_v1/validation/baseline/verify-current
```

## Frozen case set

Case set `jyothisyam_external_golden_cases_v1` contains twelve immutable birth
inputs. The set covers:

- northern and southern hemispheres
- eastern and western longitudes
- equatorial and high-latitude locations
- India and multiple international time zones
- daylight-saving and non-daylight-saving zones
- leap-day, year-boundary, near-midnight, polar-night, and altitude cases

Case-set digest:

```text
5dcd67cd142e49127cdb62165ca8e1ccb7b28f58fabbf3612eeca42c5392f624
```

Any input change must create a new case-set version rather than silently modifying
v1.

## Internal JPL baseline set

Baseline set:

```text
jyothisyam_jpl_de440s_golden_baselines_v1
```

Calculation profile:

```text
south_indian_drik_lahiri_jpl_de440s_v1
```

Full logical-set digest:

```text
e4c97e2c62ce380dfd361f645cc18682849085b823541ae509edd2d1f3568da0
```

The repository stores:

```text
app/data/validation/jpl_de440s_v1/manifest.json
app/data/validation/jpl_de440s_v1/<case_id>.json
```

Each case file contains a normalized snapshot and its own SHA-256 digest. The
manifest locks:

- the case-set identity and digest
- the canonical calculation profile
- Skyfield version 1.54
- JPL model DE440s
- all twelve case IDs and per-case digests
- the digest of the reconstructed logical baseline set

`GET .../baseline/integrity` validates storage without recalculating charts. It
checks safe paths, case membership, duplicates, missing and unexpected cases,
per-file hashes, and the full-set hash.

`POST .../baseline/verify-current` recalculates all twelve cases and compares the
current normalized output exactly with each committed baseline. It reports every
mismatched flattened field path. This operation is intentionally more expensive.

## Snapshot groups

A normalized snapshot contains:

- ayanamsha
- ascendant longitude
- point longitudes
- D1 signs
- D9 signs
- dignity labels
- Vargottama flags
- compound relationship matrix
- seven Bhinnashtakavarga arrays
- Sarvashtakavarga array
- controlled API weighting scores
- controlled API weighting ranks

An external source may submit any subset. Omitted groups are reported as skipped,
and a passing report validates only the supplied fields.

## External comparison rules

Default tolerances are:

```text
ayanamsha: 0.01 degrees
longitudes: 0.01 degrees
controlled score: 0.000001
```

Signs, dignity labels, Vargottama, relationships, bindus, and ranks are exact
comparisons. Every scalar produces a record containing the actual value, reference
value, numeric difference where applicable, tolerance, status, and reason.

## External source provenance

Every comparison identifies:

- software or manual source name
- source version
- source kind
- calculation notes

Recommended notes include zodiac, ayanamsha, node type, ephemeris, house
convention, and software-specific options.

## Completion policy

Two independently reviewed external sources are required for every frozen case.
The current truthful status remains:

```json
{
  "committed_external_snapshot_count": 0,
  "externally_validated_case_count": 0,
  "external_reference_validation_complete": false
}
```

The twelve internal JPL baselines do not change those values.

A disagreement must be investigated against calculation contracts and source
rules. The implementation must not select whichever value appears in the most
programs without understanding the cause.

## Example partial external comparison

```json
{
  "case_id": "gc_india_nagarjuna_sagar_1998",
  "source": {
    "source_name": "Independent Jyotisha Program",
    "source_version": "1.0",
    "source_kind": "external_software",
    "calculation_notes": [
      "Lahiri sidereal",
      "true node"
    ]
  },
  "reference_snapshot": {
    "point_longitudes": {
      "sun": 188.75805,
      "moon": 252.25373
    },
    "d1_signs": {
      "sun": 7,
      "moon": 9
    }
  },
  "calculation_profile": "south_indian_drik_lahiri_jpl_de440s_v1",
  "tolerances": {
    "longitude_degrees": 0.01,
    "ayanamsha_degrees": 0.01,
    "score": 0.000001
  }
}
```

The comparison route calculates the frozen case at request time. It does not
persist or approve the submitted reference snapshot.

## Regenerating internal baselines

Run only after an intentional, reviewed calculation-contract change:

```powershell
python scripts/generate_jpl_golden_baselines.py
python -m pytest tests/test_jpl_golden_baselines.py
```

A changed digest must be reviewed field by field. Do not regenerate baselines merely
to make a failing test pass.

## Weighting boundary

`transparent_strength_weighting_v1` is an API convention, not a quotation from
Brihat Jataka. External Jyotisha programs are not expected to reproduce these
scores unless they implement the same published formulas. Raw astronomical and
classical fields should be validated before score comparison.

## Exclusions

The harness does not validate or produce:

- event predictions
- profession guarantees
- debilitation cancellations from unregistered texts
- birth-risk judgments
- health diagnoses
- longevity judgments
