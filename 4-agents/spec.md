# The analysis agents — what to build

Seven analyses read the claim and report what they found. None of them decides the claim; `pdd.md` §4 says why.
This document says what each one is for and what shape its answer takes. **The prompts are yours to write** —
that is the exercise.

## The set

`pdd.md` §5 defines the work; this is the split into buildable units. One analysis per agent, because a reviewer
sees them side by side and one concern reported three times reads as three problems.

| # | Agent | Answers | Reads |
|---|---|---|---|
| 1 | **Eligibility** | Should this claim be investigated at all? Five fixed checks (§5.1) | claim, policy |
| 2 | **Report validation** | Is the assessor's report usable, and what does it say in structured form? (§5.5) | the report **as a document**, plus claim and policy |
| 3 | **Coverage** | Does the policy respond to this loss? (§5.2) | claim, policy, structured assessment |
| 4 | **Payout** | What is payable, and how was it reduced? (§5.3) | claim, policy, structured assessment, prior claims |
| 5 | **Credibility** | Does the claimant's account hold together? (§5.4) | claim, policy, structured assessment, prior claims |
| 6 | **Decision** | Which outcome do the rules recommend? (§5.6) | all four analyses |
| 7 | **Response** | The letter to the claimant (§7) | the decision, the analyses, the reviewer's words |

**Response is the one agent whose output a customer reads, and it has two failure modes the others do not.**

- **It must work when the analyses are missing.** A claim denied at either gateway skips everything downstream,
  so Response is asked for a denial letter with no coverage, payout or credibility to draw on. That is the normal
  denial path, not a broken input: the human's decision and their written reason are sufficient, and are what the
  letter is built from. An agent that treats their absence as an error fails every denial.
- **The letter is in English, always.** Claimant names and addresses in this data are Romanian, and an agent
  left to infer will write the letter in Romanian while its own summary stays English. Nothing downstream reads
  the letter, so nothing catches it.

And the rule underneath both: **if it cannot write the letter, it must fail where the process looks** — never
produce fluent prose whose content is an apology for having no inputs. That reaches the claimant.

Agents 3, 4 and 5 run **in parallel** and none reads another's output. Agent 2 runs before them and produces the
structured assessment all three consume: one reader of the document, three consumers of the data.

## The answer shape — pinned

The **six analytical agents** return the same envelope; **Response returns the response record instead**, because
what it produces is a letter rather than a set of checks (`contracts/check-envelope.md` exempts it by name).
**This is a contract, not a convention** — it is what lets one prompt shape generate all
seven, and one screen render any of them.

Four rules inside it that are easy to get wrong and expensive to discover late:

- **Report every check, passes included.** A screen showing only failures reads as a broken form. A failure sets
  the overall result; it does not stop the analysis.
- **A check whose data was unavailable is a warning, never a silent pass.** Aim for two or three genuine failures
  on a claim that has problems, and mark anything merely questionable as a warning.
- **Never put `maxLength` or `maxItems` in an output schema.** They are hard validation rather than clamps: one
  over-long string faults the whole job. Ask for a length in the prompt so the model aims for it, and clamp when
  rendering. `enum` and `required` are safe and worth using.
- **Budget each JSON payload at 8,000 characters, and say so in the prompt.** The column it lands in holds
  10,000, and **going past it faults the whole claim at the write** (`contracts/claim-entity.md`). Since the schema
  cannot enforce a length without faulting the job, the prompt is the only place the limit can live — so give
  the model a number, tell it what to leave out, and check the result rather than trusting it.

### A typed output field beats a paragraph of prompt

The most transferable thing measured in this whole exercise, and it is not obvious.

Two analyses were failing the same way: each **reasoned correctly**, wrote the discrepancy into its own prose,
and then left the check on `pass`. Three rounds of increasingly emphatic prompt wording moved neither. What
moved both, first try, was declaring the comparison as **data in the output schema**:

```jsonc
"peril":     { "claimedType": "…", "assessedType": "…", "sameEvent": true },
"aggregate": { "priorClaims": [ … ], "annualAggregate": 0, "remaining": 0 }
```

