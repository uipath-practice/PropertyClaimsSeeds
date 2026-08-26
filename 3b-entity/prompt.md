# Build — the claim entity

`PDD.md` §1.5 P5 asks for a store that outlives any single step and can be read while the claim is in flight. Build it.

The schema is [`contracts/claim-entity.md`](../contracts/claim-entity.md) and it is **pinned** — that file says why, and it is worth reading before you decide to improve a name.

Use the **`uipath-platform`** skill — Data Fabric lives there rather than in a skill of its own. It goes in **your seat folder**, not at tenant level, and the connection already exists — `CONFIG.md`, *The claim entity*.

**Get the schema right in one create.** Update takes a different body shape from the one `get` returns, so the natural read-edit-write loop does not work; creating fresh from a file is one call and no repair.

**Done when** you have written a value with cents and a nine-thousand-character payload into it, read both back unchanged, and deleted the row you used. That round trip is the only thing separating a correct set of limits from a plausible-looking one — both failure modes are silent and neither errors on create.
