# Job 4 — Reconciliation

**Status:** Approved

These stages are sequential. Canonical labels map to actual task IDs/commits
below; renumbering creates no new implementation or RED evidence. J4 remains
open until terminal benchmark proof exists.

## Stage J4.S1 — read-only readiness

- Contract: identify locally merged implementation heads, resolved bugs, local gates and closure scope; first stage is read-only, with no new acceptance test or RED requirement.
- J4.S1.T1 — readiness · `W:` none (read-only) · owner `tests/test_docs.py`, `tests/test_benchmarks.py`, `tests/test_2_data_generator.py` · final PR #42 proof is a terminal release gate after feature publication, not a memory-preparation prerequisite.

## Stage J4.S2 — technical preparation

- Contract: record technical provenance and publication cadence without runtime/harness changes.
- [x] J4.S2.T0 — technical preparation · `W:` `specs/releases/0.7.0/rc-1/PLAN.md`, `specs/releases/0.7.0/rc-1/TASKS.md`, `specs/releases/0.7.0/rc-1/tasks/job2-bug-batch.md`, `specs/releases/0.7.0/rc-1/tasks/job4-reconcile.md` · owner `tests/test_docs.py`
  Provenance: actual J4.S2.T0, `7742bba`; inherited fixes, version proof and obsolete freeze bootstrap recorded. No new tests.

## Stage J4.S3 — coverage declaration

- Contract: declare benchmark coverage after technical preparation.
- [x] J4.S3.T1 — coverage declaration · `W:` `specs/releases/0.7.0/rc-1/tasks/job4-reconcile.md` · owner `tests/test_docs.py`
  Provenance: actual J4.S2.T0B, `2095cef`. Atom `specs/memory/product/quality/benchmarks.md`, slug `benchmarks`, covers `benchmarks/**` and `.github/workflows/benchmarks.yml`; an uncovered package is not a reviewed atom.

## Stage J4.S4 — memory and derived documents

- Contract: reconcile merged behavior and catalog from the actual drift worklist; final benchmark artifacts and completion remain pending.
- [x] J4.S4.T1 — memory and docs · `W:` `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/content/templates-and-examples.md`, `specs/memory/product/generation/data-generator.md`, `specs/memory/product/generation/generation-methods.md`, `specs/memory/product/generation/spark-generator.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/relations/pk-fk-constraints.md`, `specs/memory/product/spec/rand-spec-grammar.md`, `specs/memory/product/quality/benchmarks.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json`, `README.md`, `llms.txt`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`, `specs/releases/0.7.0/_RELEASE.json` (memory record by release.py only) · owner `tests/test_docs.py`, `tests/test_benchmarks.py`, `tests/test_2_data_generator.py`
  Provenance: actual J4.S2.T1, `e0dd5e0` and `f7bf715`: eight changed atoms, zero reviewed entries. This product task does not write PLAN, TASKS, Job 2 or this file.

## Stage J4.S5 — corrective memory

- Contract: correct source coverage and fixed test-law text after J4.S4; shared derived markers are updated sequentially.
- J4.S5.T1 — corrective memory · `W:` `specs/memory/product/content/templates-and-examples.md`, `specs/memory/product/relations/pk-fk-constraints.md`, `specs/memory/QUALITY.md`, `specs/memory/product/catalog.json`, `specs/memory/product/index.md`, `README.md`, `llms.txt`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md` (affected markers only) · owner `tests/test_docs.py`
  Provenance: actual J4.S4.T2, `13b53d4`; local gate and merge are recorded by the main thread, not presumed here.

## Stage J4.S6 — readiness narrative

- Contract: record evidence/holds honestly; append release log only, preserving milestones and previous memory/history.
- [x] J4.S6.T1 — readiness narrative · `W:` `specs/releases/0.7.0/rc-1/tasks/job4-reconcile.md`, `specs/releases/0.7.0/_RELEASE.json` (append log only) · owner `tests/test_docs.py`
  Provenance: actual J4.S5.T1, this metadata task. Local gates and reviewer APPROVED precede local feature merges; no worktree pushes/job CI. Only prepared feature is published. Existing remote worktree refs remain untouched. J4 is not done.

## Stage J4.S7 — terminal benchmark follow-up

- Contract: after feature CI, commit actual final PR #42 proof only when every FR12 ratio ≤ 1.3; name measured head/run, then complete J4. Samples, repetitions, RNG and limit unchanged.
- J4.S7.T1 — terminal proof · `W:` `docs/benchmarks.json`, `docs/BENCHMARKS.md`, `specs/releases/0.7.0/_RELEASE.json`, `specs/releases/0.7.0/rc-1/tasks/job4-reconcile.md` (done) · owner `tests/test_benchmarks.py` · not started; replaces the unstarted J4.S3.T1 terminal label. No worktree push.
