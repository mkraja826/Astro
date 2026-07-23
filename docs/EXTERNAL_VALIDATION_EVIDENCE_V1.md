# External Validation Evidence Manifest v1

## Purpose

This manifest is the only source of truth for claims that Jyothisyam has been
independently validated. Internal JPL regression snapshots protect the engine from
drift, but they never count as external evidence.

Committed manifest:

```text
app/data/validation/external_v1/manifest.json
```

Public verification endpoint:

```http
GET /v1/classical/varahamihira_v1/validation/external/manifest
```

## Approval threshold

A frozen case becomes externally validated only when the manifest contains at
least two **approved** records with distinct `source_id` values for that case.
The complete validation program requires this threshold for all twelve frozen
cases.

The API derives all counts from manifest records. Hand-edited count fields are not
accepted.

## Required evidence record

Every record must contain:

- immutable `snapshot_id`
- frozen `case_id`
- stable independent `source_id`
- source name, version, kind, and calculation notes
- repository-relative JSON `snapshot_path`
- lowercase SHA-256 digest of that file
- review status
- reviewer identity and UTC review time for approved records
- review notes explaining settings and discrepancy resolution

`internal_baseline` is rejected as an external source kind.

## Evidence file content

Store the normalized external snapshot plus the original source provenance. At a
minimum preserve the exact settings needed to reproduce the export:

- sidereal or tropical zodiac
- ayanamsha and software option used
- true or mean node
- ephemeris or calculation mode where exposed
- local civil time, timezone, latitude, longitude, and altitude
- house/sign convention
- exported field groups
- original export filename or report identifier

Do not commit personal contact information or unrelated source files.

## Review workflow

1. Export one frozen case from an independent Jyotisha program.
2. Normalize it through `POST .../validation/normalize/external`.
3. Compare it through `POST .../validation/compare`.
4. Investigate every mismatch against the calculation contracts and source settings.
5. Commit the normalized evidence JSON under `app/data/validation/external_v1/`.
6. Compute its SHA-256 digest.
7. Add one pending manifest record.
8. Have a reviewer verify provenance, settings, digest, and discrepancy notes.
9. Change the record to approved with reviewer identity and UTC timestamp.
10. Run Ruff and the full pytest suite before merging.

## Independence rules

- Two exports from different versions of the same underlying program do not
  automatically constitute two independent sources.
- A copied report, reformatted file, or API wrapper around the same engine counts as
  the same source.
- The same `source_id` may contribute to multiple frozen cases but only once per case.
- Majority agreement is not proof. A discrepancy must be understood before approval.

## Current truthful state

Version 1.0.0 intentionally begins with zero records, zero approved snapshots, and
zero externally validated cases. The manifest framework is complete; the evidence
collection program is not.
