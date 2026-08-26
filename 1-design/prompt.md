# Design

Read `PDD.md` — a claims manager has described how property claims are handled, and that is the whole brief. Then `CONFIG.md`, *What already exists*, so you bind what is deployed instead of designing a replacement for it.

Use the **`uipath-maestro-case`** skill and design the case from it. **Design only — write `sdd.md` and stop.** Nothing built, nothing deployed.

Three things decide whether the rest of the week is assembly or invention:

- Write it to the four-section shape in `method/template-sdd-case.md`. `method/sdd-guide.md` explains why that one and not the other, and it is worth the five minutes — the wrong shape is not rejected, it is quietly built badly.
- **Take every task's type from the PDD's §5.3 decision-nature column.** Where a step says *rule-expressible*, the work is deterministic; where it says *judgement*, it is not. If the tenant happens to hold something that suggests otherwise, say so and design to the PDD anyway.
- **Deterministic does not mean *a new component*.** Every component you name is a project to build, publish, version, bind and debug, and the case can already do most of it: `execute-connector-activity` writes the claim record and calls connectors directly, the six provided automations cover what exists, and a `=js:` expression with optional chaining reads a nested payload without anything flattening it first. **`contracts/components.md` pins what you build — seven agents and nothing else** — and says what covers the rest. Design the split yourself if you want the exercise, then reconcile against it. How the case is *shaped* is still entirely yours.

Then check your own work and fix what it finds:

```bash
python3 1-design/check_sdd.py sdd.md --pdd PDD.md
```

**Done when a solution architect could hand this to a developer and walk away** — every stage, every task, every rule and every human decision described well enough to build from, with nothing left to guess. The checker exiting 0 is the floor, not the finish.

If a check fires on something you believe is right, say so and leave it — a wrong rule in the checker is worth more to us than a file edited to satisfy it.
