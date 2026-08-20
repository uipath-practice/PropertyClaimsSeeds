# Block 1a — build your own extraction project

**Goal.** Create, train and publish an IXP project that turns the claim submission form into the six field
groups every later block consumes.

**Read.** `1-extraction/spec.md` (what to build and what "done" means) · `1-extraction/taxonomy.json` (import this verbatim) and
`1-extraction/taxonomy.md` (what is in it) · `1-extraction/cookbook.md` (the traps) · `CONFIG.md` (your folder)

**Skill.** `uipath-ixp`.

**Do.**

1. **Generate samples.** Run the provided `Retrieve Property Claim` process 10–15 times without pinning a
   scenario, so you get the natural mix of countries, currencies, incident types and damage-row counts. Download
   the claim-form PDFs from the `Claims` bucket. *(The policy and assessor report are not extracted — skip them.)*
2. **Create the project blank and import the taxonomy** — `--skip-taxonomy`, then `import-taxonomy` with
   `1-extraction/taxonomy.json`. Do not accept a suggested taxonomy: it will be close, and close fails at the
   consumer.
3. **Label every document.** Review each prediction against the document and confirm what is correct. Leave
   wrong predictions unannotated — never type the right answer in.
4. **Iterate on the low scorers.** Where a field scores badly, improve its instructions and let it retrain
   (~2 min per round), rather than labelling more.
5. **Publish** the model and tag it live.
6. **Bind it to your folder in the IXP interface.** This one step has no CLI equivalent — the model is not
   callable from an automation until you do it.

**Must hold.**

- The six group names match `1-extraction/taxonomy.md` exactly. A renamed group is a broken build three blocks later.
- **Title the project for your seat** — `ClaimCase-<NN>`, the same string as everything else you create
  (`CONFIG.md`, *One name, everywhere*). The platform derives its own lowercase slug `Name` from your title, and
  that slug is what every later command wants.
- A five-row claim returns five occurrences of `ClaimDamageInventory`. Confirm those **per occurrence** — the
  plain form confirms a field in every occurrence, including the ones that extracted wrong.
- Field types match the imported taxonomy. Most are `Exact Text` deliberately; do not "improve" them.
- You confirmed values you actually checked. A blind-confirmed field scores 1.00 and is still wrong.

**Done when.**

```bash
uip ixp projects get-metrics <project-name> --output json     # a real score, not "not validated yet"
uip ixp projects list-models <project-name> --output json     # a version tagged live
```

Plus, by inspection: a claim form the project has never seen returns all six groups, with the right number of
damage rows.

**If it stalls, switch.** Use `1-extraction/prompt-shared.md` and move on. Extraction feeds everything downstream, so a
half-trained project is worse than a borrowed one — and the rest of the exercise is identical either way.

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
