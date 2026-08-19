# The claim-form taxonomy

**`1-extraction/taxonomy.json` next to this file is the artifact — import it, do not retype it and do not accept the one
IXP suggests.**

```bash
uip ixp projects create "<title>" <docs-dir> --skip-taxonomy --output json
uip ixp projects import-taxonomy <project-name> 1-extraction/taxonomy.json --output json
```

Six groups, 32 fields, one field group that repeats. This page says what is in it and which parts are
load-bearing.

## The groups, and where the payload keys come from

IXP names a nested group with a `>` path, and the extracted payload flattens that path into one key. **That is
where the key names come from** — change the path and every downstream reference changes with it.

| Group path in IXP | Payload key | Fields |
|---|---|---|
| `Claim` | `Claim` | Claim ID · Insurer Name · Insurer Address · Date of Submission |
| `Claim > Claimant` | `ClaimClaimant` | Name · Phone Number · Email Address · Policy Number |
| `Claim > Property` | `ClaimProperty` | Street Address · City · State · Zip Code · Primary Residence · Present At Incident |
| `Claim > Incident` | `ClaimIncident` | Date / Time / Type / Description of Incident · Police Report Filed + Number · Emergency Services Called · Temporary Repairs Made + Description |
| `Claim > Damage Inventory` | `ClaimDamageInventory` | Category · Location · Description · Estimated Cost · Repair or Replace |
| `Claim > Claim Totals` | `ClaimClaimTotals` | Total Structure Damage · Total Personal Property · Total Additional Living Expenses · Total Claim Amount |

Field names lose their spaces in the payload: `Claim ID` → `ClaimID`, `Date of Incident` → `DateOfIncident`.

## Damage Inventory repeats, and nothing declares it

The Section 4 table carries one to five rows and IXP returns **one occurrence of the group per row**. There is no
"repeatable" flag to set — occurrences are how extraction works.

Where that does bite is **labelling**: confirming a field confirms it in *every* occurrence, so a document whose
rows 1 and 3 extracted correctly and row 2 did not needs per-occurrence confirmation, or you confirm the wrong
one too. `1-extraction/cookbook.md` has the command.

## Types are chosen, not inherited

Three rules decided every type here:

- **Money is `Monetary Quantity`** — the five amount fields. It is pre-trained on amounts, which extracts better
  than reading them as text, and it carries the currency rather than discarding it. Claims arrive in several
  currencies and are **never converted**, so the currency travelling with the number is the point.
- **Real dates are `Date`; everything identifier-shaped stays `Exact Text`.** `Date of Incident` and `Date of
  Submission` are dates and the filing-deadline check subtracts one from the other. But Claim ID, Policy Number,
  Zip Code and Phone Number stay text on purpose — they are identifiers, and a type that normalises them (drops a
  leading zero, reformats a prefix) breaks the join to the policy.
- **Yes/No answers are `Boolean`** — the four emergency-response and property questions.

**Reuse the six built-in types** (`Exact Text`, `Inferred Text`, `Number`, `Date`, `Monetary Quantity`,
`Boolean`). They are pre-trained; a custom type that formats identically extracts worse for no gain.

## Every field carries an instruction, and they do real work

The form has a fixed layout, so each instruction names the section and the label **as printed** — which matters
most where the printed label and the field name differ:

| Field | Printed on the form as |
|---|---|
| `Type of Incident` | "Type of Loss" |
| `Location` | "Location in Home" |
| `Total Claim Amount` | "TOTAL CLAIMED AMOUNT" |
| `Primary Residence` | "Is this your primary residence?" |

Others rule out a wrong-but-plausible answer:

> **Date of Incident** — *"the 'Date of Incident' field only. Do NOT read a date out of the incident description."*
> **Insurer Address** — *"…in the top header. Not the insured property address in Section 2."*
> **State** — *"Legitimately blank in countries that have none — leave it empty rather than inventing one."*

When a field scores badly, **this is what to improve** — not more labelling.
