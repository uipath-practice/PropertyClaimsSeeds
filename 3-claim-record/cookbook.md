# Block 3 — getting the claim record built

Friction from real builds. The spec is `contracts/claim-entity.md`; this is how to get it onto the platform.

**Skill.** `uipath-platform` — Data Fabric has no skill of its own, and this is the one place its
preview-then-confirm gate fires on a schema that is already agreed (`3-claim-record/prompt.md` grants it).

## The JSON columns are `MULTILINE_TEXT`, and the limit is real

A larger field type (`MULTILINE_MAX`, 128 KB) exists but is in private preview and gated per tenant. If you try
it you get a clean early error:

```
Cannot create MULTILINE_MAX field 'claimDataJson': the Multi-line (Max) feature is not enabled for this tenant.
```

**Use `MULTILINE_TEXT` with `lengthLimit: 10000` and move on.** Two things the error above does not tell you:
`50000` and `131072` are rejected outright too, so 10,000 really is the ceiling for this type — and a column
created with *no* `lengthLimit` silently defaults to **200**, which is the same failure fifty times worse.

**Every limit, and why each one is what it is, lives in `contracts/claim-entity.md`.** Read it before you write
the schema rather than after: it is the file that decides whether this block ships broken, and it is short.

## Create the entity in your seat folder

Data Fabric entities can live at tenant level or in an Orchestrator folder. **Yours goes in your seat folder**,
which means one extra flag and one changed failure mode:

```bash
# Exact-name match, not `--output-filter "[0].Key"` — that keeps the envelope and `--name` is a
# prefix match, so `[0]` is a coin toss between your seat and its -Deploy folder.
# known-issues/cli-commands.md has both traps and the PowerShell form.
FK=$(uip or folders list --all --name ClaimCase-<seat> --output json \
     | python3 -c "import json,sys; print(next(f['Key'] for f in json.load(sys.stdin)['Data'] \
                                               if f['Name']=='ClaimCase-<seat>'))")
uip df entities create ClaimCase_<seat> --file <schema>.json --folder-key "$FK" --output json
uip df entities list --native-only --folder-key "$FK" --output json      # confirm
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
`Entity 'ClaimCase_<seat>' not found at tenant level` reads as expected rather than as a broken entity.

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

## Changing a column after the fact

You will get one wrong. Widening a `lengthLimit` is safe and loses nothing — but `updateFields` keys on the
field's **`id`**, not its name, and the name is what you have:

```
Each field in updateFields must include a non-empty 'id' string
```

Read the ids out of the entity first, then send a partial update naming only what changes:

```bash
uip df entities get <entity-id> --folder-key <seat-folder-key> --output json \
  --output-filter "Fields[?Name=='eligibilityNotes'].Id | [0]"

uip df entities update <entity-id> --folder-key <seat-folder-key> \
  --body '{"updateFields":[{"id":"<field-id>","lengthLimit":4000}]}'
```

A partial update leaves everything you did not name alone — `displayName`, `isRequired` and the type all
survive. `--yes` is only needed for `removeFields`.

## Naming: the entity is the one place the hyphen is illegal

Everything else you create is `ClaimCase-<seat>` — folder, solution, packages, build directory (`CONFIG.md`,
*One name, everywhere*). Entity names take **letters, digits and underscores only, and must start with a
letter**, so this one is `ClaimCase_07`. Not `ClaimCase-07`, which is rejected, and not `ClaimCase07`, which is
accepted and then reads as somebody else's convention for the rest of the build.

Your folder scopes the name, so a collision with another seat is not the risk it would be at tenant level — but
keep the seat token anyway. It is what makes a row, a log line or a runtime error attributable to you.

If you find entities from an earlier attempt at this use case — a normalised model with names like `Claim`,
`Policy`, `DamagedItem` — **leave them alone** and do not bind to them by accident. They are not this design,
and the tenant is shared. On a clean tenant you will see `SystemUser`, which is Data Fabric's own, and `WorkshopFindings`, which is the findings table you have been logging to since the first minutes of the exercise. Neither is a leftover and neither is yours to touch.

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

## Proving it is done

```bash
uip df entities list --native-only --folder-key <your-seat-folder-key> --output json   # the entity exists
uip is connections list uipath-uipath-dataservice --refresh --all-folders --output json  # the shared connection

# A raw `entities get` on 38 columns is upwards of 22,000 tokens and will be truncated on you.
# Ask for the four things that can be wrong:
uip df entities get <entity-id> --folder-key <your-seat-folder-key> --output json \
  --output-filter "Fields[].{n:Name,t:Type,len:LengthLimit,dp:DecimalPrecision}"
```

**Audit three things, and only these three.** "No column is capped at 200" is the wrong test — four columns are
*deliberately* 200 or below, so a check that flags every 200 flags four correct columns and buries the real one.

| Must read | Columns |
|---|---|
| `lengthLimit: 10000` | every `MULTILINE_TEXT` — a missing one loses everything past character 200, silently, on every claim from here on |
| `lengthLimit: 4000` | `eligibilityNotes`, `reviewerNotes` |
| `decimalPrecision: 2` | `totalClaimAmount`, `approvedPayout` |

**Two things in that output are the platform's, not yours, and both look like drift the first time.** `get`
returns a **39th field, `RecordOwner`** (a `RELATIONSHIP`), which you did not send; and it stamps a
`LengthLimit` on typed columns that have no length at all — `1000` on `DATE`, `DATETIME_WITH_TZ` and `DECIMAL`,
`100` on `BOOLEAN`. Ignore both. **Only `STRING` and `MULTILINE_TEXT` limits are yours.**

Neither failure mode announces itself, so **round-trip a value** rather than reading the schema and believing it:
insert one row with cents in both decimals, a 1,000-character note and a ~9,000-character JSON payload, read it
all back unchanged, then delete the row. Four minutes, and it is the only thing that separates a correct
`decimalPrecision` from a plausible-looking one.
