# Job 1 — Finish bounded release maintenance

**Wave:** 1
**Waits on:** —
**W:** `specs/bugs/BUGS.jsonl`, `tests/test_9_cli.py`, `rand_engine/cli.py`, `pyproject.toml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/benchmarks.yml`, `.github/workflows/docs.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | pe | AC1.4 | `specs/bugs/BUGS.jsonl` | On the parent `wt-main` under the bug-ledger writer exception, register `get-started-race-overwrites-existing-target` with the documented no-overwrite contract, the real competing-creator reproduction, `J6.T2` cause and the intended exclusive-create remedy. Commit shape 1 only; write no product path. |
| J1.T2 | sr | AC1.1, AC1.3 | `tests/test_9_cli.py` | Add one race partition to the existing CLI test home. Wrap only the target `Path.open` write attempt once; immediately before delegating the original `"wb"`/`"xb"` open, create literal competing bytes with real I/O. Assert exit 1, unchanged bytes, empty stdout and the existing stderr wording. Do not mock `Path.exists()` or open modes; preserve every existing CLI assertion. This is the RED task. |
| J1.T3 | sr | AC1.2, AC1.3 | `rand_engine/cli.py` | REBUILD only `main` target creation: remove the preliminary existence check and truncating write; create and write through one exclusive binary `Path.open("xb")` path, mapping only `FileExistsError` to the existing stderr/exit-1 contract. Preserve slugs, `<slug>-example.py`, packaged bytes, success output and unrelated I/O propagation. This is the GREEN task for J1.T2. |
| J1.T4 | sr | AC2.1–AC2.3, AC3.1–AC3.3 | `pyproject.toml`, `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/benchmarks.yml`, `.github/workflows/docs.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml` | Set only `[build-system].requires` to `poetry-core>=2.2.0`. At all fourteen existing installer sites, use the already selected interpreter for `python -m pip install poetry==2.5.1`; remove only remote-bootstrap and installer-only PATH workarounds. Keep actions, Java 17 setup, OS shells, triggers, matrices, permissions, cache behavior, Poetry commands, artifacts, summaries and publishing unchanged. Record direct exact-floor build evidence outside the repo; add no source-text or workflow-mirror test. |
| J1.T5 | sr | AC4.1–AC4.3 | `tests/test_docs.py` | Tighten the existing main-reference assertion to compare sorted live directive and `__all__`-derived lists, preserving multiplicity without making reference-page order a contract. Prove RED by duplicating a valid directive in a temporary mutation, then restore it; retain the live `__all__` and docstring assertions and add no test home. |
| J1.T6 | sr | AC1.4, AC5.3 | `specs/bugs/BUGS.jsonl` | After J1.T3 is GREEN, resolve the registered bug on the parent `wt-main` via `bugs.py`, naming J1.T3's fix SHA, cause, RED/GREEN evidence and solution. Commit shape 4 only; write no product path. |

J1.T1 precedes J1.T2, J1.T2 precedes J1.T3, and J1.T3 precedes J1.T6. J1.T4
and J1.T5 may run beside that serial CLI chain because their exact product and
test write sets are disjoint. The one job review and unchanged job-merge
`verify:` provide the complete suite; existing workflow checks provide package,
cross-platform and CI evidence.
