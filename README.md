# Property claims processing end to end implementation plan

A property claim arrives and needs to be analyzed. Three documents related to the claim do not always agree with each other. Your solution reads them, works out whether the claim is payable and for how much, puts a human in front of the two decisions that need one, and keeps the claimant updated on progress.

**You are not here to learn insurance.** You are here to drive a coding agent through the end-to-end build — from document extraction, building analysis Agents, stitching together a Maestro Case with a Coded Action Apps for validation screen and dashboard overview. Build, Test and Deploy. 

## Contents

[Get the seed](#get-the-seed) · [What you are building](#what-you-are-building) · [The sequence](#the-sequence) · [How a block works](#how-a-block-works) · [Clearing context](#clearing-your-agents-context-between-blocks) · [What already exists](#what-already-exists) · [What finished means](#what-finished-means)

## Get the seed

**You have been given a seat name** — a word or a number that follows `ClaimCase-` on your Orchestrator folder. Everything you create takes it. Use it here:

```bash
git clone https://github.com/uipath-practice/PropertyClaimsSeeds.git ClaimCase-<seat>
cd ClaimCase-<seat>
```

No git on the machine? The same content as a zip:

```bash
curl -L https://github.com/uipath-practice/PropertyClaimsSeeds/archive/refs/heads/main.zip -o seed.zip
unzip seed.zip && mv PropertyClaimsSeeds-main ClaimCase-<seat>
cd ClaimCase-<seat>
```

On Windows PowerShell: `Invoke-WebRequest -Uri <url> -OutFile seed.zip`, then `Expand-Archive seed.zip`.

Then put your toolchain on the line this seed was tested on — the four commands are in [`CONFIG.md`](CONFIG.md), *Toolchain* — sign in, and open the folder in your editor:

```bash
uip login                    # the tenant CONFIG.md names
uip login status             # confirm the org and tenant match
```

Start your coding agent **in this folder** — `AGENTS.md` and `CLAUDE.md` are picked up automatically. Point it at [`1-design/prompt.md`](1-design/prompt.md) and work down [the sequence](#the-sequence).

**Clone rather than download if you can.** Everything you build shows up as untracked in `git status` and anything you changed shows up in `git diff`, which is the cheapest way to see what you actually did. It also means `git pull` brings you any fix we ship mid-workshop.

## What you are building

[`PDD.md`](PDD.md) is the whole brief — a claims manager describing how property claims are handled, in business language, naming no software. Read it once before you start. Turning it into a solution is the exercise.

[`method/`](method/) is how UiPath recommends getting from a document like that to a running solution. It is a general method, not specific to this process, and it is what the blocks below follow.

## The sequence

| Block | You produce | Done when | Go and look at it |
|---|---|---|---|
| **1 · [Design](1-design/prompt.md)** | `sdd.md` — the architecture | a solution architect could hand it to a developer and walk away | the document — read Section 2 and see whether the stages match how a claim really moves |
| **2 · [Plan](2-plan/prompt.md)** | `tasks.md` — what gets built in what order | the list works top to bottom with nothing blocked by something below it | the list — every generation task should be followed by something that checks it |
| **3 · Build** — six runs, in order | | | |
| &nbsp;&nbsp;a · [Extraction](3a-extraction/prompt.md) | the shared IXP project adopted and proven on a real form — or, by [`prompt-build.md`](3a-extraction/prompt-build.md), your own IXP project trained | an unlabelled form comes back complete | the extraction result over a real form, field by field, with its confidence |
| &nbsp;&nbsp;b · [Claim record](3b-entity/prompt.md) | the Data Fabric entity every step writes to | a value with cents and a 9,000-character payload round-trip unchanged | the table in Data Fabric, and a row in it |
| &nbsp;&nbsp;c · [Agents](3c-agents/prompt.md) | the seven Agents that decide things | each returns what `PDD.md` §7 says — including *nothing* on a clean claim | one agent's trace — what it was given, what it concluded, and why |
| &nbsp;&nbsp;d · [The case](3d-case/prompt.md) | the Maestro case, authored and validated | both gates are green and the plan opens in Studio Web | **the case diagram** — the whole process as a picture, for the first time |
| &nbsp;&nbsp;e · [Run it](3e-run/prompt.md) | the case, deployed and proven | a clean claim settles with no task ever raised, and the four human routes work | **a live instance, stages completing one after another** — the moment it stops being files |
| &nbsp;&nbsp;f · [Action App](3f-validation/prompt.md) | the Coded Action App a reviewer decides in | both gates render in a browser and a decision writes back | the reviewer's screen in Action Center, with a real claim on it |
| **4 · [Verify](4-verify/prompt.md)** | a results table | every planted problem caught by the component that owns it, and a clean claim settled untouched | your own results table against the answer key |
| **5 · [Hand over](5-ship/prompt.md)** | the deployed version pinned, and an operator runbook | the deployed version is the one you packed, and the runbook says how it moves on | the solution in Studio Web, exactly as it runs |
| **6 · Process app** — *later* | the in-flight view `PDD.md` §11 asks for | it shows live claims, their stage and their SLA | — |

**Block 3 is six separate runs, not one.** Each piece is built and proven before the next begins — that is the sequencing rule the method insists on, and it is what keeps the last day from being one enormous debugging session.

**Authoring the case and running it are two blocks on purpose.** They fail in completely different ways: a plan that will not validate is a design problem, and a plan that validates and then misbehaves is a binding problem. Kept together, the second gets debugged through repeated deploys of the first. **Take the look at the diagram before you deploy** — it is the cheapest review you will ever do on this build, and the stage order being wrong is obvious in a picture and invisible in JSON.

**Block 6 comes after everything else and is not written yet.** `PDD.md` §11 asks for a real-time view of claims in flight, and §4.4 says why: the only thing doing that job today is a shared spreadsheet that gets overwritten daily. It is a genuine requirement rather than a bonus, and it is the one part of the process nothing else in this build addresses.

## How a block works

```
read the brief  →  prompt your agent  →  it builds  →  run the gate  →  fix, or move on
```

**The gate is a command, not an opinion.** This pipeline fails late and quietly, and a mistake three blocks back costs far more to find than the same mistake caught at its own gate.

**Block 1 decides the day.** It creates nothing on the platform, which makes it the easy one to rush, and it is where the build stops living in your agent's context and starts living on disk. Everything after it is assembly if block 1 is right, and invention if it is not.

## Clearing your agent's context between blocks

**A block boundary is the safe place to start your agent fresh, and you should use it.** Everything a later block needs is on disk — `sdd.md`, `tasks.md`, the components you built and published — which is the whole reason the blocks are separate runs. Nothing of value lives only in the conversation.

What you carry forward is nothing; what you lose by *not* clearing is real. An agent running near its limit compacts itself, and a compaction quietly drops the detail of what it just built — so it starts re-deriving decisions it already made, and any finding it was holding to write up later is simply gone.

| Your model's context | What to do |
|---|---|
| **~1M tokens** | You can run from block 1 through authoring the case without clearing — if you do, clear before deploying and running it, and again before the app. |
| **~250k tokens** | **Clear or compact after every block.** You will otherwise be compacting mid-block, which is the worst moment for it — halfway through something, with the reasoning that got you there being summarised away. |

**Log findings as you go, not at the end** — see [`AGENTS.md`](AGENTS.md), *Log what you learn*. This is the rule clearing depends on: what survives a fresh start is what you already sent.

**If a block goes badly wrong, clear and start it again from the brief.** A long recovery conversation carries every wrong turn with it, and re-running a block from a clean context against artifacts that are already on disk is usually faster than untangling one.

## What already exists

You are not starting from nothing. The claim documents are generated for you, the retrieval automations are deployed, the connections are provisioned, and it is all in **your** folder. [`CONFIG.md`](CONFIG.md) has the detail — read *What already exists* before you design anything, because designing a replacement for something already deployed is the commonest way this build goes wrong.

## What finished means

- A claim with a planted problem stops at the right decision point, and the check that owns that problem is the one reporting it — worded so a human can act on it.
- A claim with nothing wrong clears both human gates and settles in full, **with no task raised at all**.
- The claimant's letter says what actually happened.
- You have a design describing what you built, and a set of findings describing what it cost.

**The second one is where most solutions fail.** A solution that finds something to flag on every claim has not learned to be careful — it has learned to always answer *yes* to *"is anything wrong here?"*, which is the easiest way to look thorough and the least useful.
