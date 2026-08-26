# Agentic delivery with coding agents

**How a business process becomes a running UiPath solution when coding agents do the building.** Oriented to the agentic stack — Case Management or BPMN as the coordination host, with Data Fabric, IXP, Coded Apps, Agents, API Workflows and RPA as components.

This is a **general method**. Nothing in it is specific to the process you are building here, and it is published on its own as well — the worked examples in [`samples/`](samples/) are the only part that knows what this exercise is about.

## What is here

| File | Answers |
|---|---|
| [`delivery-process.md`](delivery-process.md) | the stages, who owns each, what closes each gate, and what each stage owes the next |
| [`pdd-guide.md`](pdd-guide.md) | what a PDD must carry for a design stage to work from it without inventing business rules |
| [`template-pdd.md`](template-pdd.md) | the skeleton to fill in |
| [`sdd-guide.md`](sdd-guide.md) | what an SDD must carry, how deep to go, and the two documents that share the name |
| [`template-sdd-case.md`](template-sdd-case.md) | the Case Management skeleton |
| [`samples/`](samples/) | a worked PDD and SDD, complete |

## Two ways to use it

**Forward, to build.** Work the stages in order. Each has a gate, and the gate is what stops a defect travelling to where it costs ten times as much to fix.

**Backward, to review.** Point a coding agent at these guides and at a PDD or SDD somebody else wrote, and ask what a design stage would have to guess. That is the cheapest quality signal available on a document, and it takes minutes:

> Read `pdd-guide.md` and `template-pdd.md`. Then read `<their-pdd>` and tell me: which MUST sections are absent; every place a design stage would have to invent a business rule; every threshold that is not numeric; every decision with no stated decision nature; and anything that names a product, which does not belong in a PDD at all. Quote the document. Do not fix it.

The same shape works for an SDD against `sdd-guide.md`, and it is worth running **before** anyone builds from either.

## What it is grounded in

Claims are tagged so you can tell what is checkable from what is judgement:

| Tag | Meaning |
|---|---|
| `[SKILL]` | encoded in the shipped `UiPath/skills` repository — what the agent will actually do. Verify with `uip skills install` and read it |
| `[UIPATH]` | UiPath public documentation or product statement |
| `[MEASURED]` | observed on a real build, with what it cost |
| `[JUDGEMENT]` | a recommendation, not doctrine |

**Where a guide and an installed skill disagree, the skill wins** — and the disagreement is worth reporting. Several claims here started as documentation and turned out to describe a version that had already moved.
