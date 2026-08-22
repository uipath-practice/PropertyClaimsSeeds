# Block 4 — the analyses

**Goal.** Seven questions have to be answered about every claim, and answering them is what a claims handler
spends their day on. Build the things that answer them.

**Read.** `pdd.md` §5 (what each analysis has to decide) and §9 (the nine problems that turn up in real claims) ·
`2-design/` (your own tables — which analysis you made responsible for what) · `4-agents/spec.md` (the set, and
the shape every answer takes) · `contracts/check-envelope.md` (that shape, in detail) ·
`4-agents/cookbook.md` (how to build them here)

## What the business is asking for

Seven questions, each owned by one analysis:

| | Asks |
|---|---|
| **Eligibility** | Should we be looking at this claim at all? |
| **Report validation** | Is the surveyor's report usable, and what does it actually say? |
| **Coverage** | Does the policy respond to this loss? |
| **Payout** | What is payable, and how was that figure reduced? |
| **Credibility** | Does the claimant's account hold together? |
| **Decision** | Given all of the above, what do the rules recommend? |
| **Response** | What do we tell the claimant? |

**None of them decides the claim.** They report; a person decides. That separation is the whole design
(`pdd.md` §4), and an analysis that quietly settles something on its own removes the decision a human is
accountable for.

## What a good analysis produces

Everything here follows from one idea: **a person reads this.** Two of them, in fact — an eligibility reviewer
and a claims adjuster — and what they can see determines whether they can decide.

- **Show your work.** A verdict with no reasoning is not reviewable. Say what was checked, what was found, and
  what in the documents supports it.
- **Report the checks that passed, too.** A screen listing three problems does not tell a reviewer whether the
  other twelve things were checked or skipped.
- **Say it in a sentence, not a field name.** These strings go straight onto a screen a claims handler reads.
- **Do not find fault where there is none.** An analysis that flags something on every claim has learned that
  flagging looks thorough. It costs a human's attention every time, and a solution that stops a *clean* claim has
  failed even though every individual check looks defensible.
- **Stay in your lane.** Where two analyses touch the same fact, the one that does not own it says so and names
  the owner, rather than raising it as its own finding. Three of these run at the same time and none of them can
  see what the others found.
- **Respect what a human already settled — and notice when nobody was asked.** Every analysis after screening is
  told what the reviewer decided and why. A finding they saw and accepted is closed (`pdd.md` §6). But most
  claims never reach that reviewer, so the same inputs also have to carry *"screening passed, nobody was asked"*
  — and an empty decision must not be read as approval of anything.

**Two of the seven read a document rather than extracted fields** — the policy and the surveyor's report. Those
documents are prose whose meaning lives in specific sentences, and an analysis has to be able to quote the one it
relied on. `4-agents/spec.md` says how they receive it and what that costs when you come to test them.

## Done when

Each analysis answers its own question, on a real claim, in language a claims handler could act on.

Specifically: **a clean claim comes back clean** — every check run, every check passed, nothing flagged — and a
claim with a known problem in it is caught **by the analysis that owns that problem**, worded so a reviewer can
see what is actually wrong rather than which rule fired.

**And all seven are registered in the solution**, not merely present on disk:

```bash
uip solution projects list        # seven analyses, by name — reads the manifest, no tenant needed
```

Building an analysis and registering it are two different things, and only the first has an obvious symptom. A
seat finished this block with seven working analyses and **five** in the manifest; block 5 discovered it, because
a case binds through the solution registry and can only see what the manifest lists. Repairing it there cost
hours and needed the manifest rebuilt — the CLI refuses both `projects add` ("already exists") and
`projects remove` ("not found") once the two disagree. One command here; a rebuild there.

**And you have read the cookbook back** — the two-sided review in `AGENTS.md`, *Before you finish a
block*. Two minutes, and it is what keeps this seed from only ever growing.

## How to test it

Build and test **one** analysis end to end before generating the other six. They share a shape, so a mistake in
the first is a mistake in all seven, and finding it after you have built them all costs seven fixes.

Then run each one on a pinned claim and read the output as a reviewer would. `4-agents/cookbook.md` has the
commands, including which of the seven can be exercised on their own and which cannot until block 5.

**A tooling grade is a floor, not a pass.** Your platform will score these agents and it has no idea what this
pipeline is — it cannot tell that an analysis is missing an input it needs, or that two components spell the same
payload differently. Read what you built.

**Where it goes.** Generated code into `Build/ClaimCase-<seat>/` — one solution for the whole build. Nothing is
published in this block: these ship inside the solution the case deploys in block 5. Notes and documents you
write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
