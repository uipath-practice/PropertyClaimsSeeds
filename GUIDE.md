# Property Claims — the exercise

> **Draft, 2026-08-23.** The sequence and the prompts are real; the prose around them is a skeleton that becomes
> lessons once a build has been through it. **Every block ships a full prompt, and blocks 5, 6 and 7 ship the
> largest documents in the seed** — do not skim them because this banner used to say they were outlined.

## Getting the seed onto your machine

If you are reading this, you may already have it. If not — one line in a terminal, and **the folder you create
is your working folder**, so name it for your seat:

```bash
git clone https://github.com/uipath-practice/PropertyClaimsSeeds.git ClaimCase-01
cd ClaimCase-01
```

No git on the machine? The same content as a zip:

```bash
curl -L https://github.com/uipath-practice/PropertyClaimsSeeds/archive/refs/heads/main.zip -o seed.zip
unzip seed.zip && mv PropertyClaimsSeeds-main ClaimCase-01 && cd ClaimCase-01
```

On Windows PowerShell, `Invoke-WebRequest -Uri <url> -OutFile seed.zip` then `Expand-Archive seed.zip`.

**Clone if you can.** Everything you build shows up as untracked in `git status`, and anything of ours you
changed shows up in `git diff` — which makes "what did I actually produce" a command rather than a memory test,
and is worth logging at the start. `VERSION` records which seed you have;
quote it if you report a problem.

Then open the folder in your editor and start your coding agent **in it**. `AGENTS.md` and `CLAUDE.md` are
picked up automatically.

## What you are building, and why this shape

A property insurance claim arrives as three documents that do not always agree with each other. Your solution has
to read them, work out whether the claim is payable and for how much, put a human in front of the two decisions
that need one, and tell the claimant what happened.

You are not being asked to learn insurance. You are being asked to **drive a coding agent through a real
end-to-end build** — one that spans document extraction, AI analyses, a case lifecycle, a human-facing app and a
deploy. The claims process is the material; the coding agent is the subject.

**What you get:** a seed folder describing the process, the contracts between components, and what a working
result looks like. **What you write:** everything else — the agent prompts, the case plan, the entity, the app.
The seed says *what* must be true. How you get there is the exercise.

## How a block works

Every block is the same loop, and it is the loop worth taking away:

```
read the seed  →  prompt your agent  →  it builds  →  run the gate command  →  fix, or move on
```

**The gate is a command, not an opinion.** Each block ends with something you run that either passes or does not.
That is deliberate: this pipeline fails late and quietly, and a mistake three blocks back costs far more to find
than the same mistake caught at its own gate.

**Log findings as you go.** It is how the next cohort's seed gets better, and it is the most useful thing you
will have at the end when someone asks what the build actually cost. `AGENTS.md` says what and how.

## The sequence

| Block | You build | Gate | Roughly |
|---|---|---|---|
| 1 | **Extraction** — an IXP project that reads the claim form. Build your own, **or** adopt the shared one | six field groups back, damage rows repeating correctly | ~60 min · ~5 min shared |
| 2 | **The design** — four tables (stages · work · data · traceability) and an SDD | you can answer block 2's three questions from the tables alone | ~45 min |
| 3 | **The claim record** — a Data Fabric entity | every payload has a home, and the ones with no column say why | ~20 min |
| 4 | **The analyses** — seven agents | one runs on a pinned input; review grade ≥ B | ~90 min |
| 5 | **The case** — the lifecycle, the two gateways, the wiring. **Three passes**: skeleton, wiring, deploy | a clean claim settles end to end, unattended | ~90 min |
| 6 | **The app** — what a reviewer sees at each gateway | both gateways render; a decision writes back | ~90 min |
| 7 | **Test** — aim runs at known problems | nine pinned runs and two clean runs behave | ~45 min |

Timings are a sketch until a real cohort has run it.

### Why this order

**Block 2 before anything is built.** Not ceremony: the analyses hand data to the case, the case hands it to the
app, and the shapes have to be agreed before three components are written against three different guesses.

**Agents (4) before the case (5).** Agents are the only component you can test on their own — one command, one
pinned input, no deploy. The case plan is the most failure-prone artifact in the build and binds to things that
must already exist, so it is worth authoring once, against components that are real.

**The app (6) after a real run.** Build it against payloads your own agents actually produced, not against
payloads you imagined.

## Block 2 is the one that decides the day

Block 2 creates nothing on the platform, which makes it the easy one to rush. It is also the one that decides
what blocks 4 and 5 cost, because **it is where the build stops living in your agent's context and starts living
on disk.** Blocks 4 and 5 are long enough that your agent will lose its working context partway through at least
one of them; what it comes back to is either four tables it wrote, or the whole process description again.

The last of the four tables is the honesty check: **every planted problem, and which of your components catches
it.** If you cannot fill it in from your own design you do not yet understand the process well enough to build
it, and every hour after this point gets more expensive to correct. If you can, the rest of the exercise is
execution — and the same table becomes your test plan in block 7. `2-design/spec.md` has its columns.

## Block 5 is passes, not one attempt

The case plan is the biggest single piece of work here and the one that fails in the most ways, so its prompt
splits it into passes that each end in a command. **Take them seriously as stopping points**: a pass that goes
wrong costs a pass, where the same mistake found at the end costs the block. The passes themselves, and what
closes each, are `5-case/prompt.md`'s — they have changed once already and this page is not the place to learn
them from.

## When a block goes wrong — checkpoints

`checkpoints/` holds a working version of a block's output. Restore one and carry on.

Using a checkpoint is a **deliberate choice, not a failure** — the same logic as block 1's shared extraction
project. A half-finished component that everything downstream depends on is worse than a borrowed working one,
so take the checkpoint the moment a block stops being the interesting part of your day.

Two things make it honest. **Read the block's `spec.md` anyway** — block 5 binds these components by name, and
debugging a wiring problem in something you have never looked at is the most expensive hour available here. And
**log it**: which checkpoint, when, and what had gone wrong. That is the clearest signal
we get about where this is too hard.

## Block 1 has two routes, on purpose

Training an extraction model is the one block with a real floor on how long it takes — most of it spent waiting
for retrains. So there are two prompts: build your own, or adopt a shared project that is already trained.

**Falling back is a supported path, not a penalty.** Extraction feeds every block after it, so a half-trained
model is worse than a borrowed one. Pick the shared project the moment yours stops being the interesting part of
your day; everything downstream is identical either way, because both produce the same six field groups.

## What already exists

You are not starting from nothing. The claim documents are generated for you by a process that already runs and
drops them into storage; the connections for email and data are provisioned; and it is all in **your** folder.
`CONFIG.md` has the details, including the one that trips most builds — **a solution folder is not the same
folder**, so anything your case plan calls needs its folder named explicitly.

## What "finished" means

- A claim with a planted problem stops at the right gateway, and the analysis that owns that problem is the one
  reporting it — worded so a human can act on it.
- A claim with nothing wrong clears both gateways and settles in full, unattended.
- The claimant's letter says what actually happened.
- You have an SDD describing what you built, and a table of findings describing what it cost.

The second one is the one most solutions fail. A solution that finds something to flag on every claim has not
learned to be careful — it has learned to always answer *yes* to "is anything wrong here?", which is the easiest
way to look thorough and the least useful.
