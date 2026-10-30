# The Data Fabric entity

## How it is built here

- `uipath-platform`'s Data Fabric section owns `uip df`. The entity is **folder-scoped, in your seat folder**, never tenant level (`CONFIG.md`, *The claim entity*).
- From `contracts/claim-entity.md` read the five column tables and the casing rule; the rest of that file is for `3d`.
- **One create, from a file**, with `lengthLimit` set on every **text** column: one call and no repair. Other types refuse it.

## What bites

| Issue | Fix |
|---|---|
| A long-text column created without `lengthLimit` holds 200 characters | `MULTILINE_TEXT` defaults to 200 and nothing errors on create — only the first longer write, refused with the column named. Set `lengthLimit` on every text column explicitly, from `contracts/claim-entity.md`. |
| `entities get` shows limits you never set | `LengthLimit` 1000 on `DATE`, `DATETIME_WITH_TZ` and `DECIMAL`, 100 on `BOOLEAN`, `MaxValue` 1000000000000 on `DECIMAL` — platform defaults, not drift; leave them. The system fields are listed in the skill's `entity-schema.md`. |
| A record read is missing columns | `records list` and `records get` return the same keys: the columns the row has been written, plus the six system fields. **A column never written is absent, not `null`** — read absent and empty alike. |
