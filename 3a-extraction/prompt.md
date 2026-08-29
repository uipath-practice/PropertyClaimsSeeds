# Reuse — Claim Form IXP extraction

The claim form (FNOL) is the one document that arrives as a **structured form**, so it is read into fields with IXP. The other two — the policy and the assessor's report — are prose and stay documents; the agents read them directly (`PDD.md` §5.6).

**The IXP project already exists.** `CONFIG.md` names the shared one, published and tagged `live`, and the provided `Extract Claim Data (IXP)` automation is already wired to it — `contracts/provided-processes.md` says what it takes and what it returns. Nothing is created in this block. Point your design's extraction step at that automation and prove the reading before anything downstream binds to it.

- **Run two generated claims through it and read a payload beside its form.** Check that the key set does not vary and the damage inventory repeats per row. Every one of the six field groups present (`Claim`, `ClaimClaimant`, `ClaimProperty`, `ClaimIncident`, `ClaimDamageInventory`, `ClaimClaimTotals`), the damage rows repeating one per item, not one blob.
- **Pin the field-key spellings from what came back, not from the labels.** `contracts/provided-processes.md` lists the keys the shared model emits; confirm them against a live result and correct `sdd.md` wherever a binding spells one differently (`TypeOfIncident`, never `TypeofIncident`). 

Save the payload and let the checker walk every path the design reads:

  ```bash
  python3 3a-extraction/check_extraction_keys.py <payload.json>
  ```
- **Write down what you used** — the project name and the model version — in `PROGRESS.md` for the next stages.

Training your own model instead of reusing the shared one: `3a-extraction/prompt-build.md` — same output shape, about an hour.

**Done when:** 
- two claim forms you have never seen come back with every field group populated, the damage rows repeating correctly, and every key your design reads confirmed against a real payload. 
