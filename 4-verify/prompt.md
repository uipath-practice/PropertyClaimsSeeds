# Verify

Every piece was checked as you built it. This block asks the only question none of those could: **does the whole thing behave?**

`PDD.md` §13.2 lists the problems a real claim arrives with, and §1.3 says what success means numerically. Aim a run at each problem in turn, then run clean claims, and record what happened against both.

**Now you may read the answer key.** It sits beside the documents in the `Claims` bucket and states what was planted and what should happen — the oracle you have been forbidden until this point. `contracts/provided-processes.md` names it.

Three things to establish, and they are not equally easy:

- **Each planted problem is caught by the component that owns it, and stops the claim at the right decision point.** Not caught by something else, and not caught twice — a reviewer seeing one problem reported by three components reads three problems.
- **A clean claim settles in full with no task ever raised** (`PDD.md` §1.3 SC1). This is the one most solutions fail, and it fails quietly: everything looks careful and nothing can ever settle by itself.
- **What the claimant is told matches what actually happened.**

Then check the build against the design rather than against the process: enumerate every stage, task, rule, SLA and variable in `sdd.md` and mark each **Implemented · Missing · Mismatch · Extra**. *Extra* is the one worth looking hardest at — it is what nobody asked for, no tool reports, and every reviewer pays for later.

**Expect to spend most of this block fixing rather than measuring.** A run that finds nothing has usually not proven the solution works; it has proven the run was not aimed. Fix at the source, in the block that owns it, and re-run.

**Done when** you can say, per problem, which component caught it and where a human saw it — and when a claim with nothing wrong has gone in and come out settled, untouched.
