# Block 5 — the case

**Goal.** Build the case plan that runs the claim: the stages, what happens in each, what waits, what runs in
parallel, and every binding — then deploy it and put a clean claim through, end to end, unattended.

**Read.** `2-design/` (your own design — the stage, task and binding tables you already wrote) ·
`5-case/spec.md` (what must be true) · `contracts/provided-processes.md` (the six processes you bind —
arguments, types, behaviour) · `contracts/claim-entity.md` (what each stage writes) · `5-case/cookbook.md` (the
platform traps — read the first section before editing anything) · `CONFIG.md` (folders, names, Windows)

**This block is the longest one here. Do it in three passes, and finish each before starting the next.** Every
pass ends in a command that either passes or does not, so a pass that goes wrong costs one pass rather than the
block. Between passes, write down where you are: what is built, what is next, what surprised you. You will lose
your working context at some point during this block, and that note is what makes the next hour cheap.

## Pass 1 — the skeleton

Stages, entry and exit conditions, edges. No tasks yet.

- Every stage from your design, each with **exactly one way in**.
- Every stage exit names its finishing task or group, and every downstream entry matches how that stage
  leaves — completed against completed, exited against exited. A mismatch is silent at deploy and fatal at run.
- **Draw an edge for every transition your rules allow.** Rules make it run; edges make it readable.
- **No stage that is not in your design.** An empty stage nothing enters is not a placeholder for later work —
  it is a dead box on the canvas and a warning in every validation from here on.

```bash
uip maestro case validate <caseplan.json> --skeleton --output json     # Valid
```

## Pass 2 — the tasks and the wiring

- **Bind the plumbing; do not build it.** Six processes are already deployed. Read what they are for in
  `contracts/provided-processes.md`, and read their exact arguments from the platform —
  `uip or packages entry-points "<PackageId>:<Version>"` — before binding. If you are about to write a bucket
  download, an IXP call or a PDF-to-text step, you have missed one.
- **Match the types.** One retrieval returns an object, another a string, three return files. A type mismatch
  packs and deploys cleanly and faults on a live claim.
- **One solution, named for your seat**, holding the case and all seven agents. A case cannot bind an agent that
  lives in another solution.
- Parallel work is *grouped*, not sequenced.
- Every stage writes what it produced to the claim record, and nothing it did not — through the shared Data
  Fabric connection, using the **V3 activities** your folder-scoped entity needs (`5-case/cookbook.md`).
- Build **without the two human gateway tasks** — the app does not exist yet and a case cannot deploy binding an
  app that is not built. **Keep both human-decision stages in place and shaped**; block 6 drops a task into each.
  `5-case/spec.md` explains the two passes and what "shaped" has to mean.

```bash
python3 5-case/check_caseplan.py <caseplan.json>       # 0 problems
uip maestro case validate <caseplan.json> --output json
```

## Pass 3 — deploy, and run a clean claim

The acceptance run is **a claim with nothing wrong with it**: `scenario=auto-settle`, no discrepancy. It must
reach an ending on its own, with no human asked and no Action Center task raised.

```bash
uip maestro case pack <case-project-dir> <throwaway-dir>       # recompiles caseplan.json.bpmn
grep -c "<a-token-your-edit-introduced>" caseplan.json.bpmn    # not 0 — the runtime has your change
```

Then deploy into your seat folder and start one aimed run (`7-testing/spec.md` has the aiming, and `CONFIG.md`
has the shell-quoting trick if you are on Windows).

**Done when** a clean claim reaches an ending, every stage it entered shows complete, and the claim record
carries a row written stage by stage. A claim sitting in `Running (With Faults)`, or a stage whose tasks are all
green while the next stage never started, is a failure.

**If the clean claim gets flagged for review, the case plan is not what is wrong.** It has parked at the review
stage exactly as designed, because an analysis said something was off with a claim that has nothing wrong with
it. Go back to that agent's prompt and fix the over-flagging — `7-testing/spec.md` says how to find which one.
A workshop-day claim that always needs a human is a solution nobody would ship.

**Where it goes.** Generated code into `Build/ClaimCase<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block 5-case --category <kind> --summary "..."` — every retry,
every surprise, everything these instructions failed to explain, and anything that took longer than it should
have. Dead ends included; they are the point. `AGENTS.md` has the detail.
