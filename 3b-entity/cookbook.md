# The Data Fabric entity — what bites

| Issue | Fix |
|---|---|
| A long-text column created without `lengthLimit` holds 200 characters | `MULTILINE_TEXT` defaults to 200 and nothing errors on create — only the first longer write, refused with the column named. Set `lengthLimit` on every column explicitly, from `contracts/claim-entity.md`. |
| `entities get` shows limits you never set | `LengthLimit` 1000 on `DATE`, `DATETIME_WITH_TZ` and `DECIMAL`, 100 on `BOOLEAN`, `MaxValue` 1000000000000 on `DECIMAL` — platform defaults, not drift; leave them. The system fields are listed in the skill's `entity-schema.md`. |
| A record read is missing columns | `records list` and `records get` return the same keys: the columns the row has been written, plus the six system fields. **A column never written is absent, not `null`** — read absent and empty alike. |
