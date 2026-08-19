# How to work in this folder

This is the seed for the Property Claims exercise. It describes **what to build**; you write everything that
does the building. Read this file first, then `GUIDE.md` for the sequence and the gates.

## What is being built

A property insurance claim arrives as three documents that do not always agree with each other: the claimant's
**claim form**, their **insurance policy**, and an **assessor's report** on the damage. Only the claim form is a
structured form; the other two are free prose and reach the analyses **as files**, to be read rather than
extracted (`pdd.md` §1). The solution reads them,
works out whether the claim is payable and for how much, puts a human in front of the two decisions that need
one, and writes to the claimant.

```
three PDFs ──▶ extraction ──▶ seven analyses ──▶ two human gateways ──▶ one record ──▶ an app, and a letter
   (given)      (block 1)       (block 4)          (block 5)           (block 3)      (block 6)
```

The claim moves through five stages, and every stage writes what it learned to a single Data Fabric row:

| Stage | What happens |
|---|---|
| **Intake** | the documents are fetched, the row is created, extraction runs, the policy and any prior claims are retrieved |
| **Eligibility analysis** | one analysis decides whether the claim should be investigated at all — then a **human screens it** |
| **Data analysis** | the assessor's report is validated and structured, then coverage, payout and credibility run **in parallel**, then a decision analysis reads all four |
| **Claim review** | a **human adjuster decides** — unless nothing was flagged, in which case this stage is skipped entirely |
| **Settlement and closure** | the letter is written, the row is closed |

## Four ideas that decide whether your build is right

Everything in this seed follows from these. If a design choice seems arbitrary, it is probably one of these
four showing through.

**1. Analyses report; humans decide.** No agent may refuse a claim. They produce *findings* and a
*recommendation*; the two human gateways turn that into an outcome. Approval is the one direction allowed to run
unattended — a claim with nothing wrong settles without an adjuster, but it still passes the screening gateway.

**2. One analysis per agent, and no agent reports another's concern.** A reviewer sees the findings side by
side, so the same problem raised by three analyses reads as three problems. An agent may *cite* another's finding
as evidence; it may never re-raise it as its own.

**3. A finding must be visible to the analysis that reports it.** Before writing any check, ask whether the data
reaches that agent, at that stage — not whether it is on the document. An agent asked to confirm something absent
from its own input can only report it missing, confidently and wrongly.

**4. Nothing a human sees exists unless a stage wrote it down.** The case instance holds lifecycle, not content.
Every payload, decision and reason lands in a column on the claim record, and the app reads from there. A payload
with no column is data that vanishes; a column with no producer is a panel that stays blank forever.

## What already exists, and what you build

**Given to you:** six deployed processes — one that generates the three documents, and five that move data and
files between storage and your case (extraction, policy, prior claims, assessor report, notification) — plus the
buckets, and a shared extraction project you may adopt instead of training your own. `contracts/provided-processes.md` gives every one
with its exact arguments, types and behaviour.

**They are the integration layer, and they are given on purpose.** In a real insurer, fetching a policy means
driving a portal — log in, search, download, return the file. Here it is a storage bucket behind the same
interface. What that leaves you is the part worth practising: stitching the pieces into a case, putting a human
in the right two places, and making it survive a long-running execution.

So if you find yourself about to build a bucket download, an IXP invocation or a PDF-to-text step, stop and
check `contracts/provided-processes.md` — it exists.

**Yours:** the extraction taxonomy or the adoption of the shared one, the claim record, the seven agent prompts
and their schemas, the case plan and every binding in it, and the app. **All of it in one solution**, named for
your seat — a case can only bind agents that live in its own solution.

## The layout

One folder per block, numbered in build order. Inside each, the same three names:

| File | What it is |
|---|---|
| `prompt.md` | the instruction for this block — start here |
| `spec.md` | what must be true when the block is done |
| `cookbook.md` | how to get it done on this platform: commands, traps, things that cost someone an hour |

Shared at the root: `pdd.md` (the process in business language — the *why* behind every rule here), `CONFIG.md`
(names, models, folders, versions), `contracts/` (shapes more than one block must agree on), `known-issues/`
(what is known-broken upstream, so you do not debug it).

