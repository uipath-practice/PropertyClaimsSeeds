# Design

Design the solution for the property claims process with the **`uipath-planner`** skill, and write it to `sdd.md` beside `PDD.md`. Work on your own; everything you would ask me is in the files below.

Read first:
- `PDD.md`: how the claims department handles a property claim today, written by its manager.
- `CONFIG.md`: the environment you build in.
- `contracts/`: what is already deployed and the shapes everything must keep. Use what exists instead of designing a replacement.

Steps:
1. Map the process onto the platform: which steps need judgement and become Agents, which follow a rule, and where a person decides.
2. Write the design. It describes what the solution **is** when it runs; everything built later binds to it.
3. Check it with the design checker and fix what it finds.
4. Stop after the design. The task list is the next block.

Guidelines:
- Let the PDD decide what each step is. It says which steps are judgement and which are rules; what the tenant happens to hold does not.
- Build only the components the contracts list. How you shape the case (stages, order, conditions, SLAs) is your call.
- Describe the claim record (which step writes each column), and write down where the design changes the process, so the PDD's owner sees it.
- If a check fires on something you believe is right, tell me and leave it.

**Done when** a solution architect could hand `sdd.md` to a developer and walk away: every stage, task, rule and human decision described well enough to build from, nothing left to guess. The checker passing is the floor, not the finish.
