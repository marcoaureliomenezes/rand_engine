# Job 7 — FR4 record this candidate's benchmark table in the docs

**Wave:** 3 · **Waits on:** Job 3, Job 4, Job 5, Job 6

The last code job (AC4.3): it waits on every other job, and Reconciliation writes `specs/` only. Procedure: PLAN §3.4; the Benchmark record Term of the SPEC.

- Before dispatch (the main thread): all of Jobs 1 to 6 are merged into `feature/0.8.0`, which is pushed once; a `Benchmarks` run on that head is started (`gh workflow run benchmarks.yml --ref feature/0.8.0`, or the `pull_request` run when a PR on the branch is open) and ends `success`, about 17 minutes by the last measured run; its Job summary holds the table (AC4.1). The brief carries the run id and the directory where the main thread ran `gh run download <id> -n benchmarks`.
- Operator authority for the moved literals: the demand of 2026-10-16, «eu ver testes de benchmark de CI funcionando e publicando um summary no actions … + merge de benchmarks na documentação».
- Benchmarks run in CI only; the record is a copy, never a local run.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J7.T1 | sr | AC4.2 | `tests/test_benchmarks.py` | RED: `TERMINAL_HEAD` and `TERMINAL_BASE` (`:306-307`) take the artifact's `commit` and `base_commit`; the test that compares them to the committed JSON is `xfail(strict=True)` because the committed JSON still holds 0.7.0's. The `test(J7.T1)` commit names the operator demand as the authority. Owner: tests/test_benchmarks.py |
| J7.T2 | jr | AC4.1, AC4.2, AC4.3 | `docs/benchmarks.json`, `docs/BENCHMARKS.md`, `tests/test_benchmarks.py` | copy `docs/benchmarks.json` and `docs/BENCHMARKS.md` from the artifact byte for byte (`cmp` exits 0); remove the J7.T1 marker; the existing artifact tests (`:315-333`) pass. The commit body names the run id, head, base, the two sha256 values, and quotes `git diff --stat <head> HEAD -- rand_engine benchmarks pyproject.toml poetry.lock` printing nothing. Owner: tests/test_benchmarks.py |