**Paths in this seed are relative to this folder**, always — `contracts/claim-entity.md`, not `../contracts/`
and not `seed/contracts/`. A block that cites a path outside itself is telling you the knowledge is shared.

## Where your own work goes

Three places, and nothing anywhere else:

| What you produce | Where it goes |
|---|---|
| **All generated code** — agents, the case, the app | `Build/ClaimCase<NN>/` — **one solution**, named for your seat |
| **Notes and documents you write for a block** — a design, a decision about structure, an SDD | that block's folder, e.g. `2-design/sdd.md`, `5-case/notes.md` |
| **Findings** | the shared table, via `log-finding.py` — never a local file |

**One solution, and its name is fixed.** `Build/ClaimCase<NN>/` holds everything: a case binds agents by name
*inside its own solution*, so agents published in a solution of their own are unreachable from the case that
needs them. Do not create a second solution for a component, and do not invent a name — every extra solution is
another package to version, deploy and uninstall in step, and a name nobody chose is a name nobody can find.

**Seed filenames are fixed**, so nothing you write can collide: a block folder ships exactly `prompt.md`,
`spec.md` and `cookbook.md` (block 1 has two prompts, and some blocks carry a `taxonomy` or a script). **Any
other file in a block folder is yours.** Put your notes where the prompt that prompted them lives — that is
where the next person will look for them.

Do not scatter working folders across the seed, and do not build outside `Build/`. A reviewer should be able to
run `ls Build/` and see your entire solution, once.

## Rules that hold everywhere

**Names come from the contracts. Do not invent them, and do not improve them.** Agent outputs, case variables
and entity columns are one name in three casings, by design (`contracts/claim-entity.md`). A better name breaks
the mapping three blocks later, at run time, silently.

**Everything you create carries your seat token.** The tenant is shared — with this workshop and with other
exercises; `CONFIG.md` says what has to carry the token and how to find yours.

**Do not read the answer key.** The generator drops a `manifest.json` beside the documents naming the problems
it planted and the outcome it expects. Nothing you build may read it — an analysis that consults it is brilliant
and worthless. It is the test oracle, and it is yours in block 7 only.

**Check the platform's own tooling before hand-rolling.** `uip --help` and the installed skills are ahead of any
document, this one included. Where they disagree with a cookbook, the tool wins — and that disagreement is worth
logging.

**Verify, do not assume.** Nearly every "not found" here is a wrong folder, a wrong tenant, a wrong scope or a
stale cache rather than an absent resource. `uip login status` before believing anything is missing, and read
`known-issues/` before believing a `list` that comes back empty.

## Log what you learn

**One command, one sink.** Findings go to a shared table so they can be counted across everyone doing this
exercise, and `log-finding.py` is the whole interface to it:

```bash
python3 log-finding.py --block 5-case --category friction \
  --summary "What happened, what you tried, what happened next."
```

Seat, agent, model, `uip` version and seed version are filled in for you. Nothing else to look up, no entity id,
no JSON on a command line — the script writes the payload to a file before calling `uip`, which is the only shape
that survives every shell. Several at once: `--file findings.json`, a JSON array of `{block, category, summary}`.

**There is no local findings file.** Do not keep a parallel copy — the table is the record, and a second one
goes stale the first time someone reads it. If the insert fails the row is spooled and retried on your next call,
so carry on building rather than stopping to fix it.

`category` is free text — `seed-gap`, `platform-bug`, `friction`, `workaround`, whatever fits. Do not agonise;
the summary is what gets read. Reuse a category you have already used before inventing a neighbouring one.

**Write it while the finding is fresh**, not in a batch at the end — an hour later it has lost the detail that
made it useful.

**Log the frictions, not only the failures.** Anything that took longer to work out than it should have is the
point of this run: a command whose error named the wrong cause, a document that sent you the wrong way, a step
you only got right on the fourth try. Those are what get fixed before the next person arrives — in this seed, or
in the tooling itself.

It is not homework. It is the deliverable that improves this for the next person, and the most useful thing you
will have when someone asks what the build actually cost.
