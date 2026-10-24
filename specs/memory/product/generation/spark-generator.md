---
slug: spark-generator
title: SparkGenerator
tldr: "The Spark generator builds ordinary columns with native expressions and stateless pk/fk columns through the shared indexed key authority."
summary: "SparkGenerator(spark, F, spec, seed) validates ordinary columns through the Spark grammar and key columns through the shared advanced key rules, starts from spark.range(size), keeps ordinary generation native and computes partition-independent keys from source row indexes."
tags: [spark, pyspark, generator]
sources:
  - rand_engine/main/spark_generator.py
  - rand_engine/core/_spark_core.py
  - rand_engine/validators/common_validator.py
---

## Role and use

- `SparkGenerator(spark, F, spec).size(n).get_df()` builds a Spark DataFrame; PySpark is supplied by the caller and is not a runtime dependency.
- CI runs the Spark tests on PySpark 3.5 with Python 3.11 and on PySpark 4.x with Python 3.12 to 3.14, on Linux and macOS; on Windows they run with Python 3.11 and skip with Python 3.12 or later.
- `get_df()` without `.size(n)` raises `RandEngineError` naming `.size(n)`.
- Generation starts from `spark.range(size)`, adds one column per spec entry and drops technical source-index columns. A user column named `id` or like an internal helper remains in the declared schema and order.

## Grammar and refusals

- The common validator accepts ordinary Spark methods and named `kwargs`; `SparkGenerator` extracts `pk` and `fk` columns and applies the same advanced key validation as `DataGenerator` ([[rand-spec-grammar]], [[generation-methods]]).
- `exponential`, `lognormal`, `poisson`, `zipf`, `constant` and the four correlated methods `distincts_map`, `distincts_multi_map`, `distincts_map_prop` and `complex_distincts` are refused as NumPy engine only, with the fix line to use `DataGenerator`; so are `null_rate` and `anomaly_rate`; `anomaly_values` alone is accepted and has no effect.
- `args` and unknown column keys are refused.
- `integers` refuses `uint64` and any width `max - min + 1` above 2^53, at validation and in `SparkCore` alike; `int_zfilled` refuses `length` above 15. Every other accepted integer domain, width 2^53 included, is exact and inclusive.

## Behaviour

- Ordinary values come from native Spark expressions and one broadcast lookup join per `distincts` column. Key-only `mapInPandas` batches call the shared indexed `Keys` methods and join by a collision-safe source index; no row-wise Python UDF, Spark hash approximation or driver parent table is used.
- `floats` draws on the decimal grid inside `[min, max]`; a grid with more than 2^53 steps, or a grid end (bound times 10^`decimals`) outside `int64`, is drawn uniformly in `[min, max]` ([[generation-methods]]).
- `dates` translates the supported Python directives `%Y %m %d %H %M %S %f` to Spark patterns and renders UTC wall-clock text whatever the session time zone.
- Ordinary Spark output is not seeded. An explicit `seed` derives the same key seed as `DataGenerator` and affects only `pk` and `fk`; keys remain identical across partition counts and non-contiguous Arrow batches. Writing is delegated to the returned DataFrame's own writer.
