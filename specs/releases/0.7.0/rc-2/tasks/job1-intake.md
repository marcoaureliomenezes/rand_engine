# Job 1 — validation intake and catalog

**Status:** Approved

## Stage J1.S1 — RED

- Contract: exit tests `tests/test_1_common_validator.py tests/test_1_advanced_validator.py` fail by assertion under strict xfail markers; envelope `tests/test_1_common_validator.py tests/test_1_advanced_validator.py`; ACs AC2.2, AC3.2, AC4.2–AC4.3, AC8.1–AC8.2, AC9.2.
- J1.S1.T1 — common/numeric intake RED · AC2.2, AC3.2, AC4.2, AC8.1, AC9.2 · `W:` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · wrong numeric types collect, new-method domains validate, Spark refuses NumPy-only methods/modifiers/uint64.
- J1.S1.T2 — advanced-domain intake RED · AC3.2, AC4.2–AC4.3, AC8.2 · `W:` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · empty mapped pools/levels, excluded modifiers and kwargs-only migration fail before generation.

## Stage J1.S2 — rebuild

- Contract: exit owner tests GREEN by deleting their RED marker lines only; envelope `rand_engine/validators/** tests/test_1_common_validator.py tests/test_1_advanced_validator.py`; ACs AC2.2, AC3.2, AC4.2–AC4.3, AC8.1–AC8.2, AC8.7, AC9.2.
- J1.S2.T1 — replace common intake with sole catalog · AC2.2, AC3.2, AC4.2, AC8.1, AC8.7, AC9.2 · `W:` `rand_engine/validators/method_specs.py` `rand_engine/validators/common_validator.py` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · structural/type gates precede typed semantics; catalog records engine support and ordinary kind.
- J1.S2.T2 — rebuild advanced intake · AC3.2, AC4.2–AC4.3, AC8.2, AC8.7 · `W:` `rand_engine/validators/advanced_validator.py` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · consume sole catalog, refuse empty domains/modifiers on excluded methods, delete duplicated tables/history branches.
