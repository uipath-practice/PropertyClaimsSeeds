# Checkpoint — the claim record

Restores block 3's output: the `ClaimCase_<NN>` entity, all 38 columns, correct types and length limits.

```bash
uip df entities create ClaimCase_<NN> --file entity.json --output json
```

Verify it took:

```bash
uip df entities get <entity-id> --output json
```

**What it costs you:** nothing conceptual. Block 3 is a contract in and a schema out — the thinking is in
`contracts/claim-entity.md`, and you still have to read that file to bind anything in block 5. Of all the
checkpoints, this is the one to use without hesitation if the CLI is fighting you.
