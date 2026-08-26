# Checkpoints

A working version of a block's output. **Restore one and carry on** — `AGENTS.md` says when that is the right call and what to log about it.

| Block | What is here |
|---|---|
| [`1-design/`](1-design/) | a complete `sdd.md` that passes the gate |
| `3b-entity/` | `entity.json` — the pinned schema, ready to create |

**There is no checkpoint for the analyses, deliberately.** The obvious candidates are the components from an earlier version of this exercise, and they were built to a **different architecture** — two of them do work this design puts on deterministic runners, and one does the job this design splits across three. Shipping them would hand you the exact defect `1-design/check_sdd.py` exists to catch. One built to this design is owed.
