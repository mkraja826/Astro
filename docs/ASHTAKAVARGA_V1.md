# Varahamihira Ashtakavarga v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/ashtakavarga
```

This endpoint calculates the raw Chapter 9 Ashtakavarga arrays described in the
pinned N. Chidambaram Aiyar edition of *Brihat Jataka*.

## Scope

The response contains:

- seven planetary Bhinnashtakavarga arrays;
- eight contributor rows for every planetary array;
- the seven classical Grahas plus Lagna as contributors;
- twelve bindu values and twelve complementary rekha values per Graha;
- sign-wise Sarvashtakavarga totals;
- house numbers from the D1 whole-sign Lagna;
- source positions, rule IDs, verse references, and invariant checks.

Rahu and Ketu are not contributors in the selected Chapter 9 tables.

## Source rules

The favorable relative-house tables are registered at verse precision:

| Target Graha | Verse | Fixed raw bindu total |
|---|---:|---:|
| Sun | 9.1 | 48 |
| Moon | 9.2 | 49 |
| Mars | 9.3 | 39 |
| Mercury | 9.4 | 54 |
| Jupiter | 9.5 | 56 |
| Venus | 9.6 | 52 |
| Saturn | 9.7 | 39 |

The raw Sarvashtakavarga total is therefore:

```text
48 + 49 + 39 + 54 + 56 + 52 + 39 = 337
```

Verse 9.8 is registered for the favorable/unfavorable framework and the raw
sign-wise aggregation exposed by this API version.

## Contributor rotation

For each target Graha and contributor:

1. Read the contributor's natal D1 sign.
2. Read the favorable relative houses registered for that target/contributor
   pair.
3. Count each relative house inclusively from the contributor's sign.
4. Place one bindu in every resulting zodiac sign.
5. Sum the eight contributor rows to obtain the target Graha's raw
   Bhinnashtakavarga.

For a contributor in sign index `s` and favorable relative house `h`, the target
sign index is:

```text
((s + h - 2) mod 12) + 1
```

## Bindu and rekha convention

This profile uses:

```text
bindu = favorable point = 1
rekha = non-bindu contribution = 0
```

The aggregate `rekhas_by_sign` field is returned as:

```text
8 - bindus_by_sign
```

This convention is explicitly frozen in `varahamihira_v1` to avoid the
bindu/rekha symbol reversal found in some later software and publications.

## Sarvashtakavarga

The v1 Sarvashtakavarga array is the sign-wise arithmetic sum of the seven raw
planetary Bhinnashtakavarga arrays. Lagna contributes inside each planetary
array but is not added as an eighth standalone Bhinnashtakavarga.

## Deliberately excluded

This milestone does not implement:

- Trikona Shodhana;
- Ekadhipatya Shodhana;
- reduced or corrected Pinda values;
- Kakshya transit timing;
- transit interpretation;
- auspicious or adverse prediction;
- strength ranking or combination with Daśā results.

Those require separately pinned formulas and validation fixtures.

## Invariants

The automated tests verify:

- seven target Grahas;
- exactly eight contributors per target;
- unique relative-house entries between 1 and 12;
- fixed raw totals of 48, 49, 39, 54, 56, 52, and 39;
- twelve sign values between zero and eight per Bhinnashtakavarga;
- rekha values equal to eight minus bindus;
- Sarvashtakavarga sign values equal the sum of the seven planetary values;
- total raw Sarvashtakavarga bindus equal 337;
- contributor signs and longitudes match the existing D1 endpoint;
- timezone and civil-time validation remains unchanged.

## Stability

This endpoint is deterministic and non-predictive. It does not modify the
existing D1, D9, Panchanga, Vimshottari, conditions, aspects, or career
calculation contracts.
