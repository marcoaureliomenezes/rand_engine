# Job 5 — documentation and the Spark proof (wave 3, waits on Job 2)

Docs state the type once (method table or null-rate section): `string[pyarrow]`, `pd.NA` nulls, Arrow booleans from `.str.*`, the Parquet read-back rule, Spark's Arrow option, and that an embedded transformer's output dtype is whatever it returns. Every changed block is executed by `tests/test_docs.py` (owner of the docs tasks, unchanged); the phrase mirror between `README.md`, `llms.txt` and `skills/rand-engine/SKILL.md` moves together.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC2.8 | `tests/test_3_spark_generator.py` | integration on Temurin 17: with `spark.sql.execution.arrow.pyspark.enabled` on, `createDataFrame` of a frame holding `pd.NA` text yields a string column with SQL NULLs; off, a frame with no text nulls converts and a `pd.NA` frame raises the documented error. It characterises pandas and Spark on the Job 2 behaviour, so it is green on arrival |
| J5.T2 | jr | AC2.8 | `rand_engine/cases/databricks.py.txt` | UPDATE the starter: enable Spark's Arrow option before `spark.createDataFrame`; owner `tests/test_9_cli.py` (scaffold test, unchanged) |
| J5.T3 | jr | AC2.7, AC2.9 | `docs/1_DATA_GENERATOR.md`, `rand_engine/main/data_generator.py` | UPDATE `:60-77`, `:84-86`, `:112`, `:153-156` and the docstrings at 19-22, 244-245, 258: the type, `pd.NA`, Arrow booleans, the transformer note, one executed block asserting `string[pyarrow]` |
| J5.T4 | jr | AC2.6, AC2.9 | `docs/3_WRITING_FILES.md` | UPDATE `:42-44` (narrow line 44 to the Parquet read-back rule) and `:94-95`; add the Spark Arrow note |
| J5.T5 | jr | AC2.9 | `docs/5_RECIPES.md`, `README.md`, `llms.txt`, `skills/rand-engine/SKILL.md` | UPDATE `5_RECIPES.md:41-46`, `README.md:37,45,57`, `llms.txt:25`, `SKILL.md:32,43,99` to the same statements |
