# Commands that fail while the thing they describe is fine

Each was met in a real build; the command is wrong, not your solution. These cross every block; a trap that belongs to one block is in that block's `cookbook.md`.

## `--folder-key` takes a GUID, and a folder *name* fails silently

`uip or processes list --folder-key ClaimCase-07` does not error: it returns a **different, paginated, tenant-wide list** — other seats' processes included — with `HasMore: true`. Pass the GUID (`--folder-path` takes a name); read it with a JSON reader and an exact name match — `--name` is a *contains* match, so `ClaimCase-07` also returns `ClaimCase-07-Deploy`:

```bash
FK=$(uip or folders list --all --limit 200 --output json \
     | python3 -c "import json,sys; print(next(f['Key'] for f in json.load(sys.stdin)['Data'] \
                                               if f['Name']=='ClaimCase-<seat>'))")
```

`--all` is required or the seat folder is not listed. `--output-filter` needs an explicit `--limit` and keeps the envelope, so `FK=$(… --output-filter "[0].Key")` captures JSON, not the GUID. **A list bigger than you expected is scoped wrongly; `HasMore: true` has not answered your question.**

## Reading what came back: `entry-points` at a wrong version, outputs parsed twice, query field names

It reads as *no arguments*, not *no such version* — read the version from `uip or processes list` first (not all six are on `1.0.0`). `uip maestro case tasks describe --type process` finds nothing for them either. `uip df records query` filters take a field's own camelCase name (`claimId`, `sentAt`), although every read prints it PascalCased (`ClaimId`). `uip or jobs get` needs no folder — with `--folder-key` it can return no data. **Parse twice**: `entry-points` argument schemas and `uip or jobs get`'s `OutputArguments` are JSON strings inside the JSON.

## `tasks assign` with a folder, `attachments download` to a directory

`uip tasks assign` refuses `--folder-key`, while `uip tasks data get` and `uip tasks complete` need it — assign without, complete with. `uip or attachments download <id> -d <path>` takes a **file** path; given a directory it hangs.

## Warnings mixed into the output you parse

`uip solution upload --output json` prints `[WARN]` lines on stdout before the JSON, so a JSON parse of the whole capture fails at line 1 — find the envelope (`{`) first, or read `"Action": "Overwritten"`. `uip maestro case spec` writes its `[WARN]` lines to stderr: keep `2>&1` out of the redirect that saves the spec cache. In `--output-filter`, `contains(FullyQualifiedName, …)` fails on the tenant folders whose name is null; filter on `starts_with(Name, …)`.

## Instances and jobs that stop moving

| Issue | Fix |
|---|---|
| `instance migrate` answers a generic `400` | The instance is still `Pausing`. Resume it, wait for `Running`, then migrate. |
| A job sits `Pending` with no reason given | Kill it (`uip or jobs stop <key> --strategy Kill`) and start it again. |
| `instance variables` answers HTTP 500 | Transient. Wait a few seconds and read again. |
| A records or correspondence query returns exactly 50 rows | It pages at 50. Read the next page until it comes back short. |
