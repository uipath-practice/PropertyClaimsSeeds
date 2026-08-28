# Plan — what bites

**Thin on purpose.** Few builds have been through this step, so most of what is here came from two runs rather than ten. Add to it.

| Issue | Fix |
|---|---|
| The skill wants to emit live task-tracking calls and your runtime has no such tool | Expected in any runtime — Claude Code included, measured — the six harness tools the skill declares (`TaskCreate`, `TaskUpdate`, `TaskList`…) may simply not exist. It degrades cleanly: **`tasks.md` is the artifact**, the live calls never were; keep its `Status:` boxes current by editing the file. Record that it happened. |
| Task derivation refuses to start | It reads `Status: ready` from the design's handoff header and refuses a `draft`. Check the header before assuming the file is wrong. |
| Design and planning are asked for in one go and only the design appears | The design write is a deliberate turn boundary. Ask again to continue. |
| Tasks describe *how* a specialist works, not just which one | Cut it. Routing only — specialist-internal detail drifts, and then two documents disagree about the same thing. |
