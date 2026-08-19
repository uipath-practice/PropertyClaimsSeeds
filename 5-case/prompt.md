# Block 5 — the case

**Goal.** Build the case plan that runs the claim: the stages, what happens in each, what waits, what runs in
parallel, and every binding — then deploy it and put a real claim through.

**Read.** `pdd.md` §3 (the lifecycle) and §4 (the two human decisions) · `5-case/spec.md` (what must be true) ·
`contracts/provided-processes.md` (the six processes you bind — arguments, types, behaviour) ·
`contracts/claim-entity.md` (what each stage writes) · `5-case/cookbook.md` (the platform traps — read the first
section before editing anything) · `CONFIG.md` (folders and names)

**Must hold.**

- **Bind the plumbing; do not build it.** Six processes are already deployed. Read what they are for in
  `contracts/provided-processes.md`, and read their exact arguments from the platform —
  `uip or packages entry-points "<PackageId>:<Version>"` — before binding. If you are about to write a bucket
  download, an IXP call or a PDF-to-text step, you have missed one.
- **Match the types.** One retrieval returns an object, another a string, three return files. A type mismatch
  packs and deploys cleanly and faults on a live claim.
- **One solution, named for your seat**, holding the case and all seven agents. A case cannot bind an agent that
  lives in another solution.
- Build **without the two human gateway tasks** this block — the app does not exist yet and a case cannot deploy
  binding an app that is not built. **Keep both human-decision stages in place and shaped**, so block 6 drops a
  task in rather than restructuring. `5-case/spec.md` explains the two passes.
- Every stage exit names its finishing task, and every downstream entry matches how that stage leaves —
  completed against completed, exited against exited. A mismatch is silent at deploy and fatal at run time.
- Each stage has exactly one way in.
- Parallel work is *grouped*, not sequenced.
- Every stage writes what it produced to the claim record, and nothing it did not.
- Before believing any edit reached the runtime, prove it: the compiled `.bpmn` is what runs, not the file you
  edited.

**Done when.**

```bash
python3 5-case/check_caseplan.py caseplan.json    # 0 problems
grep -c "<a-token-your-edit-introduced>" caseplan.json.bpmn   # not 0
```

Then run one aimed claim end to end (`7-testing/spec.md` has the aiming). It reaches an ending, every stage it
entered shows complete, and the claim record carries a row written stage by stage. A claim sitting in
`Running (With Faults)`, or a stage whose tasks are all green while the next stage never started, is a failure.

**Where it goes.** Generated code into `Build/ClaimCase<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** Append to `build-findings.md`, and insert a row per finding into `WorkshopFindings` as
`AGENTS.md` describes — every retry, every surprise, and everything these instructions failed to explain. Dead
ends included; they are the point.
