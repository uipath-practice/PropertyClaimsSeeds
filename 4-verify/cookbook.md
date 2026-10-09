# Verify — what bites

| Issue | Fix |
|---|---|
| An aimed run's answer key says nothing was planted | `auto-settle` silently drops a valid problem id, and an empty or unknown scenario draws a random claim. Pair the id with its scenario — `eligibility-fail` for `ELIG_*`, `review-fail` for `REVIEW_*`; a clean run is `auto-settle` with an empty id. Read the key's `AppliedDiscrepancies` before counting the run. |
| You have revised a prompt twice and the number has not moved | **A prompt governs what an agent reports, not what it concludes.** Where the conclusion decides whether a claim reaches a human, put it in a case condition and stop revising. |
| Closing a false escalation made a missed problem worse | The two failures mask each other: a claim escalated for the wrong reason still reached a human, and closing that reason sends the missed problem straight through. Measure detection and restraint on the **same** batch, never one at a time. |
| A signal you downgraded in the case keeps escalating | The decision layer re-derives it from every place it is still visible — the scalar, the envelope's conclusion, the failing check left in `checks[]`. Rebuild what the decision layer is handed; leave the agent's own verdict untouched on the record and on the screen. |
| An Agent fix passes in `agent debug` and the case still gets the old answer | You tested it on inputs you built by hand. Fetch what the case sent — `python3 4-verify/agent_inputs.py --deploy-folder-key <deploy folder> --agent <Agent> --instance <instance> --out in.json` — and debug on that. If the wording changes but the verdict does not, reorder the output: the field that constrains the verdict goes before it (`3c-agents/cookbook.md`, key order). |

## Make each of the three cycles count

- **Fix everything one batch shows before you redeploy** — one redeploy per batch, never one per failure.
- **Prove an Agent fix before you spend a batch on it:** `uip agent debug` on the failing claim's recorded inputs takes minutes; a batch takes a quarter of an hour.
- **Regenerate each failing claim from the seed its answer key records** for the before-and-after, and give the rest of the batch fresh seeds, or you are tuning to the claims you have already seen.
- **Two prompt revisions that did not move a result are the signal to move the conclusion into the case** — the table above.

## Two runs are not the same as two claims

**The same claim cannot run twice**: the case mints its claim reference per instance and ignores a caller-supplied id. So the reproducibility test is two clean runs of one `profileId`; add the same `seed` and the documents are identical too, and a figure that still differs is the Agent's. Compare every figure, never the prose — the wording varies while the numbers hold. The pair also catches what no aimed run can: a settlement that differs between two identical claims has broken its own arithmetic.

## A failure no injector plants is a false positive by construction

The injectors are a short list — an unknown `in_Discrepancy` faults and names them all (`contracts/provided-processes.md`). A check that fires on something nothing plants is your agent inventing a problem, and it costs a human review on every clean claim.
