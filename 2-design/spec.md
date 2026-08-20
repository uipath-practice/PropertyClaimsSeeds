# The design — what must be true

This block produces **four tables and a document**. The document is for a person; the tables are what blocks 3,
4, 5 and 7 are built from. Both are deliverables, and only the tables are load-bearing.

Nothing here is generated for you. `pdd.md` describes the process in business language on purpose — turning it
into stages, task groups and a data map *is* the design, and it is the part a coding agent is genuinely good at
if you make it write the result down rather than hold it in its head.

**The tables are yours to re-read, not a hand-off to a tool.** No skill parses them. Block 5 still points the
case tooling at `pdd.md` directly; what the tables change is how much you have to reconstruct each time you come
back to the work.

## Table 1 — stages

| Stage | Primary or secondary | A claim enters when | The stage ends when | Ends the case |
|---|---|---|---|---|

- **Primary is the path a healthy claim takes.** Everything a claim reaches only because something went wrong —
  a denial, a wait for something missing — is secondary. `pdd.md` §3 has the criterion.
- **Every ending is a row.** A claim that is denied ends somewhere; so does one that settles.
- **A waiting stage is a stage.** If the process waits for something that arrives on its own schedule, that wait
  has entry and exit conditions like anything else, and it is where a poll lives.
- **No row without a way in**, except the one `pdd.md` §3 asks you to leave unwired. A stage you cannot describe
  an entry for is a stage you have not designed; mark the deliberate placeholder as deliberate, so block 5 can
  tell it from an omission.

## Table 2 — work

| Stage | Task | What runs it | Needs | Produces | Runs in parallel with |
|---|---|---|---|---|---|

"What runs it" is one of: a **provided process** (`contracts/provided-processes.md` — six of them, already
deployed), one of your **analysis agents**, a **write to the claim record**, or a **human**.

Two things this table is for:

- **It is where you notice you were about to build something that exists.** If a row says "download the policy
  PDF from the bucket", one of the six already does it.
- **Order falls out of "Needs".** The policy number comes out of extraction, so nothing that needs the policy
  can run before the claim form has been read. Most of the lifecycle's shape is that one fact and a few like it.

## Table 3 — data

| Payload | Produced by | Case variable | Entity column | Read by |
|---|---|---|---|---|

**This is the table that makes block 5 cheap.** A case plan is mostly bindings, bindings resolve by name at run
time, and a name that is wrong packs, deploys and runs — then fails on a live claim with an error naming
neither the binding nor the name.

- **One name, three casings** (`contracts/claim-entity.md`): agent output `out_EligibilityChecksJSON`, case
  variable `eligibilityChecksJson`, entity column `eligibilityChecksJson`. Do not improve any of the three.
- **A payload with no column still has a name, and it is not yours to choose.** Some payloads are carried
  between tasks and never stored — the raw extraction, the claims history. `claim-entity.md` cannot name those
  because they have no column, so take the name from the argument that produces it:
  `out_PreviousClaimsJSON` → `previousClaimsJson`. Read the argument rather than recalling it,
  `uip or packages entry-points "<PackageId>:<Version>"`. A plausible synonym like `priorClaimsJson` costs
  nothing here and everything in block 5, where bindings resolve by name at run time.
- **Every column in `contracts/claim-entity.md` appears here with something that writes it.** A column nothing
  writes is either a design gap or a column that should not exist; both are worth knowing before block 3.
- **Note the big ones.** Any payload that could run long has a size budget to respect
  (`contracts/claim-entity.md`); this table is where you decide which ones those are, and block 4 is where the
  budget goes into a prompt.

## Table 4 — traceability

| Planted problem | Caught by | Field carrying the finding | Stage where it shows |
|---|---|---|---|

`pdd.md` §9 lists nine. Each gets **exactly one** owner — an analysis that must catch it. Two owners means
neither is accountable and a claim gets flagged twice; no owner means a claim passes with a real problem in it,
and nothing in the build will tell you.

This is also the block's honesty check. **If you cannot fill this table from your own design, you have not
understood the process yet**, whatever the SDD says. It is used again unchanged in block 7 as the test plan.

## The SDD

A document a person reads to understand what you built: the architecture, the components and what each is for,
the lifecycle, where the humans stand, and how the pieces are wired. The four tables belong in it.

It is a real deliverable — the documentation outcome of this exercise — and it is graded by whether someone who
was not here could pick up your solution from it. It is **not** input to any tool.

## Done when

The three questions in `2-design/prompt.md` can be answered from the tables alone, without re-reading `pdd.md`.
