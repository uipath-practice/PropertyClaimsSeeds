# Verify — what bites

| Issue | Fix |
|---|---|
| Runs come back random and nothing is reproducible | Aim them. The claim generator takes a scenario and an exact problem id — `contracts/provided-processes.md`, *Retrieve Property Claim*. Leave them empty only for the clean runs. |
| You cannot tell which run is which | Identify a case by its instance, not by scanning the job list. The job list shows every seat's work; the instance is yours. |
| A claim seems stuck | Poll the instance rather than guessing a duration. The inspection wait is an independent draw per call, so wall-clock time tells you about your poll interval and nothing else. |
| A claim faulted and the error names something you never wrote | Read the incident detail **from the end** — it runs to tens of thousands of characters and the cause is at the bottom. A node id that appears nowhere in your design usually means a condition was evaluated at case start. |
| The answer key is not where you expect | It is named after the claim, not `manifest.json`, and lives beside the claim form. |
| A gateway will not open for testing | Aim the run at it. A clean claim skips both gates by design, so the reviewer's screen you are trying to test never appears. |
| You complete a task from the command line and the case does not move on | Hand back every identifier the task was given — anything writing task data replaces the payload rather than merging. `3f-validation/cookbook.md` has the shape. |
| A fix works and you cannot tell whether it broke something else | Re-run the clean claims after every fix. It is the cheapest regression you have, and over-flagging is the failure that reappears. |
| `uip tasks complete` refuses a task an Action App owns | On this line it needs `--type AppTask`; no `--help` says so. |
| You are on your fourth prompt revision and the number has not moved | **A prompt governs what an agent reports, not what it concludes.** Where the conclusion decides whether a claim reaches a human, put the conclusion in a case condition. Measured 2026-08-27: four revisions on an over-flagging check moved nothing and one condition in the case closed it; six revisions on an under-detecting check moved nothing either. Same lever, same result, three times — stop. |
| Closing a false escalation made a missed problem worse | The two failures mask each other: a claim escalated for the wrong reason still reached a human; close the wrong reason and the missed problem goes straight through. Measure detection and restraint on the **same** batch, never one at a time. |
| A signal you downgraded in the case keeps escalating | Every place it is still visible to the decision layer is a place it re-derives the escalation from — the scalar, the envelope's conclusion, the failing check left in `checks[]`. Rebuild what the decision layer is handed; leave the agent's own verdict untouched on the record and on the screen. Three iterations, measured. |
| A fix you deployed does not show on the claims you are reading | A running instance keeps the plan it started under; agent packages resolve by name at call time. Six claims started one version earlier were running the previous plan — start the batch after the deploy. |
| You need the list of problems the generator can plant | An unknown `in_Discrepancy` **faults, and the fault lists the valid ids** — one deliberately wrong job enumerates them; an unknown `in_Scenario` silently draws a random claim. |

## Two runs are not the same as two claims

**A pinned run proves detection. A clean run proves restraint.** Solutions are good at the first and bad at the second, so budget the clean runs first rather than last — they are the ones that send you back into the agents.

## Keep the log as you go

What you aimed at, what happened, what you changed. It is the results table this block owes, and reconstructing it afterwards from memory produces something nobody can act on.
