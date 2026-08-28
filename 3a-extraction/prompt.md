# Reuse — Claim Form IXP extraction

The claim form (FNOL) is the one document that arrives as a **structured form**, so it is read into fields with IXP. The other two — the policy and the assessor's report — are prose and stay documents; the agents read them directly (`PDD.md` §5.6).

**The IXP project already exists.** `CONFIG.md` names the shared one, published and tagged `live`, and the provided `Extract Claim Data (IXP)` automation is already wired to it — `contracts/provided-processes.md` says what it takes and what it returns. Nothing is created in this block. **Point your design's extraction step at that automation and prove the reading before anything downstream binds to it.**

Three things I care about:

- **Run one generated claim through it and read the payload beside the form.** Every one of the six field groups present (`Claim`, `ClaimClaimant`, `ClaimProperty`, `ClaimIncident`, `ClaimDamageInventory`, `ClaimClaimTotals`), the damage rows repeating one per item — not one blob.
- **Pin the field-key spellings from what came back, not from the labels.** `contracts/provided-processes.md` lists the keys the shared model emits; confirm them against a live result and correct `sdd.md` wherever a binding spells one differently (`TypeOfIncident`, never `TypeofIncident`). Every such binding is optional-chained, so a wrong key never throws — it yields nothing, three blocks later. Save the payload and let the checker walk every path the design reads:

  ```bash
  python3 3a-extraction/check_extraction_keys.py <payload.json>
  ```
- **Write down what you used** — the project name and the model version — in `PROGRESS.md`. A later reader of your solution has to be able to tell where the extracted data came from.

**Done when** a claim form you have never seen comes back with every field group populated, the damage rows repeating correctly, and every key your design reads confirmed against a real payload. Ten minutes, and then the interesting part begins.

Want the IXP craft itself — training, labelling, publishing your own IXP project? That is `3a-extraction/prompt-build.md`, a supported route with the same output shape. Take it only if you have the hour.
