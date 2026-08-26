# The Data Fabric entity — what bites

| Issue | Fix |
|---|---|
| A JSON column silently truncates to 200 characters | The limit defaults to 200 and **the default is the trap**. Set every `MULTILINE_TEXT` explicitly. [`contracts/claim-entity.md`](../contracts/claim-entity.md) has the numbers. |
| `Missing permissions` / `You don't have permission to access the entity` on create | You created at tenant level. It goes in your **seat folder** — pass `--folder-key`. The message names permissions and the cause is scope. |
| The hyphen that works everywhere else is rejected | The record name takes letters, digits and underscores only and must start with a letter. `ClaimCase_Jane`, not `ClaimCase-Jane`, and never `ClaimCaseJane`. |
| A field type is accepted on create and renders broken in the UI | Six are. Use only the types [`contracts/claim-entity.md`](../contracts/claim-entity.md) lists — `INTEGER`, `FLOAT`, `UUID` and plain `DATETIME` are the ones to avoid. |
| `get`, edit, `update` does not round-trip | `update` takes a different body shape from the one `get` returns. **Create fresh from a file** — one call, no repair. |
| You created your own connection | One already exists and is shared — `CONFIG.md`, *The claim entity*. A second one works until two seats disagree about which. |
| A column is wrong and the record has rows | Changing a column after the fact is possible and narrower than it looks. Cheaper to delete and recreate while the only rows are yours. |

## Proving it is done

Round-trip a decimal **with cents** and a ~9,000-character payload, read both back unchanged, then delete the row. Both failure modes — a wrong decimal precision, a defaulted length limit — are **silent and neither errors on create**. Nothing else distinguishes a correct schema from a plausible one.

`get` also echoes limits on columns that have none and adds a system field you did not define. Neither is drift.
