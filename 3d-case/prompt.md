# Build — the Maestro Case

Use the **`uipath-maestro-case`** skill and build the case from `sdd.md` — as a project inside your existing solution in Build folder. **You are authoring `caseplan.json` here, not running it** — deploying and proving the case is the next block, and keeping them apart is what stops a bad plan being debugged through five deploy cycles.

**The two human gateways are `action` tasks bound to `contracts/review-task.md`** — a Coded Action App registered with that shape and an empty page is enough to wire and prove them. **Create it first, in this block, beside the solution** — a standalone Coded Action App (`create-vite`, `-t Action`; `uipath-coded-apps`), the contract in `action-schema.json`, the page empty — publish it (`uip codedapp publish -t Action`) and deploy it into your seat folder (`uip codedapp deploy --folder-key`), then author the case that binds it by name with that folder as its explicit `folderPath`. Its screens are built at `3f`, after a run has populated the record. Not inside the solution: `CONFIG.md`, *Deploying*, says what that produced.

Everything the case binds must already exist and be published — the six RPA processes, the Data Fabric entity, the seven Agents, the Action App's contract — which is what your task list ordered.

Check it before you go any further:

```bash
python3 3d-case/check_caseplan.py <path-to>/caseplan.json
```

Read that script's comments even if the check passes. Each rule is a shape that packs, deploys and **then** fails on a live claim, and knowing them changes what you build rather than what you debug.

**Done when both gates are green and the plan opens in Studio Web** — `uip maestro case validate` reports `Valid`, `check_caseplan.py` reports no referential problems, `uip solution upload Build/ClaimCase-<seat> --force` has run, and the case plan opens in the Maestro designer inside your solution, where the diagram reads as the process: the decision path left to right, Denied below Approved on the right, Missing details below Intake and Awaiting inspection below Eligibility screening, nothing overlapping (`cookbook.md`, *Canvas*). 
