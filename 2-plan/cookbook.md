# Plan

## How it is built here

- `tasks.md` at the seed's root. The Coded Action App is a stand-alone task (beside the solution, deployed to the seat folder), ordered before the case.
- The case is one task: *build the case from `sdd.md`: resolve, convert, close what convert leaves unresolved*.
- A `Validate:` step on every task that generates something, and a testing task before anything deploys.
- **`Status:` lines**: each later block sets the `Status:` line of every task it finishes, not only the sub-items. Hand-over (`5-ship`) closes every task before it; the process app's tasks come after it and stay open there.

## What bites

| Issue | Fix |
|---|---|
| The skill wants live `TaskCreate` / `TaskUpdate` / `TaskList` calls and your runtime has none | Expected (the planner says so): **`tasks.md` is the artifact**; keep its `Status:` lines current by editing the file. |
| The planner's task format rejects `uipath-troubleshoot` or `uipath-planner` as a task's skill | Its closed list has neither. Follow `AGENTS.md`'s block table — Verify to `uipath-platform` and `uipath-troubleshoot`, Hand over to `uipath-solution` and `uipath-planner` — and log the disagreement. |
