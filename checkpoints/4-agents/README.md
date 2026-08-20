# Checkpoint — the seven analyses

Seven working agent projects. Copy them into `Build/ClaimCase-<NN>/`, **one folder each at the top level**, and
register them with `uip solution projects add`. Do not nest them under an `agents/` folder: `uip agent debug`
only searches one level up and will tell you the solution does not exist (`4-agents/cookbook.md`).

Then, before anything else:

```bash
uip agent refresh  <name>     # regenerates entry-points.json against agent.json
uip agent validate <name>     # Success
uip agent review   <name>     # PASS, grade A or better
```

## What using this costs you

**The whole of block 4** — the prompt writing is the block. Take it when the analyses have stopped being the
interesting part of your day, not before.

**You still have to read `4-agents/spec.md`.** Block 5 binds every one of these by input and output name, and
debugging a binding in an agent you have never opened is the most expensive hour in this exercise.

## What it is, and what is unverified

Repaired 2026-08-20 after a build reported it contradicted the contracts it was supposed to rescue. Four things
were wrong and are now fixed: the pinned model, the gateway notes input (`in_EligibilityReviewerNotes` →
`in_EligibilityNotes`), a missing `projectId` that made every project fail `uip agent validate` outright, and an
`entry-points.json` two inputs behind its own `agent.json`. Two agents also declared `in_PreviousClaimsJSON`
without interpolating it, which is the silent failure `4-agents/spec.md` warns about — a prior-claims history
would have arrived and been reported missing.

All seven now validate and review clean. **They have not been run end to end through a case since the repair**,
so if one misbehaves on a live claim, that is worth logging rather than working around.

The decision analysis emits `out_FinalDecision` and `out_ReviewRequired` alongside its envelope. That matches the
reference build; `contracts/claim-entity.md` has the case compute `reviewRequired` from the recommendation, so
treat the agent's value as the recommendation and the case as the authority.
