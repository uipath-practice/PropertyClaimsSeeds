# Build — the claim entity in Data Fabric

`PDD.md` §1.5 P5 asks for a store that outlives any single step and can be read while the claim is in flight. That is a **Data Fabric entity**; build it.

The schema is `contracts/claim-entity.md` and it is **pinned** — that file says why, and it is worth reading before you decide to improve a name.

Use the **`uipath-platform`** skill — its Data Fabric section owns `uip df`. The entity goes in **your seat folder**, not at tenant level — `CONFIG.md`, *The claim entity*. Read the contract's five column tables and its casing rule; the rest of that file is for the block that writes the entity (`3d`).

**Get the schema right in one create.** Update takes a different body shape from the one `get` returns, so the natural read-edit-write loop does not work; creating fresh from a file is one call and no repair.

**Done when** you have written a value with cents and a nine-thousand-character payload into it, read both back unchanged, and deleted the row you used. That round trip validates correct set of limits.
