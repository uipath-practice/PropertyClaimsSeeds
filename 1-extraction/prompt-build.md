# Block 1a — reading the claim form

**Goal.** Claims arrive as a submitted form, on paper as far as the process is concerned. Teach the system to
read one, so everything downstream works with fields instead of a PDF.

**Read.** `1-extraction/spec.md` (what has to come out, and what "good enough" means) · `1-extraction/taxonomy.md`
(the fields the business needs) · `1-extraction/cookbook.md` (how to build it here, and the traps)

## What the business is asking for

A claimant fills in a claim form. Somewhere in it are the things the rest of the process cannot proceed without:
who is claiming, against which policy, on what property, what happened and when, and an itemised list of what
they say was damaged and what they think it is worth.

Today a person reads that form. You are replacing that reading step — not the judgement that follows it, which
is what the rest of the exercise builds.

**The fields are already agreed.** Someone has been through the form with the claims team and settled which of
them matter and what each is called; that list is `1-extraction/taxonomy.md` and it is not yours to improve.
Every later component was designed against those names, so renaming one to something better breaks a build three
steps away, silently.

## What has to be true

- **Every field group comes back on a form the system has never seen.** A model that works on the examples it
  was trained on has learned those examples.
- **The damage list keeps its rows.** A claim listing five damaged items comes back as five items — not one, not
  a merged blob. This is the part that most often looks right and is not.
- **What you confirmed, you actually checked.** Training this means agreeing or disagreeing with what it read,
  one field at a time, against the document in front of you. Waving through a field you did not look at produces
  a model that scores perfectly and is wrong in production, and you will not find that out here.

## Done when

You can hand the system a claim form it has never seen and get back every field the claims team asked for, with
the right number of damage rows — and you would be comfortable letting the next step act on the result.

## How to test it

Generate a few fresh claims and read the extracted fields **beside the document**, not as a score. A score tells
you the model agrees with what it was taught; you are asking whether it agrees with the form.

Vary them. Claims come from different countries in different currencies with different numbers of damaged items,
and a model trained on a narrow sample fails on the first claim that is not like the others.

## If it stalls, switch

Use `1-extraction/prompt-shared.md` and move on. **A supported route, not a penalty.** Reading the form feeds
everything downstream, so a half-trained model is worse than a borrowed one, and every block after this one is
identical either way. The interesting part of this exercise is not here.

**Where it goes.** Generated code into `Build/ClaimCase-<NN>/` — one solution for the whole build. Notes and
documents you write for this block go in this block's folder.

**Log as you go.** `python3 log-finding.py --block <this-block> --category <kind> --summary "..."` — every
retry, every surprise, everything these instructions failed to explain, and anything that took longer than it
should have. Dead ends included; they are the point. `AGENTS.md` has the detail.
