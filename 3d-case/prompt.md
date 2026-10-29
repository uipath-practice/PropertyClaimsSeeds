# The Maestro case

Build the case from `sdd.md` with the **`uipath-maestro-case`** skill, as a project inside your solution. **Author and validate it here; don't run it.** Deploying and testing is the next block.

Steps:
1. **Register the review app first.** The two human gates are Action Center tasks bound to a Coded Action App, so it has to exist before the case: an empty page with the shape of `contracts/review-task.md`, built beside the solution and deployed on its own to your seat folder. Its screens come later. If you can hand work to a subagent, give it this, and write the app's name, id and folder into `PROGRESS.md` before you start the case.
2. **Generate the plan from `sdd.md`; don't write it by hand.** Then close only what the generator leaves for you.
3. Fix the shapes the generator is known to get wrong on this case, and run the case checker.
4. **Lay the diagram out so it reads as the process**: the decision path left to right, each side lane next to the stage it leaves from, nothing overlapping.
5. Validate the plan strictly against `sdd.md`, upload the solution, and give me the Studio Web link so I can look at the diagram.

Guidelines:
- Everything the case binds must already exist and be published. That is what your task list ordered.
- If the generator gets something else wrong, log it. Fix `sdd.md` and regenerate only before any hand edit; after one, every regeneration has to be redone by hand.
- Every error the validator prints is a runtime failure waiting to happen, not strictness.

**Done when:**
- the strict validator reports the plan valid against `sdd.md`
- nothing the generator left open is still open
- the case checker reports no problems
- the plan opens in Studio Web and I have the link.
