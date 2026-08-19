# Checkpoints — a way back in

A working version of a block's output, so a block that has gone wrong does not cost you the rest of the day.

| Checkpoint | Restores | Cost of using it |
|---|---|---|
| `3-claim-record/` | the Data Fabric entity, 38 columns | none conceptual — block 3 is a contract in, a schema out |
| `4-agents/` | seven working analyses | **the whole of block 4** — read its README first |

**Using one is a deliberate choice, not a failure.** Extraction has a shared project for the same reason: a
half-finished component that everything downstream depends on is worse than a borrowed working one. Pick a
checkpoint the moment a block stops being the interesting part of your day.

**But read the block's `spec.md` either way.** Block 5 binds these components by name, and debugging a wiring
problem in something you have never looked at is the most expensive hour in this exercise.

**Say so in `build-findings.md`.** Which checkpoint, at what point, and what had gone wrong. That is not an
admission — it is the single most useful signal about where the seed is too hard, and it is why the next
cohort's version is better.
