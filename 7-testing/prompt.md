# Block 7 — testing

**Goal.** Prove the solution catches what it is supposed to catch, in the right place, for the right reason —
and lets a clean claim through untouched.

**Read.** `7-testing/spec.md` (what to test and what a pass is) · `7-testing/cookbook.md` (the commands) ·
`pdd.md` §9 (the nine planted problems) · your own traceability table from `2-design/`

**Skill.** `uipath-platform` to start runs and read state; `uipath-troubleshoot` when one fails and you need
to know why. Not `uipath-test` — that drives Test Manager, which this exercise does not use.

**Must hold.**

- **Aim every run.** Pin the scenario and the discrepancy. An unpinned run that goes green proves one claim
  passed, not that a check works.
- **Assert against the manifest**, not against what looks reasonable. The generator writes down what it planted
  and what must happen; that is the answer key, and this is the only block allowed to read it.
- **The right analysis has to be the one that catches it.** A claim stopped for the wrong reason is a fail, and
  it reads as a pass everywhere except the wording.
- **At least two clean runs.** A solution that flags every claim has not passed.
- Keep the failures. A results table with only successes cannot show whether the solution got better.

**Done when.** A results table with a row per run: what was aimed at, where the claim stopped, which analysis
caught it, what the claimant was told, and pass or fail. Nine pinned runs, two clean runs, then twenty on
`random`.

**Where it goes.** The results table in this block's folder. Generated code, as ever, in `Build/ClaimCase-<NN>/`.

**Log as you go.** `python3 log-finding.py --block 7-testing --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
