# Extraction

## How it is built here

- **Two claims**: run `Retrieve Property Claim` with two different `in_ProfileId` values (two random draws can be the same claimant), then `Extract Claim Data (IXP)` on each form (`contracts/provided-processes.md` has both argument lists).
- **Six field groups**: `Claim`, `ClaimClaimant`, `ClaimProperty`, `ClaimIncident`, `ClaimDamageInventory`, `ClaimClaimTotals`; the damage inventory repeats one row per item.
- **Key spellings come from the live result**, never from the form's labels: `TypeOfIncident`, never `TypeofIncident`. Correct `sdd.md` wherever a binding differs.
- **The gate**: save one payload and run `python3 3a-extraction/check_extraction_keys.py <payload.json>`; it walks every path `sdd.md` and every `caseplan.case` read, through aliases, array callbacks and the raw output name. Run it again after every case plan edit that touches the claim data. A `NOTE` is an expression it could not follow; check that one by hand.
- **In `PROGRESS.md`**: the IXP project name and the `live` tag the automation runs.

## What bites

| Issue | Fix |
|---|---|
| `uip ixp deployments list` on the shared project returns `[]` | Nothing is missing. The provided `Extract Claim Data (IXP)` automation is **pinned** to the shared project — project id, `live` tag and a model version are literals in its workflow, so a newer version in the project is not what it runs; only the `Claims` bucket is a deploy-time binding. It needs no folder deployment,. |
