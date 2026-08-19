# Block 4 — the analysis agents

**Goal.** Build and publish the seven analyses that read a claim and report what they found.

**Read.** `2-design/` (your own tables — which analysis owns which problem, and what each one is called) ·
`pdd.md` §5 (what each analysis decides) · `4-agents/spec.md` (the set and the answer shape) ·
`contracts/check-envelope.md` (the payload every one returns) · `4-agents/cookbook.md` ·
`7-testing/spec.md` (what a pass looks like — read it before you write prompts, not after)

**Must hold.**

- The two agents that read a source document — the policy, the assessor's report — take it as a **job
  attachment**, not as text. `4-agents/spec.md` says why, and what it costs at test time.
- One analysis per agent. An agent may cite another's finding as evidence, never report it as its own.
- Every agent returns the pinned envelope. No length or item-count limits in any output schema.
- **Each payload has a size budget, and it belongs in the prompt.** The columns that store them cut at 10,000
  characters — silently in the entity, and *loudly* through the connector, which faults the whole case with
  `The provided value for field [<column>] is longer than length limit 10000`. Aim each at 8,000 in the prompt
  text. A `maxLength` in the schema is not the same thing: it is hard validation and it faults the agent.
- **Nothing is flagged that the process did not ask about.** An analysis that finds fault with a clean claim
  passes every check in this block and fails block 5's acceptance run — read `7-testing/spec.md`,
  *What a clean claim proves*, before you write a single check.
- Every declared input is named in the prompt text. An input the prompt does not interpolate does not reach
  the model.
- Each agent reports **every** check it evaluated, passes included — not only the failures.
- Build and test **one** agent end to end before generating the other six. They share a shape, so a mistake in
  the first is a mistake in all seven.

**Done when.**

```bash
uip agent validate <project-dir> --output json   # all seven
uip agent review   <project-dir> --output json   # all seven — grade B or better, zero errors
uip agent debug    <project-dir> --output json   # the five that take no attachment
```

**A grade is a floor, not a pass.** Review scores structure and wording; it has no idea what this pipeline is, so
it cannot see a missing input or a wrong name. Read the schemas yourself: every analysis after the eligibility
gateway declares all three gateway inputs, and every payload name matches `contracts/claim-entity.md`.

Plus, by inspection: a clean claim produces five passing eligibility checks, and a claim with a planted problem
produces a failing check *in the agent that owns it*, worded so a reviewer can see what is actually wrong.

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
