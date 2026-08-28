# Extraction — what bites

## On the reuse route — the one `prompt.md` sends you down

| Issue | Fix |
|---|---|
| Everything resolves by title and then one command does not | Projects are addressed by **`Name`**, not `Title` (`property-claims-shared-…-ixp`, not *Property Claims Shared*). They differ, and the one that fails is not always the one you tested. |
| `uip ixp deployments list` on the shared project is empty and you go looking for the deployment | There is none, and none is needed. The provided `Extract Claim Data (IXP)` automation is **pinned** to the shared project — project id, `live` tag and version are literals in its workflow, not deploy-time bindings (only the `Claims` bucket is). **Publishing is not deploying**, but the only caller here resolves nothing by folder. |
| `uip or buckets files` — *unknown command* | Bucket contents are a noun of their own: `uip or bucket-files list <bucket-key> --folder-key <seat folder>`. |
| `check_extraction_keys.py` says *no paths found* on a design that plainly reads the extraction | It walks `vars.claimData?…` and `vars.claimDataJson?…` (the object and its stringified column copy — `contracts/claim-entity.md`). A design that holds the payload under a third name has to rename, not the checker; say which name in `PROGRESS.md`. |
| The confidence numbers do not mean what a threshold rule assumes | Three states, not two — `contracts/provided-processes.md`, *Three value shapes*. Both `-1.0` with an empty value is *nothing found*, and a blank optional row is not a data problem. |

## If you train your own — `prompt-build.md`

| Issue | Fix |
|---|---|
| The tool suggests a taxonomy and it looks fine | It is plausible-but-slightly-different, and the difference surfaces three blocks later as a field nobody can find. Import `taxonomy.json` instead — `--skip-taxonomy` on create, then import. |
| A field you defined is not in the extraction | Reuse the built-in data types rather than defining your own where one fits. Custom types where a built-in exists are the commonest cause of a field the model never learns. |
| The damage table extracts as one blob | It needs per-occurrence confirmation during labelling. One row per item is the whole point of that group — a blob passes labelling and fails every downstream check. |
| Retraining seems stuck | It is automatic and slower than it feels. Check state rather than re-triggering; a second train on top of a running one costs the first. |
| Your own model is published and an automation cannot call it | **Publishing is not deploying.** A published version needs a folder deployment (`uip ixp deployments create`) before an automation that resolves it by folder can call it. |
| You trained and deployed your own model and the extraction still reads with the shared one | The provided automation is pinned to the shared project (above). Deploying your model to your folder changes nothing it reads; see `prompt-build.md`, *Open*. |
| Labelling feels endless | You are the reviewer, not the extractor. Correct what the model got wrong and move on; re-entering values it already has right teaches it nothing. |

## Proving it is done

Two claim forms you never labelled, back with every field group populated and damage rows repeating one per item — and `python3 3a-extraction/check_extraction_keys.py <payload.json>` exiting 0 on each, which says every `vars.claimData?…` / `vars.claimDataJson?…` path in `sdd.md` resolves on that payload. **Test on an unlabelled form** — a form from the training set proves only that it memorised.
