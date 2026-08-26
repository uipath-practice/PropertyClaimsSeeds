# Agents — what bites

| Issue | Fix |
|---|---|
| An input arrives empty at run time though it is declared | **An input the prompt never names does not arrive.** Declaring it is not enough — the prompt has to use it. |
| Output comes back shaped differently each run | The output schema is **validation, not a style guide**. Constrain it there rather than asking for a shape in the prose, and give every required field an invariant it can check itself against. |
| A tool is never called, or called with the wrong shape | A resource folder must be named after the resource, **spaces and all**. And tool parameter descriptions are read as literally as parameter names — a description naming a key that does not exist produces a call using that key. |
| `agent debug` cannot find the agent | It only finds one sitting **directly under the solution**. A nested layout packs and publishes fine and fails only here. |
| `agent debug` rejects your fixture | Inputs are capped **all together**, not each — and the usable budget measures **~8,700**, not the documented 10,000. Trim the fixture, not the component. |
| A component takes three record columns and will not start | Those two limits are different and they collide. A column holds 10,000; three of them do not fit in one input budget. **Budget producers to 8,000 and count what a consumer is handed.** |
| You bind an output by the name you saw in `agent debug` and get nothing | `agent debug` **PascalCases every key it prints**, nested ones included. Binding from that output binds a name the component never emits, silently. Read the trace instead. |
| The skill says attachments cannot be passed through the CLI | They can, and it is the only way to prove a component that reads a document. Two places in the skill say otherwise; the skill is wrong. |
| A grade of A and the component still violates the contract | Measured: seven components scored 99/A while four were missing two of their three required inputs. **A grade is a floor.** Read the schemas against what the design said they take. |
| Swapping the model changes behaviour | **A model change is a contract change** — it changes tool-call behaviour. Pin it per `CONFIG.md`, and if you change it, log it so it can be ruled out later. |
| Everything flags something on every claim | See below. This is the one that decides whether anything can ever settle. |

## Over-flagging is structural, not a wording problem

**Measured over fifteen clean claims: every one came back carrying some caution, and deleting the offending check did not help — the caution reappeared on the neighbouring check in the same component.** The behaviour is *one caution per analysis*, not a caution about a topic, so prompt wording alone will not get you to a silent clean claim.

**What fixes it is the routing, not the mood.** Scope the escalation conditions so a caution raised by one analysis is not read as another's concern — a settlement warning is not *"coverage is ambiguous"*. With that scoping, twelve of those fifteen settled unattended while still carrying a warning somewhere.

Build `PDD.md` §7.9 as carefully as §7.1–§7.8. It is the half that says what to leave alone.

## Test one before building the rest

They share a shape. Getting one right and then replicating costs an hour; getting seven wrong the same way costs a day.
