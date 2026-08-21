# Block 1b — use the shared reader

**Goal.** Use the extraction model the team already has, rather than training your own, and satisfy yourself it
reads a claim form properly before the rest of your build depends on it.

**Read.** `1-extraction/spec.md` (what has to come out of it) · `1-extraction/cookbook.md`, *Adopting the shared
project* (where it is and how to point at it)

## Why this route exists

Training a document reader is a craft, and it is not what this exercise is about. Reading the claim form feeds
every later step, so a half-trained model of your own is worse than a working one someone else built. **Take
this route whenever extraction has stopped being the interesting part of your day** — every block after this one
is identical either way.

## What has to be true

- **It returns every field group the claims team asked for**, under the agreed names.
- **The damage list keeps its rows** — a claim listing five damaged items comes back as five.
- **You know which model you used, and can say so.** A later reader of your solution has to be able to tell
  where the extracted data came from; write the project and version into your notes.

## Done when

You have run a real claim form through it and seen every field the later steps need come back correctly, with
the right number of damage rows.

**Where it goes.** Generated code into `Build/ClaimCase-<seat>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.

**And you have read the cookbook back** — the two-sided review in `AGENTS.md`, *Before you finish a
block*. Two minutes, and it is what keeps this seed from only ever growing.

