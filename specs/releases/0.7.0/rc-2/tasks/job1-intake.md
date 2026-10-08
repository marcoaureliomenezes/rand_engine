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

- Contract: after J1.S2 closes GREEN, exit `tests/test_1_advanced_validator.py` with 100 passed and no xfails by deleting its RED marker lines only; envelope `rand_engine/validators/common_validator.py rand_engine/validators/advanced_validator.py tests/test_1_advanced_validator.py`; ACs AC3.2, AC4.2–AC4.3, AC8.2, AC8.7, AC9.2.
- J1.S3.T1 — rebuild shared typed intake and advanced intake · AC3.2, AC4.2–AC4.3, AC8.2, AC8.7, AC9.2 · `W:` `rand_engine/validators/common_validator.py` `rand_engine/validators/advanced_validator.py` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · make Common's sole catalog-driven required/optional/type/unknown/semantic seam reusable by Advanced before method-specific rules; refuse empty domains/modifiers on excluded methods; delete duplicated tables/history branches; preserve field/option/key-path diagnostics without dumping collections, pairs, items or input values.

## Stage J1.S4 — review regressions RED

- Contract: after the J1.S2 additional checkpoint and J1.S3 implementation, exit `tests/test_1_common_validator.py` with assertion-first regressions under strict xfail markers; envelope `tests/test_1_common_validator.py`; ACs AC2.2, AC3.2, AC7.1, AC8.1, AC8.3, AC9.2.
- J1.S4.T1 — validator compatibility and totality RED · AC2.2, AC3.2, AC7.1, AC8.1, AC8.3, AC9.2 · `W:` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · prove through public construction that legacy `floats`/`floats_normal` accept and generate negative decimals and infinite mean/std while negative std remains invalid; every new-distribution numeric parameter (`scale`, `mean`, `std`, `lam`, `a`) reports a collected `SpecValidationError` for a huge integer rather than leaking `OverflowError`; and anomaly values accept the declared scalar family but reject an arbitrary object. Keep final literal behavior in each assertion, observe raw RED by assertion, then add only strict xfail marker lines.

## Stage J1.S5 — review corrections and close

- Contract: exit the J1.S4 owner tests GREEN by deleting only their new RED marker lines; require the repeated J1.S2 additional checkpoint to approve that GREEN before J1.S5.T2 writes terminal `done`; then require the official Stage J1.S5 gate GREEN with its closing trailer and a final Job 1 review bound to that complete closing HEAD before canonical job merge; envelope `rand_engine/validators/method_specs.py rand_engine/validators/common_validator.py tests/test_1_common_validator.py specs/releases/0.7.0/rc-2/tasks/job1-intake.md`; ACs AC2.2, AC3.2, AC7.1, AC8.1, AC8.3, AC9.2.
- J1.S5.T1 — repair validator compatibility, numeric totality and scalar structure · AC2.2, AC3.2, AC7.1, AC8.1, AC8.3, AC9.2 · `W:` `rand_engine/validators/method_specs.py` `rand_engine/validators/common_validator.py` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · separate preserved legacy float/normal semantics from new-distribution domains without a new decimals ceiling; make numeric finiteness predicates total over every accepted numeric type; use one declared-scalar predicate for constant and anomaly structure; remove only the J1.S4 markers, with no flags, wrappers, special-value branches or old-assert rewrites.
- J1.S5.T2 — close validation intake job · AC8.1–AC8.3, AC8.7 · `W:` `specs/releases/0.7.0/rc-2/tasks/job1-intake.md` · owner `tests/test_1_common_validator.py` · only after J1.S5.T1 is GREEN and the repeated J1.S2 additional checkpoint approves, write terminal `done` exactly once and commit `chore(tasks): done job1-intake`; the stage gate and closing trailer then precede the final Job 1 review.
