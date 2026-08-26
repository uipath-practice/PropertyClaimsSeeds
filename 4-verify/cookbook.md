# Verify — what bites

| Issue | Fix |
|---|---|
| Runs come back random and nothing is reproducible | Aim them. The claim generator takes a scenario and an exact problem id — `contracts/provided-processes.md`, *Retrieve Property Claim*. Leave them empty only for the clean runs. |
| You cannot tell which run is which | Identify a case by its instance, not by scanning the job list. The job list shows every seat's work; the instance is yours. |
| A claim seems stuck | Poll the instance rather than guessing a duration. The inspection wait is an independent draw per call, so wall-clock time tells you about your poll interval and nothing else. |
| A claim faulted and the error names something you never wrote | Read the incident detail **from the end** — it runs to tens of thousands of characters and the cause is at the bottom. A node id that appears nowhere in your design usually means a condition was evaluated at case start. |
| The answer key is not where you expect | It is named after the claim, not `manifest.json`, and lives beside the claim form. |
| A gateway will not open for testing | Aim the run at it. A clean claim skips both gates by design, so the reviewer's screen you are trying to test never appears. |
| You complete a task from the command line and the case does not move on | Hand back every identifier the task was given — anything writing task data replaces the payload rather than merging. `3e-validation/cookbook.md` has the shape. |
| A fix works and you cannot tell whether it broke something else | Re-run the clean claim after every fix. It is the cheapest regression you have, and over-flagging is the failure that reappears. |

## Two runs are not the same as two claims

**A pinned run proves detection. A clean run proves restraint.** Solutions are good at the first and bad at the second, so budget the clean runs first rather than last — they are the ones that send you back into the agents.

## Keep the log as you go

What you aimed at, what happened, what you changed. It is the results table this block owes, and reconstructing it afterwards from memory produces something nobody can act on.
