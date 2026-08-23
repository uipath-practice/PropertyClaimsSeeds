# Block 2 — getting the design written

The spec is `2-design/spec.md`: what the four tables must contain. This is how to get them written here, and
what the tooling will do to you along the way.

Nothing in this block touches the platform, which makes it the one block where a mistake costs only your own
time. It is also the block whose mistakes are cheapest to fix and most expensive to leave.

## The four tables, and why they are the deliverable

`2-design/spec.md` states what the design has to answer. In practice it lands as **four tables plus prose**, and
naming them here saves you inventing a structure:

| Table | One row per | Columns that earn their place |
|---|---|---|
| **Stages** | stage | how a claim enters · what ends it · primary or secondary |
| **Work** | task | which stage · what kind of component · what it needs · what it produces |
| **Data** | payload | produced by · case variable name · entity column · read by |
| **Traceability** | planted problem | which check owns it · what it reports · where a human sees it |

The **Data** table is the one that pays for the block. Names have to match across three surfaces — agent output,
case variable, entity column — in three casings (`contracts/claim-entity.md`, *One name, three casings*), and a
name improved in one place breaks silently in another two blocks later.

The prose around them is the SDD, and it is a real deliverable: it is what explains the solution to a person who
was not here. Nothing downstream parses it.

## The `uipath-planner` skill, and what to keep from it

**Use it.** It is the UiPath skill for exactly this step, it reads a PDD and writes an SDD, and it asks the
questions a design should answer — exceptions, escalations, what happens when a document never arrives — that
are easy to skip when you are writing to a template of your own.

Two of its own opening steps are already answered by this seed, so a correct run should ask you nothing:
its execution-mode question is answered by `AGENTS.md`'s standing approval (autonomous), and its delivery-model
question by `CONFIG.md` (cloud). It also wants to create progress tasks through harness tools that may not exist
where you are running; its own rules cover that gracefully, so a skipped step there is expected.

Three things to know before it runs, because they change what you get:

- **Its template is a hard superset contract.** It will produce every section the template names — RACI matrix,
  SLA rules, DEV/UAT/PROD environments, compliance constraints — whether or not this exercise has any. Let it.
  Then judge the result by *our* gate, not by its section count: **the four tables and the three questions are
  what block 3, 4, 5 and 7 read**, and a design that has all seventeen sections and a thin Table 3 has failed
  the part that matters. Do not pad a section to satisfy a heading, and do not delete our tables to satisfy one.
- **It marks gaps `[SME REVIEW]` and expects a human to resolve them.** There is no SME here. Resolve what
  `pdd.md` answers, and for anything it genuinely leaves open — a production SLA, a payment interface — say so
  in one line and move on. An unresolved marker is an honest design; a rule invented to clear one is not.

If your agent does not load the skill, you are not at a disadvantage: everything required is in this document.
**Say which route you took** when you log this block, because that is a comparison worth having.

## Write it to disk as you go, not at the end

The whole point of this block is that the design outlives your context. An agent that holds four tables in its
head and writes them in one pass at the end loses them to the first compaction — and blocks 4 and 5 are long
enough that a compaction is close to certain.

Write `2-design/sdd.md` incrementally: the stage table, then the work table, then the data table, then
traceability. Each one is useful to the next block on its own.

## Read the arguments; do not recall them

Three of the four tables end up naming things that must match at run time. The authorities, in order:

| For | Ask |
|---|---|
| what a provided process takes and returns | `uip or packages entry-points "<PackageId>:<Version>"` |
| entity columns and their types | `contracts/claim-entity.md` |
| the check ids | `pdd.md` §9 — the check name in snake_case |
| the analysis payload shape | `contracts/check-envelope.md` |
| the shape of a structured record | `contracts/record-payloads.md` |
| **which case-plan shapes fail at run time, and how** | **`5-case/check_caseplan.py` — read its comments now** |

That last row is not filed under block 5 by accident, and it is worth the ten minutes here. The script's
comments are the most concrete source in the seed about which plan shapes fail and what they look like when they
do — each rule carries the error code and the build it was added for. Three of them have already changed a
design *before* anything was built, which is what block 2 is for; meeting them in block 5 means meeting them
after the plan is authored.

A name recalled from a plausible convention is the single most common defect this block produces, and it does
not fail here — it fails in block 5, where bindings resolve by name at run time and a wrong one packs, deploys
and runs before it breaks.

## Gaps are findings, not blockers

`pdd.md` describes a business process, not a complete system, and it leaves real things open — a production SLA,
what happens after a settlement is authorised. When you hit one:

- If `pdd.md` answers it somewhere else, use that answer.
- If it genuinely does not, **say so in one line in the SDD and log it**
  (`python3 log-finding.py --block 2-design --category seed-gap --summary "..."`). A design that names its gaps
  is finished; one that invents a business rule to fill a gap is worse than one that stops.

The gaps you find here are the most useful thing this block produces for the people maintaining the exercise —
they are what the next version of `pdd.md` fixes.
