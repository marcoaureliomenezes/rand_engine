# Job 6 — reconciliation and terminal evidence

**Status:** Approved

Job 6 is the final special `reconcile` tree. It opens only after Job 8 has merged, the original five-bug batch has been resolved with zero open records, and every normal implementation gate is green. It owns no new executable-documentation behavior, public-boundary tests, benchmark generation or product source; after memory changes, it only reconciles derived current-product truth and keeps already-correct files byte-identical.

The phase transition is the first reconciliation act. Product memory and terminal ledger evidence follow in the same tree through their canonical writers; no task worktree, stage command or pre-closure memory write is used.

| task | AC | `W:` | outcome |
|---|---|---|---|
| J6.T1 | AC1.1–AC9.4 evidence index | `specs/releases/0.7.0/_RELEASE.json` | Enter closure; main thread owns the canonical IMPLEMENTATION → CLOSURE transition at the exact merged Job 8 SHA only after release check, verify/build/package checks and zero-open-bug evidence are green. |
| J6.T2 | AC1.1–AC9.4 current product truth | `specs/memory/ARCHITECTURE.md` `specs/memory/QUALITY.md` `specs/memory/product/content/templates-and-examples.md` `specs/memory/product/generation/data-generator.md` `specs/memory/product/generation/generation-methods.md` `specs/memory/product/generation/spark-generator.md` `specs/memory/product/output/writers-and-streaming.md` `specs/memory/product/quality/benchmarks.md` `specs/memory/product/relations/pk-fk-constraints.md` `specs/memory/product/spec/rand-spec-grammar.md` `specs/memory/product/index.md` `specs/memory/product/catalog.json` `README.md` `llms.txt` `docs/1_DATA_GENERATOR.md` `docs/2_SPARK_GENERATOR.md` `docs/3_WRITING_FILES.md` `docs/5_RECIPES.md` `docs/BENCHMARKS.md` `specs/releases/0.7.0/_RELEASE.json` | Reconcile current product truth; product engineer consumes the exact eight-atom drift worklist, refreshes Architecture's Tech Stack and Structure, refreshes bug balance, keeps listed-but-unchanged atoms byte-identical, regenerates index/catalog, then reconciles the seven affected derived documents from changed memory and records reviewed/changed sets through the canonical memory writer. Job 8 remains the behavioral documentation and benchmark-evidence owner; this task adds no behavior or artifact generation. |
| J6.T3 | AC1.1–AC9.4 closure proof | `specs/releases/0.7.0/_RELEASE.json` | Terminal ledger evidence; main thread records the truthful summary, size, drifts, test dispositions, dispositions, reviews and artifact-GC results through canonical writers. |
| J6.T4 | AC1.1–AC9.4 | `specs/releases/0.7.0/rc-2/tasks/job6-reconcile.md` | Close reconciliation job; main thread writes terminal `done` exactly once after all terminal checks are green. This is the release's final job-file mutation. |

J6.T1 → J6.T2 → J6.T3 → J6.T4 is mandatory. After J6.T4, the root obtains one review of that exact complete HEAD and merges only an APPROVED result. The repeated `_RELEASE.json` authority is deliberate and sequential inside the one special reconcile tree; it is not parallel task ownership.
