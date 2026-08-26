# Property claims — build it end to end

A property claim arrives as three documents that do not always agree with each other. Your solution reads them, works out whether the claim is payable and for how much, puts a human in front of the two decisions that need one, and tells the claimant what happened.

**You are not here to learn insurance.** You are here to drive a coding agent through a real end-to-end build — document extraction, analyses, a case lifecycle, a human-facing screen, a deploy. The claims process is the material; the coding agent is the subject.

## Contents

[Get the seed](#get-the-seed) · [What you are building](#what-you-are-building) · [The sequence](#the-sequence) · [How a block works](#how-a-block-works) · [What already exists](#what-already-exists) · [What finished means](#what-finished-means)

## Get the seed

```bash
git clone <seed-repo> ClaimCase-01 && cd ClaimCase-01
```

**The folder you create is your working folder**, so name it for your seat. Then open it in your editor and start your coding agent **in it** — `AGENTS.md` is picked up automatically.

Clone rather than download if you can: everything you build shows up as untracked in `git status`, and anything you changed shows up in `git diff`.

## What you are building

[`PDD.md`](PDD.md) is the whole brief — a claims manager describing how property claims are handled, in business language, naming no software. Read it once before you start. Turning it into a solution is the exercise.

[`method/`](method/) is how UiPath recommends getting from a document like that to a running solution. It is a general method, not specific to this process, and it is what the blocks below follow.

## The sequence

| Block | You produce | Done when |
|---|---|---|
| **1 · [Design](1-design/prompt.md)** | `sdd.md` — the architecture | a solution architect could hand it to a developer and walk away |
| **2 · [Plan](2-plan/prompt.md)** | `tasks.md` — what gets built in what order | the list works top to bottom with nothing blocked by something below it |
| **3 · Build** — five runs, in order | | |
| &nbsp;&nbsp;a · [Extraction](3a-extraction/prompt.md) | a model that reads the claim form, or the shared one adopted | an unlabelled form comes back complete |
| &nbsp;&nbsp;b · [Claim record](3b-entity/prompt.md) | the store every step writes to | a value with cents and a 9,000-character payload round-trip unchanged |
| &nbsp;&nbsp;c · [Checks and analyses](3c-agents/prompt.md) | the components that decide things | each returns what `PDD.md` §7 says — including *nothing* on a clean claim |
| &nbsp;&nbsp;d · [The case](3d-case/prompt.md) | the lifecycle, deployed | a clean claim settles with no task ever raised |
| &nbsp;&nbsp;e · [Validation app](3e-validation/prompt.md) | what a reviewer sees and decides on | both gates render in a browser and a decision writes back |
| **4 · [Verify](4-verify/prompt.md)** | a results table | every planted problem caught by the component that owns it, and a clean claim settled untouched |
| **5 · [Ship](5-ship/prompt.md)** | a packaged solution and a handover | it deploys into a folder that never held it, and a claim runs through |
| **6 · Process app** — *later* | the in-flight view `PDD.md` §11 asks for | it shows live claims, their stage and their SLA |

**Block 3 is five separate runs, not one.** Each piece is built and proven before the next begins — that is the sequencing rule the method insists on, and it is what keeps the last day from being one enormous debugging session.

**Block 6 comes after everything else and is not written yet.** `PDD.md` §11 asks for a real-time view of claims in flight, and §4.4 says why: the only thing doing that job today is a shared spreadsheet that gets overwritten daily. It is a genuine requirement rather than a bonus, and it is the one part of the process nothing else in this build addresses.

## How a block works

```
read the brief  →  prompt your agent  →  it builds  →  run the gate  →  fix, or move on
```

**The gate is a command, not an opinion.** This pipeline fails late and quietly, and a mistake three blocks back costs far more to find than the same mistake caught at its own gate.

**Block 1 decides the day.** It creates nothing on the platform, which makes it the easy one to rush, and it is where the build stops living in your agent's context and starts living on disk. Everything after it is assembly if block 1 is right, and invention if it is not.

## What already exists

You are not starting from nothing. The claim documents are generated for you, the retrieval automations are deployed, the connections are provisioned, and it is all in **your** folder. [`CONFIG.md`](CONFIG.md) has the detail — read *What already exists* before you design anything, because designing a replacement for something already deployed is the commonest way this build goes wrong.

## What finished means

- A claim with a planted problem stops at the right decision point, and the check that owns that problem is the one reporting it — worded so a human can act on it.
- A claim with nothing wrong clears both human gates and settles in full, **with no task raised at all**.
- The claimant's letter says what actually happened.
- You have a design describing what you built, and a set of findings describing what it cost.

**The second one is where most solutions fail.** A solution that finds something to flag on every claim has not learned to be careful — it has learned to always answer *yes* to *"is anything wrong here?"*, which is the easiest way to look thorough and the least useful.
