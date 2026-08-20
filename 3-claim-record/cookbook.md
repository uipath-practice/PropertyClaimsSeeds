# Block 3 — getting the claim record built

Friction from real builds. The spec is `contracts/claim-entity.md`; this is how to get it onto the platform.

## The JSON columns are `MULTILINE_TEXT`, and the limit is real

A larger field type (`MULTILINE_MAX`, 128 KB) exists but is in private preview and gated per tenant. If you try
it you get a clean early error:

```
Cannot create MULTILINE_MAX field 'claimDataJson': the Multi-line (Max) feature is not enabled for this tenant.
```

**Use `MULTILINE_TEXT` with `lengthLimit: 10000` and move on.** That is the design as it stands
(`contracts/claim-entity.md`), and 10,000 is the type's hard maximum — a `lengthLimit` of 50000 or 131072 is
rejected outright, with the allowed range in the message.

What matters is what happens *past* the limit: the write succeeds and the content is cut, silently. So the
budget belongs upstream, in the agent prompts you write in block 4 — aim each payload at **8,000 characters** —
and the check belongs in block 7, where a column whose length is exactly 10,000 is a truncated column.

**A `MULTILINE_TEXT` column with no `lengthLimit` defaults to 200 characters.** Same silent truncation, fifty
times worse. Set it explicitly on every one.

**`STRING` does the same thing, and it is easier to miss** because 200 characters looks generous until the value
is a person's reasoning. `contracts/claim-entity.md` gives minimums for the five columns where it matters; the
two reviewer-notes columns are the ones that hurt. Three builds guessed three different answers here, and two
of them cut an adjuster's notes at 200 without reporting anything.

## Create the entity in your seat folder

Data Fabric entities can live at tenant level or in an Orchestrator folder. **Yours goes in your seat folder**,
which means one extra flag and one changed failure mode:

```bash
FK=$(uip or folders list --all --name ClaimCase-<NN> --output json --output-filter "[0].Key")
uip df entities create ClaimCase_<NN> --file <schema>.json --folder-key $FK --output json
uip df entities list --native-only --folder-key $FK --output json      # confirm
```

Without `--folder-key` the create is refused:

```
You don't have permission to access the entity, field or record or you are using an unsupported robot type.
```

That message describes neither the scope nor the fix. It is not a login problem and not a role problem — it is
the tenant-level create you were never entitled to make. Add the flag.

**Every later `df` command needs the same flag.** `entities list`, `entities get`, `records query` — a
folder-scoped entity is invisible to the tenant-scoped form of the same command, which returns success and an
empty list. An empty list here means *wrong scope*, not *missing entity*.

**The one consequence to carry forward:** in block 5 the case writes to this entity through the Data Fabric
connector, and the connector's default activities resolve entity names **at tenant level only**. They will not
find yours. `5-case/cookbook.md` has the six-line fix; know now that it exists, so the runtime error
`Entity 'ClaimCase_<NN>' not found at tenant level` reads as expected rather than as a broken entity.

## The Data Fabric connection is shared — find it, do not create it

One connection serves every seat, in the `Shared` folder:

```bash
uip is connections list uipath-uipath-dataservice --refresh --all-folders --output json
uip is connections ping <connection-id> --output json      # expect Enabled
```

**Use exactly that first command.** A bare `uip is connections list` reports *"No connections found for any
connector"* while the connection exists and works — it does not look past its default folder scope or its cache.
The CLI's own `Instructions` field suggests the bare form, so the natural next step is a message saying nothing
is there. Add `--refresh --all-folders` before concluding anything failed.

Do not create your own. A connection needs an interactive OAuth consent that a coding agent cannot complete, and
a second connection in a personal workspace produces `Missing instance <n> for user <n>` at run time in block 5,
with nothing in the message pointing back to here.

There is no `uip is connections get`. Inspect a connection with the `list` form above.

## Naming: the entity is the one place the hyphen is illegal

Everything else you create is `ClaimCase-<NN>` — folder, solution, packages, build directory (`CONFIG.md`,
*One name, everywhere*). Entity names take **letters, digits and underscores only, and must start with a
letter**, so this one is `ClaimCase_07`. Not `ClaimCase-07`, which is rejected, and not `ClaimCase07`, which is
accepted and then reads as somebody else's convention for the rest of the build.

Your folder scopes the name, so a collision with another seat is not the risk it would be at tenant level — but
keep the seat token anyway. It is what makes a row, a log line or a runtime error attributable to you.

If you find entities from an earlier attempt at this use case — a normalised model with names like `Claim`,
`Policy`, `DamagedItem` — **leave them alone** and do not bind to them by accident. They are not this design,
and the tenant is shared. On a clean tenant you will see only `SystemUser`, which is Data Fabric's own.

## The types you actually need

`entities create --help` documents the exotic types (`CHOICE_SET_*`, `RELATIONSHIP`, `FILE`, `MULTILINE_MAX`)
and none of the ordinary ones. This entity needs six:

| Type | For | Note |
|---|---|---|
| `STRING` | names, ids, decisions, notes | `isRequired` / `isUnique` are the flags on the key |
| `MULTILINE_TEXT` | every JSON payload | **always** set `lengthLimit: 10000` |
| `DECIMAL` | amounts | never `FLOAT` or `DOUBLE` — see below |
| `DATE` | calendar dates (`…Date`) | |
| `DATETIME_WITH_TZ` | instants (`…At`) | never plain `DATETIME` — see below |
| `BOOLEAN` | flags | |

Field keys are camelCase: `fieldName`, `type`, `lengthLimit`, `isRequired`, `isUnique`.

## Six field types are accepted by the server and broken in the UI

The CLI guards against them and names the whole set in its error:

```
UI-broken types: INTEGER, BIG_INTEGER, FLOAT, DOUBLE, UUID, DATETIME.
```

Use `DECIMAL` for amounts and `DATETIME_WITH_TZ` for timestamps. `DATE` is fine for a plain calendar date. A
column created as one of the broken six looks right in `entities get` and cannot be rendered, filtered or edited
by any human afterwards.

## Get the schema right in one `create`

`uip df entities update` takes a **different body shape** from what `entities get` returns, so the natural
round-trip — get, edit, put back — does not work. Errors also surface one section at a time, so a schema with
three problems takes three attempts to learn about. Creating fresh is faster than repairing, and at this stage
you have no data to lose:

```bash
uip df entities create ClaimCase_<seat> --file entity.json --output json
```

Write the definition to a file rather than inlining it. Thirty-odd fields on a command line is unreadable, and
you will want to diff it when block 5 reports a column it cannot find.

## Done when

```bash
uip df entities list --output json          # the entity exists, carrying your seat token
uip df entities get <entity-id> --output json   # every column from the contract, with the type the contract gives
```

Then check no column is capped at 200 by accident — every `MULTILINE_TEXT` in the output should carry
`lengthLimit: 10000`. A missing one is the single most likely way this block ships broken, because nothing fails
and nothing warns; you simply lose everything past the 200th character on every claim from here on.
