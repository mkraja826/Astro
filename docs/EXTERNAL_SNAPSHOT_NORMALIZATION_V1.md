# External snapshot normalization v1

## Purpose

Independent Jyotisha programs use different labels and export shapes. The
normalization endpoint converts a supported generic JSON export into the existing
`GoldenChartSnapshot` contract before comparison.

Normalization does not persist, approve, or count an external source as validated.
A reviewed comparison from two independent sources per frozen case is still
required.

## Endpoint

```http
POST /v1/classical/varahamihira_v1/validation/normalize/external
```

## Supported format

```text
generic_json_v1
```

The payload can be supplied directly or wrapped in `snapshot`,
`reference_snapshot`, `chart`, or `data`.

## Common aliases

The normalizer supports common English and Jyotisha names, including:

- Ascendant, Asc, Lagna, Lagnam
- Sun, Surya, Ravi
- Moon, Chandra, Soma
- Mars, Mangala, Kuja
- Mercury, Budha
- Jupiter, Guru, Brihaspati
- Venus, Shukra, Sukra
- Saturn, Shani, Sani
- Rahu, North Node, Ascending Node, True Node, Mean Node
- Ketu, South Node, Descending Node

It also accepts English or common Sanskrit sign names, for example Aries/Mesha,
Libra/Tula, Sagittarius/Dhanu, and Pisces/Meena.

## Supported snapshot groups

- ayanamsha
- ascendant longitude
- planetary or point longitudes
- D1/Rasi signs
- D9/Navamsa signs
- dignity
- Vargottama
- compound relationships
- Bhinnashtakavarga
- Sarvashtakavarga
- controlled weighting scores and ranks

Unknown fields are returned in `ignored_paths`. Alias changes and convention-sensitive
node handling are visible in `normalized_aliases` and `warnings`.

## Example

```json
{
  "source": {
    "source_name": "Independent Jyotisha Program",
    "source_version": "1.0",
    "source_kind": "external_software",
    "calculation_notes": [
      "Sidereal zodiac",
      "Chitrapaksha ayanamsha",
      "True node"
    ]
  },
  "format": "generic_json_v1",
  "payload": {
    "chart": {
      "ayanamsa": 23.81619793,
      "lagna_longitude": 246.88818395,
      "planetary_longitudes": {
        "Surya": 188.75805003,
        "Chandra": 252.25373490,
        "True Node": 125.20717069,
        "Ketu": 305.20717069
      },
      "rasi_signs": {
        "Lagna": "Dhanu",
        "Surya": "Tula",
        "Chandra": 9
      },
      "navamsha_signs": {
        "Lagna": "Mithuna",
        "Surya": "Dhanu",
        "Chandra": "Karka"
      }
    }
  }
}
```

The returned `snapshot` can be copied into `reference_snapshot` for:

```http
POST /v1/classical/varahamihira_v1/validation/compare
```

## Safety boundaries

- Internal-baseline provenance is rejected by this endpoint.
- Unsupported labels fail explicitly instead of being guessed.
- Unknown planets or fields are ignored with warnings.
- True-node and mean-node names normalize to Rahu, but the source convention must
  remain recorded in `calculation_notes` and reviewed before approval.
- The normalizer never resolves disagreements or selects a majority result.
