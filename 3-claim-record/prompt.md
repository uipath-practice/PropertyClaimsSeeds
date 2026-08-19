# Block 3 — the claim record

**Goal.** Create the Data Fabric entity that holds one row per claim, so every later step has somewhere to write
and the reviewer's screen has somewhere to read from.

**Read.** `contracts/claim-entity.md` · `pdd.md` §8 (why the record exists at all) · `CONFIG.md` ·
`3-claim-record/cookbook.md`

**Must hold.**

- Every payload your design produces has a column, and the column types match the contract.
- The entity name carries your seat token — entity names are tenant-scoped and will collide otherwise.
- You have not exceeded the platform's cap on large-text columns. Count them before you create, not after.

**Done when.**

```bash
uip df entities list --output json          # your entity exists, with your seat token
uip df entities get <entity-id> --output json   # every column from the contract is present
```

**Where it goes.** Generated code into `Build/ClaimCase<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** Keep `build-findings.md`: every retry, every surprise, and everything these instructions
failed to explain — what you tried, what happened, what you did next. Dead ends included; they are the point.
