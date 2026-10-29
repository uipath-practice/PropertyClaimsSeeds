# Claim form extraction

The claim form is the one document that arrives as a structured form, so it is read into fields with IXP. The policy and the assessor's report are prose; the Agents read them directly.

**Nothing is built in this block.** The shared IXP project already exists and the provided extraction automation is wired to it (`CONFIG.md`, `contracts/provided-processes.md`). Prove that it reads the way your design expects before anything depends on it.

Steps:
1. Run two newly generated claims, for two different claimants, through the extraction automation.
2. Read each result beside its form: every field group present, and the damage items as one row each, not one blob.
3. Check every field your design reads against the real result, and correct the design wherever it spells a field differently.
4. Write down which project and model you used in `PROGRESS.md`.

**Done when** two claim forms you have never seen come back with every field group populated, the damage rows repeating correctly, and every field your design reads confirmed against a real result.
