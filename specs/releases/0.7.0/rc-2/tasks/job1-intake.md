# Job 1 — validation intake and catalog

**Status:** Approved

## Stage J1.S1 — RED

- Contract: exit tests `tests/test_1_common_validator.py tests/test_1_advanced_validator.py` fail by assertion under strict xfail markers; envelope `tests/test_1_common_validator.py tests/test_1_advanced_validator.py`; ACs AC2.2, AC3.2, AC4.2–AC4.3, AC8.1–AC8.2, AC8.7, AC9.2.
- J1.S1.T1 — common/numeric intake RED · AC2.2, AC3.2, AC4.2, AC8.1, AC9.2 · `W:` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · wrong numeric types collect, new-method domains validate, Spark refuses NumPy-only methods/modifiers/uint64.
- J1.S1.T2 — advanced-domain and single-intake RED · AC3.2, AC4.2–AC4.3, AC8.2, AC8.7 · `W:` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · empty mapped pools/levels, excluded modifiers and kwargs-only migration fail before generation; a counting callable returning independently invalid common/advanced columns is evaluated once for the failed public construction, yields one collected issue per column, never reaches a generation sentinel and leaks no internal exception.

## Stage J1.S2 — common catalog rebuild

- Contract: exit `tests/test_1_common_validator.py` GREEN by deleting its RED marker lines only; envelope `rand_engine/validators/method_specs.py rand_engine/validators/common_validator.py tests/test_1_common_validator.py`; ACs AC2.2, AC3.2, AC4.2, AC8.1, AC8.7, AC9.2.
- J1.S2.T1 — replace common intake with sole catalog · AC2.2, AC3.2, AC4.2, AC8.1, AC8.7, AC9.2 · `W:` `rand_engine/validators/method_specs.py` `rand_engine/validators/common_validator.py` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · structural/type gates precede typed semantics; catalog records engine support and ordinary kind.

## Stage J1.S3 — shared intake and advanced rebuild

- Contract: after J1.S2 closes GREEN, exit `tests/test_1_advanced_validator.py` with 100 passed and no xfails by deleting its RED marker lines only, then write this job file's terminal `done` once; envelope `rand_engine/validators/common_validator.py rand_engine/validators/advanced_validator.py tests/test_1_advanced_validator.py specs/releases/0.7.0/rc-2/tasks/job1-intake.md`; ACs AC3.2, AC4.2–AC4.3, AC8.2, AC8.7, AC9.2.
- J1.S3.T1 — rebuild shared typed intake and advanced intake · AC3.2, AC4.2–AC4.3, AC8.2, AC8.7, AC9.2 · `W:` `rand_engine/validators/common_validator.py` `rand_engine/validators/advanced_validator.py` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · make Common's sole catalog-driven required/optional/type/unknown/semantic seam reusable by Advanced before method-specific rules; refuse empty domains/modifiers on excluded methods; delete duplicated tables/history branches; preserve field/option/key-path diagnostics without dumping collections, pairs, items or input values.
- J1.S3.T2 — close validation intake job · AC8.1–AC8.2, AC8.7 · `W:` `specs/releases/0.7.0/rc-2/tasks/job1-intake.md` · owner `tests/test_1_advanced_validator.py` · after the stage contract is green, write terminal `done` exactly once and commit `chore(tasks): done job1-intake`.
