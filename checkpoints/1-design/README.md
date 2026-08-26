# Checkpoint — the case design

A worked `sdd.md` for the process in `PDD.md`. **Restore it if your design block goes wrong**, so the build blocks can carry on.

Taking a checkpoint is a deliberate choice, not a failure. A half-finished design that every later block depends on is worse than a borrowed working one — and this block is the one whose mistakes are cheapest to fix and most expensive to leave.

**Read the block's own prompt anyway.** The build blocks bind these stages and tasks by name, and debugging a wiring problem in a design you have never read is the most expensive hour available here.

```bash
cp checkpoints/1-design/sdd.md .
python3 1-design/check_sdd.py sdd.md --pdd PDD.md      # exits 0
```

## What it contains

8 stages · 29 tasks, one per `PDD.md` §5.3 step · 22 case variables · the 5 stage SLAs the PDD gives and no others · both human gates as `action` tasks · both waits as `wait-for-connector`.

Every task's type comes from §5.3's **Decision nature** column: *rule-expressible* work on a deterministic runner, *judgement* work on an agent. Two steps are worth knowing about because a design shaped by tenant discovery gets them wrong — **4.3 settlement** and **5.1 the decision rules** are both marked rule-expressible, and both belong on a deterministic runner however tempting the alternative looks.

## Two things it does deliberately

**`Missing details` is present and inert.** §15 defers the asking, not the detection. A stage with no entry condition is orphaned rather than unwired, so the lane carries a complete interrupting entry condition guarded by `missingDetailsLaneEnabled` — a variable defaulting `"false"` that nothing produces. Wiring it later means adding one producer, not restructuring. The B-02 detection is still live at task 1.2.

**Business days are prose, not configuration.** The rule is stated in the design; attaching a calendar is a build-time step — `1-design/cookbook.md` has the entry.

## Resource identities are unresolved on purpose

The design names what each task needs and does not bind tenant ids. Resolution belongs to the build, against your own seat.
