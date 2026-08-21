# Building the IXP project — platform notes

Friction other builds met, and the commands that show what is actually happening.

## Skills, and the order that works

**Skill.** `uipath-ixp`.

Six steps, and the last one has no CLI equivalent:

1. **Generate 10–15 sample claims** and download the claim-form PDFs from the `Claims` bucket. Do not pin a
   scenario — you want the natural mix of countries, currencies, incident types and damage-row counts. *(Only the
   claim form is extracted; the policy and the assessor's report are read as documents later, not extracted.)*
2. **Create the project blank and import the taxonomy** — `--skip-taxonomy`, then `import-taxonomy` with
   `1-extraction/taxonomy.json`, verbatim.
3. **Label every document** — confirm what is right, leave what is wrong unannotated.
4. **Iterate on the low scorers** by improving a field's instructions and letting it retrain (~2 min a round),
   rather than by labelling more documents.
5. **Publish** the model and tag it live.
6. **Bind it to your folder in the IXP interface.** No CLI equivalent exists, and until you do it the model is
   not callable from an automation — which surfaces two blocks later as an extraction that returns nothing.

**Title the project `ClaimCase-<seat>`**, the same string as everything else you create (`CONFIG.md`, *One name,
everywhere*).

**Field types come from the imported taxonomy and are deliberate.** Most are `Exact Text`; do not "improve" them.

## Proving it is done

```bash
uip ixp projects get-metrics <project-name> --output json     # a real score, not "not validated yet"
uip ixp projects list-models <project-name> --output json     # a version tagged live
```

Neither is the real test — run an unseen claim form through and read the six groups yourself. A score is the
model agreeing with its own training.

## Adopting the shared project

`CONFIG.md` names it. Nothing has to be created, and nothing about the shared project is yours to change — other
seats are reading the same model.

```bash
uip ixp projects list --output json                            # it is visible to you
uip ixp projects list-models <project-name> --output json      # it has a version tagged live
```

Then run one generated claim form through it and read the six groups. Record the project name and the model
version in your notes: later blocks bind to it, and your solution's own documentation should say which
extraction it used.

## Use the project's `Name`, never its `Title`

`projects list` returns both. `Title` is what you typed (`Claim_Forms`); `Name` is a lowercase slug with a UUID
and an `-ixp` suffix (`claim_forms-f1afa9ef-ixp`). **Every command wants `Name`.** Passing the title gets a
not-found that reads as though the project does not exist.

## Import the taxonomy rather than accepting the suggestion

`projects create` will suggest a taxonomy from the documents, and it will be plausible and wrong in small ways —
a group named `Claimant` instead of `ClaimClaimant`, an amount typed as text. Those differences surface three
blocks later as an app rendering nothing.

```bash
uip ixp projects create "<title>" <docs-dir> --skip-taxonomy --output json
uip ixp projects import-taxonomy <project-name> <taxonomy-file> --output json
```

One shape trap: `projects get-taxonomy` returns `{ status, dataset: { entity_defs, label_groups } }`, and
`import-taxonomy` reads those keys at the **top level** — pass the inner `dataset` object, not the whole response.

## Reuse the built-in data types

Every project ships with `Exact Text`, `Inferred Text`, `Number`, `Date`, `Monetary Quantity`, `Boolean`. Use
`Monetary Quantity` for money and `Date` for dates rather than hand-rolling a type that formats the same way —
the built-ins are pre-trained and a custom clone is not, so the clone extracts worse for no benefit.

## You are the reviewer, not the extractor

The model predicts; you confirm what is right and leave what is wrong **unannotated**. Do not type the correct
value in — a wrong prediction you "fix" teaches the model that its wrong answer was right.

The one exception is genuine OCR garble, where the prediction found the right thing in the right place and
misread the characters (`MSIÓÓÓ601020` → `MSI0601020`). Test before every correction: *is this the correct
answer, merely mis-typed?* If no — a number that should be different, a boolean that should flip — leave it
alone.

```bash
uip ixp labellings get-predictions <project-name> <document-id> --output json
uip ixp labellings confirm <project-name> <document-id> --fields <ids> --output json
```

**A high score is not evidence of correct extraction.** F1 measures prediction-versus-confirmed-label agreement,
so anything you blind-confirm scores 1.00 by construction. Check each value against the document before
confirming it.

## The damage table needs per-occurrence confirmation

`ClaimDamageInventory` produces one occurrence per row. `confirm --fields <id>` confirms that field in **every**
occurrence — so if rows 1 and 3 are right and row 2 is wrong, the plain form confirms the wrong one too.

```bash
# one occurrence, 0-based, --group takes the FULL label path
uip ixp labellings confirm <project> <doc> --group "Claim > ClaimDamageInventory" --occurrence 2 --output json
```

## Retraining is automatic, and slower than it feels

Any change to labels or instructions triggers a full retrain, roughly two minutes. If the model version has not
advanced or the metrics have not moved, that is almost always the answer — wait and re-read rather than changing
something else.

```bash
uip ixp projects list-models <project-name> --output json    # has the version advanced?
uip ixp projects get-metrics <project-name> --output json    # per-field F1, lowest first
```

When a field scores badly, fix its **instructions** rather than labelling harder:
`uip ixp fields update-prompts`. Check the parent group's instructions too — they can contradict a field prompt,
and the group wins.

## Publishing is not deploying

```bash
uip ixp projects publish <project-name> --tag live --output json
```

That makes the version live *within IXP*. **Binding it to an Orchestrator folder so an automation can call it is
a product-side step with no CLI equivalent** — do it in the IXP interface. Nothing in the CLI will tell you this
is missing; the model simply is not there when your case plan looks for it.
