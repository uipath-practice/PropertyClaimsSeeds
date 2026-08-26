# Deploying the case and running it — what bites

**The plan passed both gates and neither of them ran anything.** Everything here is a failure that only exists once something executes.

## The package is missing the only file that runs

`3d-case/cookbook.md`, *The edit does not take effect*, tells you which command compiles `caseplan.json.bpmn`. This is what happens if you skip it: **`uip solution pack` omits the compiled file from the package** — silently, and even though `package-descriptor.json` lists it. Nothing fails at pack time. The job faults at run time with *"entry point could not be resolved to a BPMN file"*.

**Case-pack first, then solution-pack, then check the compiled file is actually inside the package** before you deploy.

## Deploying

| Issue | Fix |
|---|---|
| A redeploy creates a second deployment | Same name, every time — `CONFIG.md`, *Deploying*. |
| `Validation failed` on a deploy that never got that far | It is a **failed uninstall** reported as a validation error. Clear the half-failed deployment first. |
| A bound automation is not found, five seconds in, having executed nothing | The folder. `contracts/provided-processes.md`, last section. |

## When a claim does not do what you expected

Read the instance, not the job list. The variable table at run time is what the case actually had; the incident detail is long and **the cause is at the end**, not the start.

## Bindings that survive both gates and still misbehave at run time

| Issue | Fix |
|---|---|
| A component receives the literal name of an output instead of its value | A bare output name is a **string**, not a reference. Every task goes green and every field downstream is blank. |
| A polling loop overwrites a good result with a later empty one | A stage that re-enters re-runs its calls. **Guard the write**, or a ready result is replaced by the next not-ready one. |
| A routing guard sends a claim down the wrong lane | The value it tests may not be written yet at the moment the gate evaluates. `'' !== 'Deny'` is true, and a denied claim goes down the approved path with a letter that says otherwise. **Test for the outcome you want, not against the one you don't.** |
| A resources refresh reports `Created 0, Imported 0, Skipped 0` | The counter is unreliable in both directions. **The resources tree on disk is the truth** — check it wrote files rather than believing the number. |
