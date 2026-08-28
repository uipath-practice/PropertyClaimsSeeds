# Agentic delivery with coding agents

**How a business process becomes a running UiPath solution when coding agents do the building.** Oriented to the agentic stack — Case Management or BPMN as the coordination host, with Data Fabric, IXP, Coded Apps, Agents, API Workflows and RPA as components.

This is a **general method**. Nothing in it is specific to the process you are building here; the one worked example is [`PDD.md`](../PDD.md) at the seed root, written to the guide below — 15 sections, 51 numbered business rules each with a worked example, a §5.3 step table where every decision carries its nature.

## What is here

| File | Answers |
|---|---|
| [`delivery-process.md`](delivery-process.md) | the stages, who owns each, what closes each gate, and what each stage owes the next — the blocks in `README.md` are these stages |
| [`pdd-guide.md`](pdd-guide.md) | what a PDD must carry for a design stage to work from it without inventing business rules — the standard `PDD.md` was written to |
| [`sdd-guide.md`](sdd-guide.md) | what an SDD must carry, how deep to go, and what the build does and does not check — read its first section before `1-design` |
| [`sdd-addendum.md`](sdd-addendum.md) | the two sections the seed adds to the planner's own template — the claim entity with its write-ownership matrix, and the design's feedback to the PDD |

## Two ways to use it

**Forward, to build.** Work the stages in order. Each has a gate, and the gate is what stops a defect travelling to where it costs ten times as much to fix.

**Backward, to review.** Point a coding agent at a guide and at a PDD or SDD somebody else wrote, and ask what a design stage would have to guess. That is the cheapest quality signal available on a document, and it takes minutes:

> Read `method/pdd-guide.md`. Then read `<their-pdd>` and tell me: which MUST sections are absent; every place a design stage would have to invent a business rule; every threshold that is not numeric; every decision with no stated decision nature; and anything that names a product, which does not belong in a PDD at all. Quote the document. Do not fix it.

The same shape works for an SDD against `sdd-guide.md`, and it is worth running **before** anyone builds from either.

## What it is grounded in

Claims are tagged so you can tell what is checkable from what is judgement:

| Tag | Meaning |
|---|---|
| `[SKILL]` | encoded in the shipped `UiPath/skills` repository — what the agent will actually do. Verify with `uip skills install` and read it |
| `[UIPATH]` | UiPath public documentation or product statement |
| `[MEASURED]` | observed on a real build, with what it cost |
| `[JUDGEMENT]` | a recommendation, not doctrine |

**Where a guide and an installed skill disagree, the skill wins** — and the disagreement is worth logging. Several claims here started as documentation and turned out to describe a version that had already moved.
