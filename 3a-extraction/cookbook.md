# Extraction — what bites

| Issue | Fix |
|---|---|
| `uip ixp deployments list` on the shared project returns `[]` | Nothing is missing. The provided `Extract Claim Data (IXP)` automation is **pinned** to the shared project — project id, `live` tag and model version 3 are literals in its workflow, so a newer version in the project is not what it runs; only the `Claims` bucket is a deploy-time binding. It needs no folder deployment, and deploying a model of your own changes nothing it reads (`prompt-build.md`). |
