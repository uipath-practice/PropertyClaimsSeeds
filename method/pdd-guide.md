# Writing a PDD

`MUST` = the design stage cannot proceed correctly without it. `SHOULD` = its absence becomes a recorded assumption somebody confirms later.

**Two hard boundaries.** The PDD describes the **business, not the platform**. And it is **signed by business users**, so every material fact needs provenance — verbatim, derived, or assumed.

## Section map

| § | Section | Level | What goes in |
|---|---|---|---|
| — | Document control · sign-off · key contacts | MUST | version, history saying *what* changed, who signs and what signing means, and only roles actually named |
| — | Glossary & operational vocabulary | SHOULD | domain nouns, role titles, decision-outcome labels and system names in the customer's **exact words and casing** |
| — | Authoritative references | SHOULD | sources and regulations, each tagged statutory / supervisory / industry practice / internal policy |
| 1.1 | Purpose | — | one paragraph: what decision this document supports |
| 1.2 | Objective & target outcome | MUST | the outcome **and the KPI it moves** |
| 1.3 | Success criteria | MUST | numeric. These become the UAT acceptance criteria |
| 1.4 | Business case | SHOULD | volume × time × cost, expected saving — input to the economics gate |
| 1.5 | Minimum prerequisites | SHOULD | licences, access, test data, credentials |
| 2.1 | Process profile | MUST | one table, fields below |
| 2.2 | In scope | MUST | enumerated, not prose |
| 2.3 | Out of scope | MUST | with a reason per row. **Strictly enforced — nothing here may appear in the design's inventory** |
| 2.4 | Assumptions & constraints | MUST | business, organisational, timing |
| 3 | Personas & responsibilities | MUST | role, what they do, which steps, **decision authority with numeric thresholds**, touch volume, what they must see |
| 4.1–4.2 | As-is narrative & map | MUST | **never skip** — skipping pushes cost to UAT scope-creep |
| 4.3 | Applications used today | MUST | interface type, access method, auth, quirks |
| 4.4 | Pain points & workarounds | MUST | **label steps that exist only because a human does the work** — they are meant to disappear |
| 4.5 | Volumetrics by step | SHOULD | where the time actually goes |
| 5.1–5.2 | To-be narrative & map | MUST | what changes, what a human still does, and a numbered step list matching the diagram. **Keep step numbers stable** |
| 5.3 | Detailed step table | MUST | the most load-bearing table in the document |
| 5.4 | Control-flow structure | MUST when present | **decides the coordination host.** Absent structure must not be inferred |
| 5.5 | Lifecycle, stages & SLAs | MUST for case work | stages in order with owner, done-condition and required-for-completion; which are interrupting; SLAs at work-item **and** stage level with at-risk and breach behaviour; **every exit path** |
| 5.6 | Documents & unstructured input | MUST when docs | per type: arrival, structure class, fields to read, human confirmation, layout variability, change frequency, **storage location — never assumed** |
| 5.7 | Human decision & approval points | MUST | who decides, what they see, what they may change, **every outcome named**, what each causes, delegation, and no-action-within-SLA. **Business intent, not a form spec** |
| 6.1–6.2 | Data objects & fields | MUST | business entities and their business meaning. **Stop at business meaning** |
| 6.3 | Value mappings | MUST where they exist | full source→target tables, never "map appropriately" |
| 6.4 | Retention, privacy, residency | SHOULD | periods, masking, no-log fields, residency limits |
| 7 | Business rules | MUST | `BR-nn`, one row each |
| 8.1–8.3 | Exceptions | MUST | `B-nn` with detection, action, notification, can-continue. **Keep the catch-all row.** Name who owns an unclassified failure |
| 8.4 | Reversibility & risk | SHOULD | irreversible steps — these get a human gate regardless of confidence |
| 9 | Integrations | MUST | per system: role, direction, **API vs UI-only**, **cloud-reachable vs on-prem**, owner. Inbound events need a **correlation key** |
| 10 | Compliance & controls | MUST where applicable | requirement, source, steps constrained, evidence, auditor |
| 11 | Reporting & monitoring | SHOULD | reports, and what is needed **in flight** — queue, SLA dashboard, ageing view |
| 12 | Variants & regional forks | SHOULD | the questions that change process shape. Keep §5 neutral |
| 13 | Test data & canonical examples | MUST | ≥1 complete canonical case, plus one example per rule and exception path |
| 14 | Out of scope for automation | MUST | steps staying manual, with category and reason |
| 15 | Change control | MUST | date, change, sections, reason, raised by, impact class |

## §2.1 — the process profile fields

