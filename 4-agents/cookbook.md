# Building the analysis agents — platform notes

Friction other builds met, and the commands that show you what is actually happening. Not a tutorial: it assumes
you can read the SDK and CLI docs and are stuck on something they do not mention.

## Skill, and the rules that are mechanics rather than judgement

**Skill.** `uipath-agents`.

Five constraints that come from the platform rather than from the claims process. Each one fails silently or
late, which is why they are here and not in the prompt:

- **No `maxLength`, `maxItems` or `minItems` in an output schema.** They are hard validation, not clamps: one
  over-long string faults the whole job and discards every other output the agent produced. `enum` and `required`
  are safe and worth using.
- **Budget each JSON payload at 8,000 characters, in the prompt text.** The column it lands in holds 10,000 and
  truncates past that silently; through the connector it is louder and worse — the whole case faults with
  `The provided value for field [<column>] is longer than length limit 10000`. Since the schema cannot enforce a
  length without faulting the agent, the prompt is the only place the limit can live.
- **Every declared input must appear in the prompt text.** An input the schema declares and the prompt never
  interpolates does not reach the model — see the next section, which is the most common silent failure here.
- **All three gateway inputs on all four post-gateway analyses** — the findings, the decision, and the reviewer's
  words. A grade will not catch a missing one.
- **Every payload name matches `contracts/claim-entity.md`.** One name, three casings; a better name breaks the
  mapping two blocks later.

## Proving each one

```bash
uip agent validate <project-dir> --output json   # all seven
uip agent review   <project-dir> --output json   # all seven — grade B or better, zero errors
uip agent debug    <project-dir> --output json   # the five that take no attachment
```

**Two of the seven cannot be run from the CLI at all.** `agent debug` has no mechanism for supplying a job
attachment, so the two document readers are validated and reviewed here and first *run* in block 5, on a real
job. That is a testing limitation, not your build being wrong — do not redesign the input to make a CLI run
possible.

## An input the prompt never names does not arrive

The symptom is distinctive and misleading: the model says the data is missing, and the job faults — while the
job's own record shows every value present.

```bash
uip or jobs get <job-key> --output json     # prints the real InputArguments the job received
```

If the arguments are there and the model says they are not, the prompt is not interpolating them. **Declaring an
input in the schema does not put it in front of the model**; only the prompt text does. Check the placeholder
form your platform expects — a near-miss resolves to nothing, silently, with no validation error and no empty
marker. Both forms typically pass the designer's own check.

## The output schema is validation, not a style guide

A length or item-count limit in an output schema is enforced hard: exceed it and the whole job faults rather than
retries. Budgets belong in the prompt, where the model can aim for them, and in whatever renders the result.

By contrast an `enum` on a required field is worth adding wherever a wrong value would produce plausible-looking
output — it turns a silent wrong answer into a loud startup failure that names the field and the permitted values.

## Tool parameter descriptions are read as literally as the parameter name

If a tool's parameter is described with something that looks like a key, the model will use it as one. A
description reading `in_PolicyFile` produced a call shaped `{"in_PolicyFile": [...]}` against a tool expecting
`attachments`, and every retry failed identically — the description is deterministic, so there is no run-to-run
luck to wait for. Write descriptions as sentences that name the parameter.

## Test one agent before building seven

They share a shape, so a mistake in the first is a mistake in all seven, and discovering it after publishing all
of them costs seven fixes and seven deploys.

```bash
uip agent debug <project-dir> --output json     # run it on one pinned input, no case, no deploy
uip agent review <project-dir> --output json    # deterministic checks + a letter grade
```

### `agent debug` only finds an agent that sits directly under the solution

Put the seven agent projects at the **top level** of `Build/ClaimCase-<seat>/`, one folder each. Group them in a
subfolder — `agents/Coverage`, the tidier-looking layout — and `uip agent debug` refuses with:

```
No enclosing .uipx solution found for 'agents/Coverage'.
Create one with 'uip solution init' and add the agent to it.
```

The message is wrong about the cause: the solution exists, the manifest declares the nested path correctly, and
`agent validate`, `agent review` and `solution pack` all accept it. Only `debug` searches a single level up.
Two of three builds hit this and one lost an hour re-registering projects; measured on `1.199.0-preview.119`.

### `agent debug` caps all its inputs at 10,000 characters *together*

```
The field InputArguments must be a string or array type with a maximum length of 10000
```

This is the whole serialized input of the debug job, not one field, so it bites the agents that read four or
five payloads at once — the decision analysis first. It is rejected before the model is invoked, so it costs
nothing but tells you nothing either. Trim the *fixture's* prose to get under it; do not change the agent's own
per-payload budget to suit a test harness, and do not conclude the agent is too big.

There is also no `--inputs-file`: the JSON goes on the command line, and on Windows that runs into the command
length limit and into PowerShell rewriting the quoting. Pass it from a small script (`subprocess` with an argv
list) rather than from a shell variable.

`agent review` is the cheapest quality signal in this build: it is free, it is objective, and it returns the same
answer for everyone, which makes it worth running before you think you are finished rather than after.

## A model change is a contract change

The same agent, same prompts, same schema, ran cleanly on one model and failed on its first tool call under
another. Nothing was wrong with the newer model — it read an ambiguous schema more literally. **Re-run one claim
end to end after any model change**, and expect tool-call shape to be what moves.

## What the model sees is not what the document says

Where a document reaches an agent as extracted fields, anything the extraction does not capture is invisible to
it — even when a human looking at the PDF can see it plainly. An agent asked about such a thing will report it
missing, on a document that has it, and a reviewer who reads two of those learns to skim every caveat you write.

The distinction that matters: an agent given a **document** (as an attachment) can see the whole page; an agent
given **extracted JSON** sees only what was extracted. Check which one each agent gets before writing a check
about anything structural.
