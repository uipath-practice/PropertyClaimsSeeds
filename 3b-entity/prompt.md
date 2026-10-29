# The claim record in Data Fabric

The PDD asks for a record of each claim that outlives any single step and can be read while the claim is in flight. Build it as a **Data Fabric entity** with the **`uipath-platform`** skill, in your seat folder.

The schema is `contracts/claim-entity.md` and it is **pinned**. Read why before you decide to improve a name.

Steps:
1. Create the entity with the full schema in one go.
2. Prove it holds what the build will write into it, then clean up after yourself.

**Done when** you have written a value with cents and a nine-thousand-character payload into it, read both back unchanged, and deleted the row you used.
