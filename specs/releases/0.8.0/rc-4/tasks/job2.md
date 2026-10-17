# Job 2 — Spark key parity

**Wave:** 2
**Waits on:** Job 1
**W:** `tests/test_1_common_validator.py`, `tests/test_3_spark_generator.py`,
`rand_engine/validators/method_specs.py`, `rand_engine/validators/common_validator.py`,
`rand_engine/main/spark_generator.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1–AC2.4 | `tests/test_1_common_validator.py`, `tests/test_3_spark_generator.py` | RED acceptance tests replace only the approved PK/FK Spark refusal assertions. Prove catalog validation parity, explicit-seed parity at two partition counts for sequence/permuted/formatted PK and uniform/skew/born-before FK, inclusive and zero-parent cases, user `id` and helper-like key names, schema names/order after native joins, and ordinary Spark regression coverage. Exercise non-contiguous partition batches so parity is by supplied source index, not Arrow-batch offset. |
| J2.T2 | sr | AC2.1–AC2.4 | `rand_engine/validators/method_specs.py`, `rand_engine/validators/common_validator.py`, `rand_engine/main/spark_generator.py` | Admit keys through the shared grammar and derive their key seed exactly as pandas. Add a `mapInPandas` key-only adapter over Job 1's indexed `Keys` authority; preserve native ordinary generation and the exact user schema, including `id`. Validate a deterministically zero-eligible requested Spark size before executor evaluation so it raises the declared column-named `RandEngineError`. |

`J2.T2` may not edit tests. It must not add UDF/pandas_udF, `F.rand`, a Spark
hash approximation, a driver parent table or a new public export.