Process full name (**verbatim** if the business has a canonical one) · function · short description · criticality and regulatory flag · **trigger — who or what starts it, and how it arrives** · frequency and business hours · volume, range and peak · average handling time today and target · FTE · exception rate · input data · output data · data sensitivity and **anything that must not reach logs** · **delivery model** · products the client rules out, and why.

## §5.3 — the step table, and the one column that decides everything

`Step | Action (business verb) | Actor | System/data touched | Decision nature | Expected result | Remarks`

- **Action** — a fixed verb set, so each step can be placed on an executor: *collect · validate · decide · transform · create · transfer · notify · wait · assign · review · escalate · schedule · archive*. Two or three components max; five means five steps.
- **Actor** — a human role, or **system**. Never *robot* or *agent* — that is a design decision.
- **Decision nature** — MUST wherever a decision exists. **Rule-expressible** (state the rule) versus **requires judgement over ambiguity** (state what is being weighed).
- **Expected result** — what is true after success. It becomes a test assertion.
- **Remarks** — lift buried business rules out into §7 rather than leaving them here.

> **`[MEASURED]` Decision nature is what lets a PDD drive an architecture instead of merely describing a process.** Given a step table carrying it, two independent designs on different models each chose agents against deterministic runners **by citing the column, step by step**, and each rejected five or six plausible alternative architectures against a named section. Given a PDD without it, the same choice falls to whatever the estate sweep happened to find deployed nearby.
>
> It costs one column and it is the highest-leverage thing in the document.

## §5.4 — control-flow structure

The subsection that decides the coordination host. Answer each **Yes/No with where and what exactly happens**, and write *No* where it does not occur — **absent structure must not be inferred**:

parallel work that forks and rejoins · wait on an external event · wait on a clock · per-step deadline or timeout · cancel or compensate on failure · a reusable group of steps · handoff to a separate long-running process · batch versus item-by-item.

Then say whether **state outlives a single run**. That question, plus multiple human touchpoints and per-step SLAs, is what separates a case lifecycle from a pipeline.

## §7 — business rules

`ID | Rule | Applies at step | Inputs it reads | Outcome | Source/authority | Example (input → expected output)`

Express as `When <event>, if <condition>, then <outcome>`. **Give a worked example per rule** — concrete values anywhere in a PDD are treated as **fact, not assumption**, and become real test oracles. State thresholds numerically with the comparator, next to the role or action they gate. Separate policy rules from regulatory ones. **If a "rule" needs judgement, move it to §5.3 and say so.**

## Keep out of the PDD

| Out | Belongs in |
|---|---|
| product or technology selection | the SDD's recommended scope |
| agent type, memory design, multi-agent coordination | the SDD |
| system and user prompt text | the SDD |
| selectors, XPath, coordinates, UI layout | nowhere — determined against the live application at build time |
| field schemas, entity relationships | the SDD data model |
| connection ids, folder paths, resource identities | the SDD, as *intent* |
| queue item schemas, workflow inventories | the SDD |
| folder structure, machine templates, asset values | the SDD's deployment section |

**Screenshots:** extract application name, screen name, field and button labels, navigation, and **concrete data values**. Do not extract selectors, coordinates, colours or layout. Supply raster images — vector figures pasted from office documents cannot be read, and everything derived from them becomes a review item.

## Pre-sign-off checklist

- [ ] §1.2 names the KPI; §1.3 criteria are numeric
- [ ] §2.3 out of scope explicit, with reasons
- [ ] §5.3 every step has an actor; **every decision has a stated decision nature**
- [ ] §5.4 control-flow named concretely, or explicitly marked absent
- [ ] §5.5 stages, owners, SLAs at both levels, at-risk and breach behaviour, and every exit path
- [ ] §5.7 every human touchpoint: all outcomes named, no-action behaviour defined
- [ ] §7 every rule numbered, testable, carrying a worked example
- [ ] every threshold numeric, with its comparator, next to the role it gates
- [ ] §6.3 value mappings complete
- [ ] §8 exceptions numbered with detection and action, and a catch-all row
- [ ] §8.4 irreversible steps flagged
- [ ] §9 per system: API or UI-only, cloud-reachable or on-prem, owner; inbound events have a correlation key
- [ ] §5.6 document storage stated, not assumed
- [ ] §2.1 delivery model and product exclusions stated
- [ ] §13 one complete canonical case with concrete inputs and expected outputs
- [ ] §11 reporting requirements captured — including what is needed in flight
- [ ] every material fact traceable to a source, or marked as an assumption
- [ ] **no product selection, prompts, selectors, schemas or connection details anywhere**

**That last box is worth checking mechanically**, not by eye. A scan for product and platform nouns across the finished document costs seconds and catches the sentence that drifted.
