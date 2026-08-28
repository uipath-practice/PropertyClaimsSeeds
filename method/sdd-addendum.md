# SDD addendum — the two sections the seed adds to the planner's template

`uipath-planner` writes the Case Management SDD from its own template, and that template is what the case build reads. It has no data-model section and no channel back to the PDD, and both are load-bearing here: the claim entity is the contract every component binds to, and a design that changes the process has to say so where the PDD's owner will see it. The planner's template is a **superset contract** — extra sections are allowed — so `1-design` asks for these two to be added after `## Section 4: Integrations`, headings exactly as written.

**Why the Write-Ownership Matrix matters more than it looks.** A design once gave three columns to their producers in the entity table and to a later task in the matrix; the build followed the matrix, and that task was handed three 10,000-character inputs it never read and could not start. `1-design/check_sdd.py` (`OWN-1`) compares the two tables — it can only do that if both exist.

Placeholders: `<UPPER_SNAKE_IN_ANGLES>` replace · `—` not applicable · `> None.` empty family.

---

## Data Model

<!--
ADDITION — not in the shipped template, and `uipath-maestro-case` records entity schemas as
"not covered" notes rather than building them. Entities are built by `uipath-platform` as an
EARLIER task; the case references them as =datafabric.<Entity>.<field>.

Use ONLY these field types: STRING, MULTILINE_TEXT, MULTILINE_MAX, DECIMAL (+decimalPrecision),
BOOLEAN, DATE, DATETIME_WITH_TZ, FILE, CHOICE_SET_SINGLE, CHOICE_SET_MULTIPLE, AUTO_NUMBER,
RELATIONSHIP. Avoid INTEGER, FLOAT, UUID and plain DATETIME — accepted by the API, broken in the UI.
Field names: letters and digits only. A field cannot share its entity's name. Reserved:
Id, CreatedBy, CreateTime, UpdatedBy, UpdateTime, RecordOwner.
FILE fields need a 3-step write (create entity → insert record without the file → upload file)
and have NO automatic retention — design cleanup explicitly.
-->

### Case Entity — <EntityName>

| Field | Type | Required | Constraints | Source | Written by | Description |
|---|---|---|---|---|---|---|
| <FieldName> | <TYPE> | <Yes \| No> | <lengthLimit / min / max / decimalPrecision> | <SYSTEM_OR_TASK> | <COMPONENT> | <MEANING> |

### Documents

| Document type | Arrival channel | Storage | Processing route | Retention |
|---|---|---|---|---|
| <TYPE> | <CHANNEL> | <STORAGE> | IXP model <NAME> \| Agent \| None | <PERIOD \| explicit cleanup by <COMPONENT>> |

### Additional Entities

| Entity | Purpose | Relationship | Cardinality | Owning side |
|---|---|---|---|---|
| <NAME> | <PURPOSE> | <RELATED_ENTITY> | <1:N \| N:1> | <ENTITY> |

### Choice Sets

<!-- Values are stored as integer NumberIds assigned 0-based by creation order — record the real
     map after creation; never write labels into records. -->

| Choice set | Values (in creation order) | Used by field |
|---|---|---|
| <NAME> | <VALUE_1>, <VALUE_2>, <VALUE_3> | <ENTITY>.<FIELD> |

### Virtual / External Data

| Object | Source system | Connection | Lookup key | Fields exposed |
|---|---|---|---|---|
| <NAME> | <SYSTEM> | <CONNECTION> | <KEY> | <FIELDS> |

### Write-Ownership Matrix

| Entity.Field | Single owning component | When it is written |
|---|---|---|
| <ENTITY>.<FIELD> | <COMPONENT> | <TRIGGER_POINT> |

---

## Design Feedback to PDD

<!-- ADDITION. Technology-driven changes are recorded only. Business-process changes require a
     PDD re-baseline and re-signature, because a business user signed the previous version. -->

| # | PDD section / step | What the design changed | Reason | Impact class |
|---|---|---|---|---|
| 1 | <SECTION> | <CHANGE> | <REASON> | Technology-driven \| Business-process-driven |

---
