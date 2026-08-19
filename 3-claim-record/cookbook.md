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

## Create the Data Fabric connection now, not in block 5

The entity can be created without a connection, but nothing can *write* to it from a case plan without
one — and that failure surfaces two blocks later, expensively.

```bash
uip is connections create uipath-uipath-dataservice --no-browser --no-wait --output json
```

This returns an `AuthUrl` and stops. **A coding agent cannot finish this step** — it is an OAuth consent, and it
has to be you. Open the URL, authorise, then verify:

```bash
uip is connections list uipath-uipath-dataservice --refresh --all-folders --output json
```

**Use exactly that command.** A bare `uip is connections list` reports *"No connections found for any
connector"* while the connection exists and works — it does not look past its default folder scope or its cache.
The CLI's own `Instructions` field suggests the bare form, so the natural next step after authorising is a
message saying nothing is there. Add `--refresh --all-folders` before concluding anything failed.

The connection is deliberately **yours**, not something provisioning created for you: a connection owned by
somebody else — or living in a personal workspace — produces `Missing instance <n> for user <n>` at run time,
in block 5, with nothing in the message pointing back to here.

## Naming: the entity name is stricter than the folder name

Entity names take **letters, digits and underscores only, and must start with a letter**. Your seat token is
part of the name and folder-style punctuation is rejected — `ClaimCase_01`, not `ClaimCase-01`.

The name is also tenant-scoped, so it is the collision surface with every other seat. Check first:

```bash
uip df entities list --output json --output-filter "[].Name"
```

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
