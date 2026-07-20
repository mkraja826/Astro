# Varāhamihira Karmājīva Career Analysis v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/career
```

The endpoint combines the existing D1 and D9 calculation contracts with the
pinned Chapter 10 vocation rules. It does not alter planetary longitudes,
Navāṁśa mapping, houses, Panchāṅga, or Vimśottarī calculations.

## Source scope

The registered rules cover Bṛhat Jātaka Chapter 10, verses 10.1–10.4, using the
profile's pinned 1905 N. Chidambaram Aiyar edition as the baseline.

Chapter 10.1 provides two distinct derivations:

1. Classical Grahas occupying the tenth sign from Lagna or Moon indicate
   source relationships through which wealth may arise.
2. For the tenth signs from Lagna, Moon, and Sun, calculate the tenth lord,
   find the Navāṁśa occupied by that lord, and use the lord of that Navāṁśa as
   the Karmājīva vocation indicator.

The pinned commentary explicitly permits multiple sources and all three
Navāṁśa-lord vocation channels. Therefore the API does not discard channels or
force one profession.

## Channel calculation

For each of `lagna`, `moon`, and `sun`:

1. Read the reference point's D1 sign.
2. Count inclusively to its tenth sign.
3. Return all seven-Graha occupants of that sign.
4. Map occupants to the Chapter 10.1 source relationships.
5. Find the classical lord of the tenth sign.
6. Calculate the D9 position of that tenth lord.
7. Find the lord of the resulting D9 sign.
8. Return the Chapter 10.2 or 10.3 vocation themes of that indicator.
9. Attach the indicator's D1 dignity, Vargottama, conjunction, and retrograde
   facts.
10. Attach all Bṛhat Jātaka 2.13 aspect rays reaching that tenth sign.

## Source relationship mapping

The seven Chapter 10.1 mappings are:

| Graha | Source relationship |
|---|---|
| Sun | Father |
| Moon | Mother |
| Mars | Enemy or competitor |
| Mercury | Friend or ally |
| Jupiter | Brother or sibling |
| Venus | Wife or women |
| Saturn | Servant or service relationship |

Rahu and Ketu are not inserted into this seven-Graha mapping.

## Vocation themes

The output preserves classical terms and adds cautious modern examples.
Modern examples are explanatory labels, not additional textual rules.

- Sun: perfumes or herbs, gold, wool, medicines, medical treatment
- Moon: agriculture, water-derived products, support through women
- Mars: metals, minerals, fire, weapons, bold or hazardous activity
- Mercury: writing, accounts, mathematics, literature, handicrafts, fine arts
- Jupiter: learned, religious, legal, charitable, mining, and contract activity
- Venus: gems, silver, valuable goods, cattle, and livestock
- Saturn: hard labour, carrying burdens, difficult manual or service work

The response uses plural themes rather than converting one classical category
into one guaranteed modern occupation.

## Ranking policy

Version 1 deliberately returns:

```json
{
  "primary_indicator": null,
  "ranking_applied": false
}
```

Repeated indicators are aggregated with a transparent `repetition_count`, but
repetition is not treated as a final strength score.

A future weighted version must first validate:

- natural and temporary friendship,
- complete planetary strength rules,
- cancellation and exception rules,
- benefic and malefic support,
- relevant Daśā activation.

## Evidence

Every channel includes evidence linked to these rule IDs:

- `VM-BJ-C10-INCOME-SOURCE-EVAL-001`
- `VM-BJ-C10-NAVAMSA-LORD-EVAL-001`
- `VM-BJ-C10-VOCATION-SUN-MERCURY-001`
- `VM-BJ-C10-VOCATION-JUPITER-SATURN-001`
- `VM-BJ-C10-SUPPORT-FACTS-EVAL-001`

## Scope limitations

This endpoint is an evidence-bearing classical analysis aid. It must not be
presented as employment advice, a hiring decision, or certainty about a
person's future. A chart can expose multiple livelihood channels, and actual
work depends on education, opportunity, place, period, choice, and social
conditions.
