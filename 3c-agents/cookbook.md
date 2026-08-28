# Agents — what bites

| Issue | Fix |
|---|---|
| An input arrives empty at run time though it is declared | **An input the prompt never names does not arrive.** Declaring it is not enough — the prompt has to use it. |
| Output comes back shaped differently each run | The output schema is **validation, not a style guide**. Constrain it there rather than asking for a shape in the prose, and give every required field an invariant it can check itself against. |
| A tool is never called, or called with the wrong shape | A resource folder must be named after the resource, **spaces and all**. And tool parameter descriptions are read as literally as parameter names — a description naming a key that does not exist produces a call using that key. |
| `agent debug` cannot find the agent | It only finds one sitting **directly under the solution**. A nested layout packs and publishes fine and fails only here. |
| **You edit a prompt and nothing changes — every surface says it did** | `agent.json` stores the prompt **twice**. `messages[].content` is the readable copy; `messages[].contentTokens` is a parallel token array and **that is what reaches the model**. Edit `content` alone and the change is inert while `agent.json`, `entry-points.json` and even the trace's own `userPrompt` attribute all show the new text. Measured: six messages across four agents had diverged, one still being handed three inputs that no longer existed — it read them as empty, declared all its checks unusable, and returned an empty result on every claim. **That looks exactly like an agent hallucinating its inputs.** Edit both, or regenerate. |
| `agent debug` rejects your fixture | Inputs are capped **all together**, not each — and the usable budget measures **~8,700**, not 10,000. Trim the fixture, not the component. |
| A component is handed three record columns | Those two limits are different and they collide. A column holds 10,000; three do not fit in one input budget. **It will not refuse — it starts, reports Successful, and returns something empty**, which surfaces downstream as *unreadable*. Budget producers to 8,000, count what a consumer is handed, and sum the trace's `agentRun` start arguments before believing a green run. |
| You bind an output by the name you saw in `agent debug` and get nothing | `agent debug` **PascalCases every key it prints and drops the underscore** — `out_ClaimSummaryJSON` prints as `OutClaimSummaryJSON`, nested keys included — so the transform cannot be reversed by eye. Bind the names in `agent.json`; read the trace, never the debug print. |
| The skill says attachments cannot be passed through the CLI | They can — pass the **job-attachment object** a real job returned, whole, as the input: `{"ID": …, "FullName": "HO-41417123.pdf", "MimeType": "application/pdf", "Metadata": {}}` (from `out_PolicyPDF`), and `uip agent debug` runs Analyze Files on the real PDF. It is the only way to prove a component that reads a document. Two places in `uipath-agents` say otherwise; measured 2026-08-27, the skill is wrong. |
| A JSON payload arrives at a consumer unparseable | Its slice guard sat **below** the producer's budget and cut it mid-object — free text survives a cut, JSON does not (`contracts/claim-entity.md`, *Two budgets*). Guard ≥ budget, and order every envelope conclusion-first so a cut keeps the decisive part. |
| A grade of A and the component still violates the contract (coded agents; the low-code path has `validate`, a schema check that grades nothing) | Measured: seven components scored 99/A while four were missing two of their three required inputs. **A grade is a floor.** Read the schemas against what the design said they take. |
| Swapping the model changes behaviour | **A model change is a contract change** — it changes tool-call behaviour. Pin it per `CONFIG.md`, and if you change it, log it so it can be ruled out later. |
| Everything flags something on every claim | See below. This is the one that decides whether anything can ever settle. |

## Over-flagging is structural, not a wording problem

**Measured over fifteen clean claims: every one came back carrying some caution, and deleting the offending check did not help — the caution reappeared on the neighbouring check in the same component.** The behaviour is *one caution per analysis*, not a caution about a topic, so prompt wording alone will not get you to a silent clean claim.

**What fixes it is the routing, not the mood.** Scope the escalation conditions so a caution raised by one analysis is not read as another's concern — a settlement warning is not *"coverage is ambiguous"*. With that scoping, twelve of those fifteen settled unattended while still carrying a warning somewhere.

Build `PDD.md` §7.9 as carefully as §7.1–§7.8. It is the half that says what to leave alone — and **state each rule's application, not only the rule**: quoted verbatim, `BR-73` did not fire and a clean claim was denied on a corrosion exclusion; stated as the specific over-flag it exists to stop, the same claim approved. Measured 2026-08-27: a silent clean claim is reachable — nothing flagged anywhere, settled with no human.

## Test one before building the rest

They share a shape. Getting one right and then replicating costs an hour; getting seven wrong the same way costs a day.
