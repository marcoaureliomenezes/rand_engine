# Job 1 — FR1 one Spark integer-width rule (Bug window REBUILD)

**Wave:** 1 · **Waits on:** —

REBUILD `_spark_width_errors`: the validator stops re-deriving the engine's 2**53 limit and calls the one predicate beside `float_lattice_bounds` in `rand_engine/core/_np_core.py`. Authority and consumers: PLAN §1.1.

- Invariant 12: the operator approved `SparkCore.gen_ints` by name ("Aprovo", 2026-10-14): `_spark_core.py:38` calls the predicate and its literal is deleted.
- The moved assert `tests/test_1_common_validator.py:551-552` (`test_integer_width_2_53_is_accepted`, now refuses `max=2**53`) rides the main thread's ruling under invariant 3; the J1.T1 `test(...)` commit body cites it.
- Bug closed by this job: `spark-integers-width-2pow53-validates-then-raises`.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1, AC1.2, AC1.3, AC1.4 | `tests/test_1_common_validator.py`, `tests/test_0_spark_core.py`, `tests/test_3_spark_generator.py` | RED: width partition `2**53-1`, `2**53`, `2**53+1` and `int_zfilled` length 15 / 16 refused exactly where `SparkCore.gen_ints` refuses; `max=2**53` refused at construction with a collected `SpecValidationError` naming column and width; `max-min+1 == 2**53` pinned green. Moves the assert at test_1_common_validator.py:551-552 (ruling cited in the commit). Owner: tests/test_1_common_validator.py |
| J1.T2 | sr | AC1.1, AC1.2, AC1.3 | `rand_engine/core/_np_core.py`, `rand_engine/validators/common_validator.py`, `rand_engine/core/_spark_core.py`, `tests/test_1_common_validator.py`, `tests/test_0_spark_core.py`, `tests/test_3_spark_generator.py` | REBUILD: one width predicate in `_np_core.py` (`float_lattice_bounds` calls it); `_spark_width_errors` and `int_zfilled` call it, deleting `max - min > 2**53` and `length > 15`; `_spark_core.py:38` calls it (invariant 12 approved); the validator gains the edge `common_validator` -> `_np_core` (Reconciliation updates `ARCHITECTURE.md:54`); net lines <= 0; commit `refactor(J1.T2): REBUILD _spark_width_errors — ...`. Owner: tests/test_1_common_validator.py |
