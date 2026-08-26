# Build — the agents

**Seven agents, one per `PDD.md` §7 section — `contracts/components.md` names them and what each owns.** Nothing else is built here: the deterministic work is already deployed as the six provided automations, or belongs in the case as a connector activity or an expression.

Use the **`uipath-agents`** skill for the Agents, and the skill your design's choice implies for the rest. All of it inside your one solution — a Maestro case binds only what lives alongside it.

What each one must decide is `PDD.md` §7, by rule id. Do not re-derive it and do not soften it: those rules are what the Verify block tests, one planted problem at a time.

Three things decide whether these are usable:

- **One concern, one owner.** A component may cite another's finding as evidence; it may never re-raise it as its own. A reviewer sees every finding at once, so the same problem reported three times reads as three problems.
- **A finding must be visible to whatever reports it.** Before writing any check, ask whether that data actually reaches that component at that point — not whether it is on the document somewhere. A component asked to confirm something absent from its own input can only report it missing, confidently and wrongly.
- **§7.9 is half the job.** It says what to leave alone. A build that only implements §7.1–§7.8 flags something on every claim, and then nothing can ever settle by itself.

**Done when** each one runs on a real claim and returns what §7 says it should — including on a claim with nothing wrong, where the right answer is that it found nothing.
