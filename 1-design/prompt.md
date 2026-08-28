# Design

Read:
- `PDD.md` — property claims department manager has described how property claims are handled. 
- `CONFIG.md` - describes environment and settings.
- `contracts/` - some technical specs and description of automation blocks that already exist (use what is deployed instead of designing a replacement for it).

Use the **`uipath-planner`** skill and design the solution from the PDD. Run **autonomous** — do not pause for confirmation. **Design only: write the design to `sdd.md` at this folder's root and stop** — with `Tasks file: tasks.md` in its handoff header, which is where `2-plan` writes. No task list, nothing built, nothing deployed — `2-plan` derives the tasks next.

`sdd.md` describes what the solution **is** when it runs. It outlives the build and everything downstream binds to it.

Three things I care about:

- **Take every task's type from the PDD's §5.3 decision-nature column**, not from whatever the tenant happens to hold — and name the step in each task's *Design Rationale* (`PDD step 4.3`), which is how the checker verifies it.
- **Build only what `contracts/components.md` lists** — seven agents and one Action app, no tools, no evaluation sets. How you shape the case — stages, ordering, conditions, SLAs — is yours.
- **Add the two sections in `method/sdd-addendum.md`** after Section 4, headings as written: the claim entity with its write-ownership matrix, and what the design fed back to the PDD.

Then check your own work and fix what it finds:

```bash
python3 1-design/check_sdd.py sdd.md --pdd PDD.md
```

The planner's own audit checks the document's shape; this one checks the design against the process — task types against the PDD, one writer per column, every read variable produced, tables that actually render.

**Done when a solution architect could hand this to a developer and walk away** — every stage, task, rule and human decision described well enough to build from, with nothing left to guess. The checker exiting 0 is the floor, not the finish.

If a check fires on something you believe is right, say so and leave it — a wrong rule in the checker is worth more to us than a file edited to satisfy it.
