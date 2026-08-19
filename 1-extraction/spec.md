# Extracting the claim form — what to build

The claim submission form is the one document your solution reads as **structured data**. The policy and the
assessor's report are read as documents, by an analysis that needs judgement rather than fields (`pdd.md` §5.5)
— only the claim form goes through extraction.

You are building an IXP project that turns that PDF into the claim payload every later component consumes.

## Two ways to do this, and both are legitimate

| | Build your own | Use the shared project |
|---|---|---|
| You get | a project you created, trained and published | a working project someone else trained |
| Costs | ~45–60 minutes, most of it waiting for retrains | minutes |
| Take it when | you want the IXP experience, and you have the time | time is short, or your own project stalls |

**The fallback is not a failure.** Extraction is the one block whose output everything else depends on, so a
half-trained project poisons every block after it. If yours is not producing clean fields by the time you need to
move on, switch to the shared one and keep going — the rest of the exercise is unaffected, because both produce
the same shape.

## The shape is fixed — this is the contract

Whichever route you take, the extracted payload **must** carry these six field groups under these names. Later
components address them directly, so a renamed group is a broken build three blocks later.

| Group path in IXP | Key in the payload | Carries |
|---|---|---|
| `Claim` | `Claim` | the claim identifier, the insurer, the submission date |
| `Claim > Claimant` | `ClaimClaimant` | who is claiming, and their contact details |
| `Claim > Property` | `ClaimProperty` | the insured address as written on the form |
| `Claim > Incident` | `ClaimIncident` | what happened, when, what type, and the emergency-response answers |
| `Claim > Damage Inventory` | `ClaimDamageInventory` | one entry **per damaged item** |
| `Claim > Claim Totals` | `ClaimClaimTotals` | the per-category totals and the total claimed |

IXP names nested groups with a `>` path and the payload flattens that path into one key — which is exactly where
`ClaimClaimant` comes from. **Get the path wrong and the key changes**, three blocks before anyone notices.

`1-extraction/taxonomy.json` is the artifact: **import it, do not retype it and do not accept IXP's suggestion.** A
suggested taxonomy is plausible and slightly different, and slightly different fails at the consumer.
`1-extraction/taxonomy.md` explains what is in it.

**The damage table is where care is needed, but not in the taxonomy.** It has one to five rows and IXP returns
one occurrence of the group per row — there is no flag to set, occurrences are how extraction works. The care is
in *labelling*: confirming a field confirms it in **every** occurrence, so a document where some rows extracted
correctly and others did not needs per-occurrence confirmation, or you confirm the wrong ones too.

## Getting samples

Claims are generated on demand — you can produce as many as you need, and you should. Extraction quality comes
from variety, not volume: claims arrive in several countries and currencies, with different incident types and
between one and five damage rows.

**Aim for 10–15 documents**, drawn without pinning a scenario so you get the natural mix. Note the constraint
before you plan the run: **taxonomy suggestion accepts at most 8 documents**, so if you let IXP suggest a
taxonomy it sees a subset — but you label and train on all of them.

## Done when

- The project is published with a live tag, and `get-metrics` reports a score rather than "not validated yet".
- A claim form the project has never seen extracts all six groups.
- A claim with **five** damage rows returns five occurrences of `ClaimDamageInventory`, not one.
- Field **types** match the imported taxonomy: amounts come back as amounts carrying their currency, the two
  real dates as dates, the yes/no answers as booleans — and the identifiers (claim number, policy number, ZIP,
  phone) stay text, because normalising an identifier breaks the join to the policy.

## One thing the CLI cannot do

Publishing a model does not make it available to an automation. **Binding a published model to an Orchestrator
folder is done in the product**, and there is no CLI equivalent — so the last step of this block happens in the
IXP interface, whichever route you took.
