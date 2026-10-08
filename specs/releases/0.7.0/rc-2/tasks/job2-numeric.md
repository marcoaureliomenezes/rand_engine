# Job 2 — numeric methods and exact Spark domains

**Status:** Approved

## Stage J2.S1 — RED

- Contract: exit core/benchmark owner tests fail by assertion under strict xfail markers; envelope `tests/test_0_np_core.py tests/test_0_spark_core.py tests/test_benchmarks.py`; ACs AC2.1–AC2.4, AC7.1–AC7.3, AC8.3–AC8.5, AC9.1–AC9.2.
- J2.S1.T1 — NumPy distributions/lattice/constant RED · AC2.1–AC2.4, AC7.1–AC7.3, AC8.3, AC8.5, AC9.1 · `W:` `tests/test_0_np_core.py` `tests/test_benchmarks.py` · owner `tests/test_0_np_core.py` · consolidate duplicate tables; final literal goldens and benchmark inventory are fixed before code.
- J2.S1.T2 — Spark exact-domain RED · AC8.3–AC8.4, AC9.2 · `W:` `tests/test_0_spark_core.py` · owner `tests/test_0_spark_core.py` · literal-limb fold equals Python bigint oracle; >2**53, signed extremes, full width, crossing-zero, logical dtype refusals and no Python UDF.

## Stage J2.S2 — implement numeric contracts

- Contract: exit owner tests GREEN by RED-marker deletion only; envelope `rand_engine/core/** benchmarks/speed.py tests/test_0_np_core.py tests/test_0_spark_core.py tests/test_benchmarks.py`; ACs AC2.1–AC2.4, AC7.1–AC7.3, AC8.3–AC8.5, AC8.7, AC9.1–AC9.2.
- J2.S2.T1 — rebuild NumPy numeric module and method map · AC2.1–AC2.4, AC7.1–AC7.3, AC8.3, AC8.5, AC8.7, AC9.1 · `W:` `rand_engine/core/_np_core.py` `rand_engine/core/_py_core.py` `benchmarks/speed.py` `tests/test_0_np_core.py` `tests/test_benchmarks.py` · owner `tests/test_0_np_core.py` · vectorized RNG calls, decimal lattice, constant zero-draw, useful legacy assertions retained.
- J2.S2.T2 — rebuild Spark integer/float expressions · AC8.3–AC8.4, AC8.7, AC9.2 · `W:` `rand_engine/core/_spark_core.py` `tests/test_0_spark_core.py` · owner `tests/test_0_spark_core.py` · exact Decimal limb fold, material-bias bound, supported-domain checks, UTC/date behavior preserved.
