# Build — the Maestro Case

Use the **`uipath-maestro-case`** skill and build the case from `sdd.md` — as a project inside your existing solution in Build folder. **Authoring `caseplan.case` here, do not run it** — deploying and testing the case is the next block.

Generate the plan, do not write it: from inside the solution folder, `uip maestro case init` the project; `uip maestro case sdd resolve sdd.md --out tasks/registry-resolved.json`; `uip maestro case sdd convert sdd.md --resolved tasks/registry-resolved.json --out <project>/caseplan.case`. What convert lists under `Data.Unresolved[]` is the work left — close each entry the way the skill says, and nothing else by hand. Convert writes a few shapes that run wrong on this case; `cookbook.md` names them and `check_caseplan.py` flags them, so fix those in `caseplan.case`. Anything else convert gets wrong, log it; fix `sdd.md` and convert again only before any splice or hand edit — every one after it is redone. Diagram reads as the process: the decision path left to right, Denied below Approved on the right, Missing details below Intake and Awaiting inspection below Eligibility screening, nothing overlapping (`cookbook.md`, *Canvas*). 

The app and the case are two separate builds — if your agent can delegate to a subagent, build and register the app there and keep this context for the case; either way, write the app's name, deployment id and folder into `PROGRESS.md` before starting the case.

Register the Coded Action App first, with the shape of **`contracts/review-task.md`** — the two human gateways are `action` tasks bound to it, and an empty page is enough to wire and prove them. Use `uipath-coded-apps`: scaffold it **standalone, beside the solution** (`create-vite`, the React + TypeScript template — `-t Action` belongs to `publish`, not to the scaffold), put the contract in `action-schema.json`, `uip codedapp publish -t Action`, `uip codedapp deploy --folder-key <your seat folder>`. Then author the case that binds it by name with that folder as its explicit `folderPath`. Its screens are built at `3f`, after a run has populated the record.

Everything the case binds must already exist and be published — the six RPA processes, the Data Fabric entity, the seven Agents, the Action App's contract — which is what your task list ordered. The case skill keeps its own `tasks/` folder beside the plan (`registry-resolved.json`, its resolution ledger); that is not your `tasks.md`, and neither replaces the other.

Check it before you go any further:

```bash
python3 3d-case/check_caseplan.py <path-to>/caseplan.case
```

Run the script as it ships — reimplementing its rules in another language is not the gate. Read the checker's rules even if it passes — each is a shape that packs, deploys and then fails on a live claim.

**Done when:**
- `uip maestro case validate <path-to>/caseplan.case --strict --sdd sdd.md` reports `Valid` — the **full** validator, not `--skeleton-v2`; every error it prints is a runtime failure waiting, not validator strictness
- every entry convert listed under `Data.Unresolved[]` is closed
- `python3 3d-case/check_caseplan.py` reports no referential problems — it checks what the validator cannot: layout, argument-named outputs, connector inputs, skips on human gates
- the plan opens in Studio Web: `uip solution upload Build/ClaimCase-<seat>` has run.
