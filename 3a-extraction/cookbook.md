# Extraction — what bites

| Issue | Fix |
|---|---|
| The tool suggests a taxonomy and it looks fine | It is plausible-but-slightly-different, and the difference surfaces three blocks later as a field nobody can find. Import `taxonomy.json` instead — `--skip-taxonomy` on create, then import. |
| A field you defined is not in the extraction | Reuse the built-in data types rather than defining your own where one fits. Custom types where a built-in exists are the commonest cause of a field the model never learns. |
| Everything resolves by title and then one command does not | Projects are addressed by **`Name`**, not `Title`. They differ, and the one that fails is not always the one you tested. |
| The damage table extracts as one blob | It needs per-occurrence confirmation during labelling. One row per item is the whole point of that group — a blob passes labelling and fails every downstream check. |
| Retraining seems stuck | It is automatic and slower than it feels. Check state rather than re-triggering; a second train on top of a running one costs the first. |
| The model is published and calls to it fail | **Publishing is not deploying.** A published version still needs a folder deployment before anything can call it. |
| Labelling feels endless | You are the reviewer, not the extractor. Correct what the model got wrong and move on; re-entering values it already has right teaches it nothing. |

## Proving it is done

A claim form you never labelled, back with every field group populated and damage rows repeating one per item. **Test on an unlabelled form** — a form from the training set proves only that it memorised.
