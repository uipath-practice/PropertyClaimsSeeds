# Design

Read `PDD.md` — a claims manager has described how property claims are handled, and that is the whole brief. Then `CONFIG.md`, *What already exists*, so you bind what is deployed instead of designing a replacement for it.

Use the **`uipath-maestro-case`** skill and design the case from it. **Design only — write `sdd.md` and stop.** Nothing built, nothing deployed.

Three things I care about:

- **Write it to `method/template-sdd-case.md`.** A design in the wrong shape is not rejected — it is built thinly and passes every check. `method/sdd-guide.md` says why, if you want it.
- **Take every task's type from the PDD's §5.3 decision-nature column**, not from whatever the tenant happens to hold.
- **Build only what `contracts/components.md` lists.** How you shape the case — stages, ordering, conditions, SLAs — is yours.

Then check your own work and fix what it finds:

```bash
python3 1-design/check_sdd.py sdd.md --pdd PDD.md
```

**Done when a solution architect could hand this to a developer and walk away** — every stage, task, rule and human decision described well enough to build from, with nothing left to guess. The checker exiting 0 is the floor, not the finish.

If a check fires on something you believe is right, say so and leave it — a wrong rule in the checker is worth more to us than a file edited to satisfy it.