A model fills a declared field reliably, and will then reason from what it has written. Prose asking it to be
careful competes with everything else in the prompt; a field it must populate does not.

**But the field alone is not enough, and the counter-example is the instructive half.** The same build declared
a `causeStatement` field on the letter and got three empty strings, because the field's *description* gave a
rationale — a reason the fact was worth including — and left the agent free to decide it did not apply. What
made the two analysis fixes stick was the field **plus a mechanical rule tying an output to it**:

> `sameEvent: false` **means** this check is not `pass`. If you wrote one and reported the other, you have
> contradicted yourself.

So the rule for the seed, and for you: **when a payload must contain a fact, declare the field *and* state an
invariant over the agent's own output.** Not a reason to include it — a contradiction it can check itself
against. "Include the prior claim's identifier because a reviewer needs it" is a rationale and will be skipped;
"if `aggregate.priorClaims` is empty you may not report an aggregate reduction" is an invariant and will not.

### Tell it what is *not* a finding

`pdd.md` §5.7 is a list of things that look like problems and are not: an assessor's incidental observation, a
sublimit doing its job, a claimant misremembering a time of day. It exists because one build escalated **nine
clean claims in a row**, each for a defensible reason.

**Those rules only work if they are in the prompt.** The model never reads `pdd.md`; at run time it sees the
prompt and the inputs and nothing else. So every analysis carries its own paragraph of §5.7 — the ones that
belong to it — written as *do not flag X* rather than as a general plea for judgement. Generic prose asking an
agent to be reasonable does not survive contact with a real claim; two builds proved it, and the wording that
worked named the exact thing not to report.

### Say what to leave out, not just what to include

Two payloads overshoot the budget when nobody asks them not to: the **structured policy** and the **coverage
findings**, measured at 10.9 KB and 9.0 KB on a single claim. Both carry material no later step reads.

The rule that keeps them small is not "be brief" — a model asked to be brief drops the wrong things. It is
*name what the payload is for*: the policy blob exists so later analyses can check cover, limits, exclusions and
deductibles, so it carries those and not the full text of every clause. State the purpose, state the budget, and
the model edits sensibly. Leave either out and it writes an essay.

## Documents reach an agent as attachments, not as text

Two analyses read a source document rather than extracted fields: eligibility reads the **policy**, and report
validation reads the **assessor's report**. Both arrive as **job attachments** — the file itself, passed by
reference. The two inputs are named `in_PolicyPDF` and `in_AssessorReportPDF`; they are bound by name in block 5
like everything else, so they are not yours to rephrase.

**An attachment input does not put the document in front of the model.** Interpolating `{{in_PolicyPDF}}` renders
the attachment's *metadata* — file name, MIME type, storage key — and nothing else. An agent built with the
attachment declared and interpolated therefore sees a filename, reports the policy unreadable, and fails most of
its checks: the seed's own *tell it what does not exist* failure, arrived at by following the design.

So each of these two agents needs **a built-in attachment-reading tool as a declared resource**, and its prompt
must *call* the tool and say what to ask the document for. On the UiPath low-code agent that tool is
`analyze-attachments`, and it is the only way to reach the contents at run time; `4-agents/cookbook.md` has the
resource shape and the one trap in creating it. Ask for the exclusion and coverage clauses **verbatim**, because
`pdd.md` §5.2 requires quoting the sentence relied on and a paraphrase cannot be quoted.

This is deliberate, and it is the reason extraction does not cover these two. A policy is long unstructured prose
whose meaning lives in the exclusion and coverage clauses; two insurers write them completely differently. Sending
it through extraction would flatten the wording an analysis has to quote, and `pdd.md` §5.2 requires quoting the
exact sentence. Passing the file is both simpler and more faithful.

**The cost is a testing limitation, and it is real: `uip agent debug` cannot supply an attachment.** There is no
mechanism for it, and no grade or validation notices a document reader that cannot read. So those two agents cannot be exercised from the CLI at all — they are validated and reviewed
here, and first *run* in block 5, on a real job. Their `Done when` differs from the other five for that reason,
and nothing about it is your build being wrong.

