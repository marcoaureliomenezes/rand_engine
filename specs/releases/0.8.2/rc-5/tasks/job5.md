# Job 5 — the CLI starter test and the Spark conf home (wave 1)

Runs beside Jobs 1 to 4. T1, T2, T3 in order: T1 and T2 share `tests/test_9_cli.py`; T2 and T3 share `tests/test_3_spark_generator.py`. Tombstones at `tests/test_9_cli.py:156,204-205` stay (SPEC §3).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC35.1, AC35.2 | `tests/test_9_cli.py` | the starter test (`:166-200`) is named for what it asserts; rows are `(slug, expectation)` with each starter's notebook expectation (`lake`, `kafka`, `faker`, `databricks` start with `# Databricks notebook source`); ids come from the rows; the Spark fixture is driven by its own parameter and the body has no slug `if`. No assert removed. Owner: itself |
| J5.T2 | jr | AC35.3 | `tests/test_9_cli.py`, `tests/test_3_spark_generator.py`, `tests/conftest.py` | `ARROW_CONF` and its save and restore have one home (`conftest.py`), read by both files; the conf assert runs after the starter and before any restore (`:197-200`). Owner: J5.T1 |
| J5.T3 | jr | AC36.5 | `tests/test_3_spark_generator.py` | `test_spark_zero_callable_size_skips_the_eligibility_check` (`:680`) is renamed for its asserts, an empty frame that keeps the fk column; asserts unchanged |

Done when: `verify:`; `tests/test_9_cli.py`, `tests/test_3_spark_generator.py` pass. Sweep: `git grep -n 'arrow.pyspark.enabled' -- tests` lists one literal.
