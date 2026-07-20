# External Golden-Chart Validation Harness v1

## Purpose

This harness compares Jyothisyam calculations with independently produced
Jyotisha snapshots. It records field-level agreements and disagreements without
assuming that the majority result is correct.

The harness does not alter the astronomical, chart, classical, or weighting
engines. It is a validation layer over their existing outputs.

## Public endpoints

```http
GET  /v1/classical/varahamihira_v1/validation/profile
GET  /v1/classical/varahamihira_v1/validation/cases
POST /v1/classical/varahamihira_v1/validation/compare
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

The API returns a SHA-256 digest of the normalized case set. Any input change
must create a new case-set version rather than silently modifying v1.

## Snapshot groups

A reference source may submit any subset of:

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

Omitted groups are reported as skipped. A passing report validates only the
fields actually supplied.

## Comparison rules

Default tolerances are:

```text
ayanamsha: 0.01 degrees
longitudes: 0.01 degrees
controlled score: 0.000001
```

Signs, dignity labels, Vargottama, relationships, bindus, and ranks are exact
comparisons. Every scalar produces a comparison record with the actual value,
reference value, difference where numeric, tolerance, status, and reason.

## External source provenance

Every comparison identifies:

- software or manual source name
- source version
- source kind
- calculation notes

Recommended calculation notes include the zodiac, ayanamsha, node type,
ephemeris, house convention, and any software-specific options.

## Completion policy

Version 1.0.0 requires two independent external sources for every frozen case.
No external snapshots are committed yet, so:

```json
{
  "committed_external_snapshot_count": 0,
  "externally_validated_case_count": 0,
  "external_reference_validation_complete": false
}
```

A disagreement must be investigated against calculation contracts and source
rules. The implementation must not choose whichever value appears in the most
programs without understanding the cause.

## Example partial comparison

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
      "sun": 212.0,
      "moon": 270.0
    },
    "d1_signs": {
      "sun": 8,
      "moon": 10
    }
  },
  "calculation_profile": "south_indian_drik_lahiri_v1",
  "tolerances": {
    "longitude_degrees": 0.01,
    "ayanamsha_degrees": 0.01,
    "score": 0.000001
  }
}
```

The comparison route calculates the frozen case at request time. It does not
persist or approve the submitted reference snapshot.

## Weighting boundary

`transparent_strength_weighting_v1` is an API convention, not a quotation from
Brihat Jataka. External Jyotisha programs are not expected to reproduce these
scores unless they intentionally implement the same published formulas. Raw
astronomical and classical fields should be validated before score comparison.

## Exclusions

The harness does not validate or produce:

- event predictions
- profession guarantees
- debilitation cancellations from unregistered texts
- birth-risk judgments
- health diagnoses
- longevity judgments
