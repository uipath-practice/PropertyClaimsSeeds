# The delivery process

Seven stages, three documents, one routing file. The documents are **not** interchangeable and the boundaries are load-bearing.

```
 Discovery → PDD → SDD → tasks.md → build → verify → ship
              ▲     │                  │        │
              └─────┘ design feedback   └────────┴─ traceability back to SDD/PDD
```

| | Carries | Signed by |
|---|---|---|
| **PDD** | what the business does and needs | the business |
| **SDD** | how the platform will do it — the machine-readable contract the agent builds from | the BA and architect |
| **`tasks.md`** | which skill builds what, in what order, blocked by what. Generated, disposable, regenerable | the developer |

**The single most important structural rule: the SDD contains architecture only, never a task list; the task list contains routing only, never architecture.** `[SKILL]`

## The stages

| # | Stage | Owner | Skill | Output | Gate |
|---|---|---|---|---|---|
| 0 | Discovery & suitability | BA | `uipath-automation-discovery` | discovery report, estate inventory | suitability ∈ proceed / proceed-with-redesign / partial / do-not-automate |
| 1 | PDD | BA, with the business | template, or a process-capture tool | `pdd.md` + sample data + as-is/to-be maps | **business sign-off** |
| 2 | SDD | Solution Architect | `uipath-planner`, or the host skill's own design phase | the design document | `Status: ready`, template conformance |
| 3 | Plan | architect / lead dev | `uipath-planner` Lane A | `tasks.md` | every element has a task; leaves before consumers |
| 4 | Implement | developer | one specialist per task | artifacts + a provenance sidecar | every `Validate:` passes |
| 5 | Verify | dev / QA / architect | `uipath-test`, `uipath-review` | test results, graded review | 0 Critical, traceability complete |
| 6 | Ship | dev / DevOps | `uipath-solution`, `uipath-platform` | packed `.uipx`, deployment, runbook | production readiness sign-off — this exercise stops here at the runbook (`5-ship`) |

## Stage 0 — suitability, before anything is chosen

Seven checks, each recorded with one line of evidence in the eventual SDD. `[SKILL]`

1. **Native capability** — does the source system already do this? Configure, don't automate.
2. **Existing estate** — is something deployed already covering these steps? Reuse.
3. **Process stability** — *"automating a moving target is rework."*
4. **Redesign first** — *"steps that exist only to work around manual limitations drop out of the to-be; never automate waste."*
5. **Access feasibility** — licences, API access, credentials, environments.
6. **Economics** — volume × time saved against build + run + maintain.
7. **Residual human work** — *"when the human loop dominates, automation may not pay."*

Also capture here, because they gate every later product decision: **delivery model** (cloud / Automation Suite + version / standalone), stated product exclusions with reasons, document storage location, signing modality, robot attendance, email protocol.

> **`[MEASURED]` Check 2 has a failure mode nobody documents.** An estate sweep on a tenant that already holds a solution to the same problem does not merely offer reuse — **it reshapes the design**. On one run the sweep found a prior build and the design took its task types from what was deployed rather than from the PDD, and said so outright. Forbidding *reuse* did not stop it; the estate still drove the choices. On a shared tenant this means every team after the first inherits its neighbours' architecture, and the convergence looks like agreement. Scope discovery deliberately, or run design against a clean tenant.

## Stage 1 — the PDD

Full structure in [`pdd-guide.md`](pdd-guide.md). What matters at this altitude: the PDD's job for a coding agent is narrower and sharper than in classic delivery. It must carry enough **decidable signal** that the design stage can place each step on the right executor without inventing business rules — determinism per step, input structure, integration surface, state, coordination shape, volume, risk, reversibility, volatility, trigger.

**What it must not do is pre-select the technology.**

## Stage 2 — the SDD

Full structure in [`sdd-guide.md`](sdd-guide.md), and **read its first section before you write one** — two different documents share the name, and picking the wrong one fails silently rather than loudly.

The operative depth rule:

> **The SDD carries every decision that is a design choice or a contract between components. It stops at anything that (a) requires touching a live system to determine, or (b) is purely internal to one component.** `[SKILL]`

### How the product is chosen — four layers, in order `[SKILL]`

1. **Decompose into steps.**
2. **Choose an executor per step:**

| Step verb | Executor |
|---|---|
| validate / transfer, deterministic | RPA, or API Workflow where a stable API is reachable from that runtime |
| read/write machine-local data | RPA — cloud runtimes cannot reach these |
| collect from semi-structured documents | IXP / Document Understanding |
| decide or classify requiring judgement | AI Agent; or rules/DMN for thresholds |
| create or summarize free-form | Agent |
| review / escalate / sign-off | HITL, **host-aware** — Case → `action` task; BPMN → inline `userTask`; Flow → HITL skill; RPA → Action Center |
| wait or approve inside **one** process | long-running RPA + Action Center — **never Maestro** |
| sequence multiple automations | Maestro Flow / BPMN / Case |
| transform or compute, atomic | host-native first; a Coded Function only if extraction is justified |
| aggregate or persist shared data | **Data Fabric is storage, never an executor** |