## Two claim payloads, two names

The eligibility analysis is the only agent that reads the **extraction** output. It takes
`in_ClaimIXPDataJSON` — the raw six-group payload from block 1, shaped by the taxonomy — and emits
`out_ClaimDataJSON`, the claim reorganised for everyone downstream. Every later analysis takes
`in_ClaimDataJSON`, meaning that second, structured payload.

Using one name for both is the mistake to avoid: a case variable holds one shape at a time, so an agent whose
input and output share a name is reading the variable it is about to overwrite. The same holds for
`out_PolicyDataJSON` and `out_AssessmentReportJSON` — each is *produced* by the analysis that reads the source
document, and consumed by name thereafter.

## Inputs: name every one in the prompt

An input that the prompt does not interpolate **does not reach the model**, however correctly the schema declares
it. The model then reports the data as missing — on data that was supplied — and the job usually faults. This is
the single most common way an agent build fails silently, so treat it as a rule: every declared input appears in
the prompt text.

Where your agent platform uses a placeholder syntax, check the exact form it expects. A near-miss resolves to
nothing rather than erroring.

## What crosses a human gateway

After eligibility screening, every downstream analysis receives **three** things, and they are three *declared
inputs*, not a paragraph in the prompt:

| Input | Carries |
|---|---|
| `in_EligibilityChecksJSON` | what the eligibility analysis found |
| `in_EligibilityDecision` | what the human decided, **or that no human was asked** |
| `in_EligibilityNotes` | why, in the human's own words |

All three, on all four downstream analyses. `pdd.md` §6 has the reading rule, and it belongs in each of those
prompts. An agent that re-raises a finding the reviewer already accepted asks a human to decide the same thing
twice; an agent that never sees the decision cannot avoid doing so.

**On a clean claim the gateway never opens, so two of the three arrive empty** (`pdd.md` §4). Do not leave them
blank and hope: give `in_EligibilityDecision` an explicit value meaning *screening passed, nobody was asked*, and
tell the prompt what it means. A blank decision reads to a model as a reviewer who accepted everything, which is
the opposite of the truth — nothing was accepted, because nothing was raised. Both inputs stay **required**;
what changes is the value, never its presence.

**This is the rule a passing grade will not catch.** Agent review scores structure and prompt quality — schema
shape, whether inputs are interpolated, whether the wording is clear. It does not know what this pipeline is, so
it cannot tell that an analysis is missing two of its three gateway inputs. Check this one by reading the
schemas.

## Tell it what does not exist

Two failure modes, both of which produce confident, wrong output rather than an error:

- **A field the pipeline never produces.** An agent asked to confirm something absent from its own input can only
  report it missing. Before writing any check, ask: *can this agent actually see the thing?* — not "is it on the
  document", but "is it in the payload that reaches this agent, at this stage".
- **A field that used to exist.** A prompt branching on a path the payload no longer carries does not error — the
  model falls through to whatever *is* there and writes something plausible. One claim was approved, recorded as
  approved, and sent a letter saying it "remains under specialist review". Every field was right except the
  sentence the human read. When a rule depends on a field, say in the prompt which fields exist.

## Done when

- **The five agents that take no attachment** validate and run against one pinned input, returning the envelope
  shape with no schema error.
- **The two that read a document** — eligibility and report validation — validate and review, and are proven on a
  real job in block 5. `uip agent debug` cannot supply an attachment, so there is no CLI run to be had; do not
  redesign the input to make one possible.
- The eligibility agent reports **five** checks on a claim with nothing wrong, all passing.
- A claim with a planted problem produces a failing check **in the agent that owns it** (`7-testing/spec.md`), and the
  wording names the actual problem rather than its category.
- Your agent review tooling reports no errors — `uip agent review <dir> --output json` returns a grade; treat
  anything below a B as unfinished work rather than a style note.
