The shapes more than one block has to agree on: the analysis payload envelope, the claim record, the settlement
table, and the six processes the exercise provides. They live here rather than inside a block folder because two or three blocks each read them, and a
contract with two homes is a contract that drifts.

**Names in these files are fixed.** An unpinned contract between components is the most expensive class of
failure this build can produce — it does not fail at pack time, it fails on a live run, three blocks later.