3. **Choose the coordination host.** *"Case entity + stages + SLA → Case; formal gateways/events/subprocess without a case → BPMN; plain multi-automation pipeline → Flow. When Flow vs BPMN is genuinely close, default to Flow."* Case compiles to BPMN internally. **Never pick Maestro just to trigger a Dispatcher→Performer.**
4. **Choose packaging last.** *"Solution is packaging, not a runtime tool."*

Gating all of it, the **constraint gate**: a product unavailable on the delivery model is *blocked*, substituted, and recorded. *"User exclusions are blocks."* *"Never silently substitute."*

> **`[MEASURED]` The step-verb table only works if the PDD says which steps are deterministic** — see [`pdd-guide.md`](pdd-guide.md), §5.3. Without that column the choice falls to whatever the estate sweep found deployed nearby.

### What the SDD does NOT decide `[SKILL]`

| Deferred | Decided by |
|---|---|
| UI selectors, XPath | the RPA specialist, at build time |
| HITL field schema in Flow-hosted designs | the HITL specialist — the SDD passes business intent only |
| Coded App action schema | the coded-apps specialist, field by field |
| Agent typed models | the agents specialist |
| Data Fabric field schemas | the platform specialist, under a preview→apply gate |
| Connection ids, folder paths, identities | design-time grounding or build-time discovery |
| Connector payload schemas | the build phase |
| the implementation task list | Lane A |

## Stage 3 — the plan

A separate, cheap, regenerable stage most people collapse into implementation and shouldn't. One task per deliverable, each with a stable identity tuple, a status, `Blocked by` edges, an imperative skill prompt naming the exact SDD sections, concrete sub-steps and a mandatory `Validate:`.

```markdown
## Task T<N> — <skill> — <description>
**Identity:** `<skill>:<project>:<subject>`
**Status:** [ ] pending
**Blocked by:** <T1, T2 / none>
**Skill prompt:**
> <imperative, names exact SDD sections, ends with the anti-hallucination line>
- [ ] <concrete sub-step>
- [ ] **Validate:** <compile / build / lint / run>
```

**Routing, not redescription.** The plan says which skill and in what order, and is forbidden from describing specialist-internal flow, because that drifts. **Regenerate with preservation**: when the SDD changes, re-derive and match by identity, carrying completed work forward.

Quality rules: `Validate:` on every generation task · a testing task per generation skill before its deploy — a static gate where the artefact cannot run undeployed (a Maestro case, a Coded Action App) · leaves before consumers · routing, not redescription. The full schema is the planner's `references/plan-and-tasks-format.md`.

## Stage 4 — implement

**Dependencies before dependents.** Build leaf resources — models, functions, connectors, callable workflows, processes used as tools, data entities — then test each leaf, deploy leaves, build the orchestrator against published references, test, deploy, validate end to end.

Five rules that prevent rework `[SKILL]`:

1. **Leaves before consumers.** *"Never reference an unpublished resource by id."*
2. **Shared assets live at solution level**, built once, never duplicated per project.
3. **Testing before deploy, always.**
4. **Deploy is nobody's side job** — build skills do not deploy.
5. **One skill per artifact type, no cross-authoring.** The most common expensive mistake is a host skill hand-authoring something a specialist owns.

**Keep the provenance sidecar.** `[JUDGEMENT]` What was ambiguous, what was chosen, on what evidence. It is what lets a different person, weeks later, answer *"why does this task point at that connection?"* without re-running discovery.

## Stage 5 — verify, in three layers

1. **Structural** — each specialist's own validate/build. For RPA run **both** validate and build. For BPMN: *"validate once; fix only error-severity findings. Do not re-validate in a loop chasing warnings."*
2. **Functional** — `uipath-test`: requirements → cases → sets → executions → JUnit XML and a persona-scoped report.
3. **Conformance** — `uipath-review`: a PDD-alignment table, validation results, findings with rule ids, a derived grade.

`[JUDGEMENT]` Add a **spec-conformance task**, distinct from testing: enumerate every SDD element and mark it Implemented / Missing / Mismatch / **Extra**. *"Extra"* is the category the shipped tooling misses and the one that catches over-design.

> **`[MEASURED]` "Extra" is not hypothetical.** Two correct-shaped designs of one PDD were compared against it: one carried the five stage SLAs the PDD gave, the other carried eight, having invented deadlines for three stages the business never put one on. Nothing in the toolchain flagged it. An invented SLA escalates to somebody who never asked to be told.

## Stage 6 — ship

`init` → `projects add` → `resources refresh` → `pack` → `publish` → `deploy run` → `activate`. **Promotion is pack once, deploy many**: one package, then per environment set the tenant, publish, and deploy with that environment's config.


## The change loop

**Change enters at the document layer, never the artifact layer.** PDD if the business changed → SDD → re-derive tasks, preserving completed work by identity → execute the delta.

Classify each change. **Technology-driven** — the step now runs on extraction instead of manual entry; three steps collapse into one call → record in the SDD, no PDD change. **Business-process-driven** — a step disappears, a rule changes, scope moves, a new human decision appears, an SLA changes → **the PDD is re-baselined and re-signed**, because a business user signed the old one.

`[JUDGEMENT]` **Close the loop after the build.** Reverse-engineer the ideal PDD and SDD from the finished artifacts, diff against the originals, and use the result as the template for the next engagement. It also catches the standard failure mode, which is over-design.
