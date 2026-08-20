# Block 3 — the claim record

**Goal.** Create the Data Fabric case entity that holds one row per claim, so every later step has somewhere to write
and the reviewer's screen has somewhere to read from.

**Read.** `contracts/claim-entity.md` · `pdd.md` §8 (why the record exists at all) · `CONFIG.md` ·
`3-claim-record/cookbook.md`

**Must hold.**

- Every payload your design produces has a column, and the column types match the contract.
- **The schema is already approved.** `contracts/claim-entity.md` fixes all 38 columns, their types and the
  length limits that matter, so nothing here is inferred and there is no type for anyone to arbitrate. Show the
  preview if your tooling asks for one — then treat this line as the confirmation it is waiting for and create
  the entity.
- **The entity is created in your seat folder**, not at tenant level (`CONFIG.md`). A tenant-level create is
  refused with a message about permissions rather than about scope.
- The entity name carries your seat token, and uses underscores — `ClaimCase_07`, not `ClaimCase-07`.
- You have not exceeded the platform's cap on large-text columns. Count them before you create, not after.
- **The Data Fabric connection already exists and is shared.** Find it, confirm it answers, and record its name
  and folder — block 5 binds it. Do not create one.

**Done when.**

```bash
uip df entities list --native-only --folder-key <your-seat-folder-key> --output json   # your entity is there
uip df entities get <entity-id> --folder-key <your-seat-folder-key> --output json      # every contract column
uip is connections list uipath-uipath-dataservice --refresh --all-folders --output json  # the shared connection
```

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
