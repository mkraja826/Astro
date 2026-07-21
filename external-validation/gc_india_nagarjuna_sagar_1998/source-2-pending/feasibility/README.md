# JPL Horizons + IAU SOFA/ERFA feasibility investigation

## Status

This directory is an investigation workspace, not formal Source 2 evidence.

- Case: `gc_india_nagarjuna_sagar_1998`
- Candidate: JPL Horizons + IAU SOFA/ERFA independent reference pipeline
- Decision: `investigation_incomplete`
- Comparison performed: no
- Formal `raw.json` populated: no
- Human approval: not requested or granted

Seven apparent geocentric planetary longitudes are independently obtainable
from retained JPL Horizons responses. The independent ascendant construction is
reproducible but provisional. The exact True Chitra ayanamsha construction and
the required Jyotisha true-node convention are unresolved, so the candidate is
not ready for formal capture.

## Scope and safeguards

The scripts in this directory:

- use only the frozen input and retained external responses;
- do not import the Jyothisyam production engine;
- do not read Source 1, frozen output, internal JPL baselines, or comparison
  results;
- do not use Swiss Ephemeris, PySwissEph, PyJHora, or another astrology API;
- do not modify production dependencies or configuration; and
- do not perform an external comparison.

The isolated environment is `C:\Astro\.source2-venv`. It is excluded locally
through `.git/info/exclude`, not through tracked production configuration.

## Artifacts

- `source-identity.md`: versions, licensing, and independence assessment
- `methodology.md`: requests, parsing, Spica experiment, ascendant method, and
  deterministic classifications
- `field-coverage.md`: required-field coverage and status
- `unresolved-questions.md`: blockers requiring authoritative resolution
- `decision.md`: single feasibility decision and acceptance-gate audit
- `environment.txt`: isolated runtime and exact package versions
- `raw-responses/`: unchanged external response bytes and request manifest
- `parsed-horizons.json`: generated parse of retained Horizons responses
- `ascendant-feasibility.json`: generated independent ascendant experiment
- `spica-feasibility.json`: generated, explicitly unaccepted Spica experiment
- `scripts/`: fetch, parse, calculation, and boundary-test code

The numerical Horizons results are parsed from the retained response files and
are intentionally not retyped into the narrative documentation.

## Reproduction

From `C:\Astro`:

```powershell
& .\.source2-venv\Scripts\python.exe `
  .\external-validation\gc_india_nagarjuna_sagar_1998\source-2-pending\feasibility\scripts\parse_horizons.py
& .\.source2-venv\Scripts\python.exe `
  .\external-validation\gc_india_nagarjuna_sagar_1998\source-2-pending\feasibility\scripts\ascendant_erfa.py
& .\.source2-venv\Scripts\python.exe `
  .\external-validation\gc_india_nagarjuna_sagar_1998\source-2-pending\feasibility\scripts\spica_erfa.py
& .\.source2-venv\Scripts\python.exe -m unittest `
  .\external-validation\gc_india_nagarjuna_sagar_1998\source-2-pending\feasibility\scripts\test_classifications.py -v
```

`fetch_external_data.py` records new network responses and replaces files with
the same names. Do not rerun it when reviewing the retained capture. If a future
investigator intentionally performs a new capture, review the new access time,
URLs, response metadata, byte sizes, and SHA-256 hashes before accepting it.

## Official references

- [JPL Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons.html)
- [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html)
- [IAU SOFA current software](https://www.iausofa.org/current-software)
- [ERFA project](https://github.com/liberfa/erfa)
- [PyERFA project](https://github.com/liberfa/pyerfa)
- [IERS finals2000A metadata](https://datacenter.iers.org/versionMetadata.php?filename=latestVersionMeta%2F10_FINALS.DATA_IAU2000_V2013_0110.txt)
- [SIMBAD Spica record](https://simbad.cds.unistra.fr/simbad/sim-basic?Ident=Spica)
