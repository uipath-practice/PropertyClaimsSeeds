# Building the review app — platform notes

Friction you will meet building the reviewer's app on UiPath, and the commands that show you what is
actually happening. It is not a tutorial: it assumes you can read the SDK's own docs and are stuck on
something they do not mention.

*(First entries. This grows as builds report what actually cost them time.)*

## Getting a document onto the reviewer's screen

The reviewer needs to see three PDFs — the claim form, the policy, the assessor's report. There are
two ways to reach them and they fail differently, so choose deliberately rather than by whichever the
SDK docs open on.

### The two routes

**As a job attachment.** An RPA process that outputs a file resource leaves it in Orchestrator as a
job attachment, addressed by a GUID. Your app resolves it with `attachments.getById(id)` and gets
back a `blobFileAccess` descriptor: `{ uri, httpMethod, requiresAuth, headers }`. Fetch it, make a
blob URL, render it. Needs the `OR.Folders` scope. Not folder-scoped — a GUID is addressable on its
own.

**As a bucket file.** The same PDF also sits in a storage bucket under a filename. Resolve it with
`buckets.getByName(name, { folderPath })` for the bucket's numeric id, then
`buckets.getReadUri(bucketId, path, { folderPath })` — which returns **the same descriptor shape**, so
the fetch-and-render half of your code is identical. Needs `OR.Buckets.Read`, and the folder is not
optional.

### Which to prefer, and why it is not a matter of taste

An attachment id is a **reference that has to survive every hop between producer and consumer** —
process output → case variable → entity column → task → app. Five places where it can arrive empty,
and the symptom is always the same one: your app says the document is not there, which reads like an
app bug and is not.

A bucket path is **derived where it is used**, from identifiers the record already holds (the claim
number, the policy number). Nothing has to carry it, so nothing can drop it.

So: **try the id, fall back to the derived path.** The id is genuinely better when it arrives — no
folder scope, no bucket lookup, one call — and the fallback is what stops the feature depending on it
arriving. Written that way, the app also repairs itself if the pipeline starts populating ids again,
with no second edit.

Two things the fallback still needs to get right:

- **Derive a path only for a document that should exist.** A filename is predictable long before the
  file is; the assessor's report has a computable name from the moment a claim has a number, and no
  file until an inspection has happened. Gate the derived path on something that proves the document
  exists — the report's own extracted payload, for instance. Otherwise a reviewer gets a button that
  404s where they should have seen "the assessor has not reported yet".
- **Say what you looked for when it fails.** `Claims/CLM-…-claim.pdf did not resolve: <reason>` is a
  sentence someone can act on. "Could not load document" is not.

### Where the files are, and why the folder matters

Buckets are **linked into** the solution folder from the folder that owns them, not provisioned
inside it — a solution subfolder does not inherit its parent's buckets. So every bucket call has to
name the folder holding the bucket, which is *not* the folder your app is running in. That folder
path is the one environment-specific value your app carries: name it once, in one place.

The bucket's numeric id is tenant-local and changes if a bucket is ever recreated. Look it up by name
and cache it for the session; do not write it into the source.

**What reveals the state:**

```bash
uip or buckets list --folder-key <folder> --output json          # names, keys, numeric ids
uip or bucket-files list <bucket-key> --folder-key <folder>      # the paths actually present
```

The second one is the answer to "is the app wrong, or is the file simply not there" — a question
worth settling before reading any app code. Paths resolve with or without a leading slash.

## An app that reads a new service needs its scope, and the error says neither

Adding one SDK service to a working app can break it, because each service needs its own OAuth scope
and the refusal names neither the service nor the scope:

```
You are not authorized!
```

That is the whole message. Check the scope before suspecting your call, your folder, or your
permissions.

**Two separate things have to agree**, and this is where an afternoon goes:

| | Where it lives | What it means |
|---|---|---|
| The **grant** | the External Application registration in Automation Cloud | what the app is *allowed* to ask for |
| The **request** | `uipath.json`, which ships **inside** the app package | what it *does* ask for |

Editing the registration alone changes nothing, because the deployed app still requests the old list
— the config travels in the package, so the scopes are frozen at the version being served, and that
is the version your solution pins. Symptom: you fix the registration, reload, and get the identical
error, repeatedly.

The fix is both halves: grant it on the registration, and publish a new app version carrying the
updated `uipath.json`, pinned by a new solution version.

```bash
uip admin external-apps get <client-id> --output json    # what is actually granted
```

Worth knowing that the two drift quietly — ours had a scope granted that `uipath.json` did not list,
so neither file was evidence for the other.
