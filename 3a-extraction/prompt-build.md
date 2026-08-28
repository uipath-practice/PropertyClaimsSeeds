# Build — your own Claim Form IXP extraction

> **Draft — the reuse route (`prompt.md`) is the default.** This one is for the seat that wants the IXP craft: training an extraction model is its own skill, and it is not what the rest of the exercise is about. Extraction feeds everything after it, so a half-trained IXP project of your own is worse than the shared one — **switch to `prompt.md` the moment this stops being the interesting part of your day.** Every block after this one is identical either way, because both routes produce the same field groups under the same keys.

The claim form (FNOL) is the one document that arrives as a structured form, so it is read into fields with IXP. The policy and the assessor's report are prose and stay documents; the agents read them directly (`PDD.md` §5.6).

Use the **`uipath-ixp`** skill: create an IXP project for the claim form, train it, publish it, and deploy it to **your** Orchestrator folder.

> **Open — how your model gets called is not settled yet.** The provided `Extract Claim Data (IXP)` automation is pinned to the shared project (project id, `live` tag and version are literal in its workflow; only the `Claims` bucket is a deploy-time binding), so deploying your model to your folder changes nothing it reads. The route that fits the contract is a copy of that automation re-pointed at your project and published in your folder under the same name — and the seed does not ship its source yet. Until it does, this route ends at a trained, published, deployed model proven on an unseen form, and the case still reads through the shared one.

Three things I care about:

- **The fields are already agreed — import them, do not invent them.** `3a-extraction/taxonomy.json` is the artifact: import it verbatim (`--skip-taxonomy` on create, then import) and never accept the tool's own suggestion. A suggested taxonomy is plausible and slightly different, and slightly different surfaces three blocks later as a key nobody can find. The six group keys and their field spellings are a contract (`contracts/provided-processes.md`), and every later component was designed against them.
- **Variety, not volume.** Ten to fifteen claim forms, drawn without aiming a scenario — run the claim generator unaimed, or pull forms already sitting in the `Claims` bucket — so you get the natural spread of countries, currencies, incident types and one-to-five damage rows. Then label: **confirm what is right, leave what is wrong unannotated**. Correcting a wrong prediction by typing the right value teaches the model its wrong answer was right; the damage table needs per-occurrence confirmation or you confirm the wrong rows too.
- **Publishing is not deploying.** A published, `live`-tagged version is still not callable from any automation until it is deployed to your folder (`uip ixp deployments create`) — and nothing in the CLI tells you it is missing; an automation pointed at it simply returns nothing. Name the project `ClaimCase-<seat>` (`CONFIG.md`, *One name, everywhere*).

**Done when** a claim form you never labelled comes back with every field group populated and the damage rows repeating one per item — read beside the document, not as a score; a score only says the model agrees with what it was taught — and the model is deployed to your folder under a version you can name.

`3a-extraction/cookbook.md` has the traps: `Name` versus `Title`, the suggested taxonomy, blobs in the damage table, retrains that seem stuck.
