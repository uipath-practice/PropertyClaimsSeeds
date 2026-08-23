# Checkpoint — the claim record

Restores block 3's output: the `ClaimCase_<seat>` entity, all 38 columns, correct types and length limits.

> **Re-synced 2026-08-23** against `contracts/claim-entity.md`. Until then this file carried no `lengthLimit`
> on any `STRING` and no `decimalPrecision` on either `DECIMAL` — so a seat that took the checkpoint to save
> twenty minutes got a reviewer's notes silently capped at 200 characters and settlements possibly rounded to
> whole units, which are the two failures that contract exists to prevent.

```bash
uip df entities create ClaimCase_<seat> --file entity.json --output json
```

Verify it took:

```bash
uip df entities get <entity-id> --output json
```

**What it costs you:** nothing conceptual. Block 3 is a contract in and a schema out — the thinking is in
`contracts/claim-entity.md`, and you still have to read that file to bind anything in block 5. Of all the
checkpoints, this is the one to use without hesitation if the CLI is fighting you.
