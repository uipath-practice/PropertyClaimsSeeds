# Commands that fail while the thing they describe is fine

Each was met in a real build; the command is wrong, not your solution. These cross every block; a trap that belongs to one block is in that block's `cookbook.md`.

## `--folder-key` takes a GUID, and a folder *name* fails silently

`uip or processes list --folder-key ClaimCase-07` does not error: it returns a **different, paginated, tenant-wide list** — other seats' processes included — with `HasMore: true`. Pass the GUID (`--folder-path` takes a name); read it with a JSON reader and an exact name match — `--name` is a *contains* match, so `ClaimCase-07` also returns `ClaimCase-07-Deploy`:

```bash
FK=$(uip or folders list --all --limit 200 --output json \
     | python3 -c "import json,sys; print(next(f['Key'] for f in json.load(sys.stdin)['Data'] \
                                               if f['Name']=='ClaimCase-<seat>'))")
```

`--all` is required or the seat folder is not listed. `--output-filter` keeps the envelope, so `FK=$(… --output-filter "[0].Key")` captures JSON, not the GUID. **A list bigger than you expected is scoped wrongly; `HasMore: true` has not answered your question.**

## Reading what came back: `entry-points` at a wrong version, outputs parsed twice, query field names

It reads as *no arguments*, not *no such version* — read the version from `uip or processes list` first (not all six are on `1.0.0`). `uip maestro case tasks describe --type process` finds nothing for them either. `uip df records query` filters take a field's own camelCase name (`claimId`, `sentAt`), although every read prints it PascalCased (`ClaimId`). `uip or jobs get` needs no folder — with `--folder-key` it can return no data. **Parse twice**: `entry-points` argument schemas and `uip or jobs get`'s `OutputArguments` are JSON strings inside the JSON.

## `jobs list` at `--limit` 100, and `tasks assign` with a folder

`uip or jobs list --limit 100` (or more) returns an empty `Data[]` where 50 returns rows: page with `--limit 50 --offset`. `uip tasks assign` refuses `--folder-key`, while `uip tasks data get` and `uip tasks complete` need it — assign without, complete with.

## `codedapp publish -t Action` hangs or fails at registration on the 1.203 and 1.204 preview lines

The package uploads, then *Registering coded app…* fails with *Error occurred while creating a version for action schema … multi-document transaction*, or hangs for 300 s and ends `fetch failed`. The preview `codedapp-tool` gives every Action App on a tenant the same action-schema key, so only the first one ever registers (APPS-38047). Your app is fine. Publish that one step with the stable tool, run from its package in the app folder; `uip codedapp deploy` and everything else stay on the pinned line:

```bash
npm pack @uipath/codedapp-tool@1.202.2 --silent && mkdir -p /tmp/codedapp-stable \
  && tar -xzf uipath-codedapp-tool-1.202.2.tgz -C /tmp/codedapp-stable && rm uipath-codedapp-tool-1.202.2.tgz
uip codedapp pack                                          # as usual
node /tmp/codedapp-stable/package/dist/index.js publish -t Action -n <app-name> -v <version>
```

Use a version the failed attempts did not take. A Web app has no action schema and publishes normally.
