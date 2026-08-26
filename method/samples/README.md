# Worked examples

A complete PDD and a complete Case Management SDD for one process, written to the templates beside them. Read them when a section of a template is clear about *what* goes in and unclear about *how much*.

| Sample | Written to | Notable |
|---|---|---|
| `pdd.md` | [`../template-pdd.md`](../template-pdd.md) | all 15 sections filled · 51 numbered business rules, each with a worked example · a §5.3 step table where every decision carries its nature · a canonical case whose arithmetic can be checked |
| `sdd.md` | [`../template-sdd-case.md`](../template-sdd-case.md) | 8 stages · 29 tasks, one per step in the PDD's step table · every task type traceable to that step's decision nature |

**The SDD was generated from the PDD**, not written alongside it — which is the point. Two different models produced near-identical designs from it: same stages, same names, same task count, and the same deterministic-versus-judgement split.

**Both are synthetic.** The process is internally consistent and complete, and the organisation is not real.

---

*Maintainers: the samples are not committed here. They live once, at `../../PDD.md` and `../../checkpoints/1-design/sdd.md`, and are vendored into this folder when the guide is published standalone — a second committed copy is the one that goes stale.*
