# Job 4 — FR3.1 `int_zfilled` length is refused outside 1..18 (REBUILD of the catalog rule)

**Wave:** 2 · **Waits on:** —

Bugs closed by this job, one cause: `int-zfilled-nonpositive-length-validates-then-raises` and `int-zfilled-length-above-18-validates-then-raises`. The `int_zfilled` rule is the only numeric-`length` rule in the catalog with no `semantic`, so the validator never states its domain; the engine fails at `10**length` (int64) and at `length < 1` instead. Authority and consumers: PLAN §1, §1.1, §1.2.

- REBUILD the rule: `method_specs.py` gains one `semantic` function for `int_zfilled` beside `_integers`, issuing `("length", "must be an integer within 1..18")` when `length` is outside `1 <= length <= 18` (`bool` is not an int here, as for the other rules). `_spark_width_errors` drops the `min(..., 16)` clamp: `validate_column` runs first, so the value is ≤ 18 and `10 ** kwargs["length"]` is safe. Spark's `<= 15` width check and message stay. `NPCore.gen_ints_zfilled` is not touched (invariant 12).
- Net lines are not ≤ 0 (one function is added, one clamp deleted): the stated reason is that no unit carries the bound, and the function is the catalog's existing mechanism, not a second path. The reviewer judges it.
- R2 (PLAN §2): the cases 5000 and 10**7 of `test_int_zfilled_length_above_15_is_one_collected_error` (`tests/test_1_common_validator.py:569-575`) move into the new partition test; `16` stays in the old one unchanged; the `test(J4.T1)` commit body names the ruling.
- Revert check for the reviewer: reverting J4.T2 turns the J4.T1 tests red.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC3.1 | `tests/test_1_common_validator.py` | RED: `length` 0, -1, 19, 5000, 10**7 each give exactly one issue naming `length` from `CommonValidator.validate_column` and from `validate_spark_spec`; `DataGenerator({'z': {...}})` raises `SpecValidationError` at construction for 0, -1, 19; `length` 1, 8, 18 give `[]` from `validate_column` and construct. Literal expected values; strict xfail on the refusal cases. Moves the 5000 and 10**7 cases per R2. Owner: tests/test_1_common_validator.py |
| J4.T2 | sr | AC3.1 | `rand_engine/validators/method_specs.py`, `rand_engine/validators/common_validator.py`, `tests/test_1_common_validator.py` | REBUILD of the `int_zfilled` rule as above and the clamp deleted; removes the J4.T1 markers; commit `refactor(J4.T2): REBUILD int_zfilled rule — …`, then the two `resolve` ledger commits. Owner: tests/test_1_common_validator.py |
