# Build — the Maestro Case

Use the **`uipath-maestro-case`** skill and build the case from `sdd.md` — as a project inside your existing solution in Build folder. **Authoring `caseplan.json` here, do not run it** — deploying and testing the case is the next block. Diagram reads as the process: the decision path left to right, Denied below Approved on the right, Missing details below Intake and Awaiting inspection below Eligibility screening, nothing overlapping (`cookbook.md`, *Canvas*). 

Register the Coded Action App first, with the shape of **`contracts/review-task.md`** — the two human gateways are `action` tasks bound to it, and an empty page is enough to wire and prove them. Use `uipath-coded-apps`: scaffold it **standalone, beside the solution** (`create-vite`, `-t Action`), put the contract in `action-schema.json`, `uip codedapp publish -t Action`, `uip codedapp deploy --folder-key <your seat folder>`. Then author the case that binds it by name with that folder as its explicit `folderPath`. Its screens are built at `3f`, after a run has populated the record.

Everything the case binds must already exist and be published — the six RPA processes, the Data Fabric entity, the seven Agents, the Action App's contract — which is what your task list ordered.

Check it before you go any further:

```bash
python3 3d-case/check_caseplan.py <path-to>/caseplan.json
```

Read the checker's rules even if it passes — each is a shape that packs, deploys and then fails on a live claim.

**Done when:**
- both gates are green: `uip maestro case validate` reports `Valid`, `check_caseplan.py` reports no referential problems
- the plan opens in Studio Web: `uip solution upload Build/ClaimCase-<seat> --force` has run.
