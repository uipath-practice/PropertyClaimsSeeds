# The validation app — what bites

## Where the time goes

**Park your Action Center tasks before you start iterating.** Getting a claim to stop at a gate takes minutes; doing it again for every code change is the difference between a morning and an afternoon. Aim a run at a gate once, leave the task waiting, and rebuild against it.

**Match the loop to what you changed.** A style change does not need a redeploy; a schema change does. Redeploying for everything is most of the time this block costs.

| Issue | Fix |
|---|---|
| A local run looks like it has hung | Give it three seconds. It reliably looks dead just before it works. |
| A PDF will not display | Browser-native embedding is **blocked by the host's sandbox** — `<embed>`, `<object>` and `<iframe>` all fail. Use a JavaScript renderer. |
| The screen cannot read the record | It signs in through the shared registration, which is read-only and already exists. Do not create or edit one — `CONFIG.md`. |
| Tasks raised earlier stop matching the app you are fixing | Publishing the same app name in two folder contexts registers **two identities under one name**. Existing tasks stay pinned to the first while every deploy upgrades the second. Invisible until you compare a task's app id against your own config. |
| You complete a task from the command line and the claim cannot be re-opened | **Anything that writes task data replaces the payload rather than merging into it**, so a decided review loses its identifier unless every writer re-sends it. |
| The solution deploys without the screen | A coded app is not part of the package and does not travel with it. **Put it back into the solution** as an explicit step, or the next deploy silently ships without it. |

## Testing it

**Check the record, not the screen.** The screen can render beautifully from stale state; the record is what the case actually wrote.

**Two runs, not one.** One claim aimed at each gate. The gates differ in what has happened by the time they open — the first has five checks and no assessment, the second has everything — and a screen built for one shows empty panels at the other.

**Open it in a browser, in both states, before calling it done.** Waiting and decided. A build that passes every command and has never been looked at is not finished, and the two flaws found this way on the reference build were both presentational — raw payload tokens as labels, and a completed-task edge case — which no command would have caught.
