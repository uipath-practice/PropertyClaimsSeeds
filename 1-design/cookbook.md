# Design — what bites

| Issue | Fix |
|---|---|
| The skill builds a whole project when you only wanted a design | Say **design only** in the request. It then writes `sdd.md` and stops. |
| Types come out matching agents already deployed on the tenant rather than the PDD | Its design phase pulls the registry **before** designing, so a tenant holding a prior build of the same process drives the choices. Name §5.3 explicitly in your request. Record what discovery found — that is a finding, not noise. |
| `sdd.md` is accepted and the case built from it is thin — blank task inputs, exit rules that never fire, a dropped SLA | The build **never checks the shape**: *"trust `sdd.md` as written; the skill does not validate or gap-fill it."* Nothing downstream will tell you. `check_sdd.py` is the only gate that exists. |
| Two templates both look like "the SDD template" | The numbered 17-section one is the planner's and is documentation. The four named sections are what the build reads. `method/sdd-guide.md`, first section. |
| A stage is both `Required for Case Completion: Yes` and secondary | Not expressible. A stage every healthy claim passes through is **primary**, however much waiting it does. |
| SLAs come out in wall-clock days when the PDD says business days | A stage SLA is a plain duration with no calendar field. State the rule in the design and attach a calendar at build time. |
| Resource ids cannot be resolved and the design stalls | Leave them unresolved. Identity resolution belongs to the build, against your own seat. |
| A `uip` command returns exit 0, prints *"Checking for updates…"* and no result | It consumed your command while updating itself. Run it again. |
| `check_sdd.py` fires on something you believe is correct | Leave it and say so. A wrong rule is worth more to us than a file edited to pass. |

## Reading the checker

`FAIL` reaches the built plan · `WARN` is worth a look and does not stop a build · `NOTE` is something it could not decide, which is never a pass.

`NATURE-3` counts tasks it could not match to a PDD step by name. A high count means the type check covered little, whatever the other lines say.
