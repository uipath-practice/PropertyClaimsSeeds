# `is connections list` reports nothing while the connection exists

**What you see.** You create a connection, authorise it in the browser, then run the verification command the
CLI itself suggests:

```
$ uip is connections list --output json
{ "Result": "Success", "Data": { "Message": "No connections found for any connector." } }
```

It reads as a failed authorisation. It is not — the connection is Enabled and usable.

**Why.** The bare form does not look past its default folder scope, and it answers from a cache.

**What to do instead.**

```bash
uip is connections list <connector-key> --refresh --all-folders --output json
```

Never conclude a connection is missing from the bare form. The same caution applies to any `list` that returns
an empty set for something you have just created — scope it and refresh before believing it.
