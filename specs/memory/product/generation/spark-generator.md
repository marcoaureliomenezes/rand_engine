---
slug: spark-generator
title: SparkGenerator
tldr: "The Spark generator builds a Spark DataFrame from the ten common RandSpec methods with native expressions, no Python UDF, and refuses NumPy-only features."
summary: "SparkGenerator(spark, F, spec) validates the common grammar, starts from spark.range(size), adds native SparkCore columns and refuses pk, fk, the distribution and constant methods, modifiers and integer widths Spark cannot carry exactly."
tags: [spark, pyspark, generator]
sources:
  - rand_engine/main/spark_generator.py
  - rand_engine/core/_spark_core.py
---

## Role and use

- `SparkGenerator(spark, F, spec).size(n).get_df()` builds a Spark DataFrame; PySpark is supplied by the caller and is not a runtime dependency.
- `get_df()` without `.size(n)` raises `RandEngineError` naming `.size(n)`.
- Generation starts from `spark.range(size)`, adds one column per spec entry and drops the technical `id` unless the spec defines it.

## Grammar and refusals

- The common validator accepts the ten common methods and named `kwargs` ([[rand-spec-grammar]], [[generation-methods]]).
- `pk`, `fk`, `exponential`, `lognormal`, `poisson`, `zipf` and `constant` are refused with guidance to use `DataGenerator`; so are `null_rate` and `anomaly_rate`; `anomaly_values` alone is accepted and has no effect.
- `args` and unknown column keys are refused; correlated pandas methods warn and produce a null string column.
- `integers` refuses `uint64` and any width above 2^53; `int_zfilled` refuses `length` above 15. Every other accepted integer domain is exact and inclusive.

## Behaviour

- Values come from native Spark expressions and one broadcast lookup join per `distincts` column; no Python UDF runs.
- `floats` draws on the decimal grid inside `[min, max]`; a grid with more than 2^53 steps, or a grid end (bound times 10^`decimals`) outside `int64`, is drawn uniformly in `[min, max]` ([[generation-methods]]).
- `dates` translates the supported Python directives `%Y %m %d %H %M %S %f` to Spark patterns and renders UTC wall-clock text whatever the session time zone.
- Spark output is not seeded, and writing is delegated to the returned DataFrame's own writer.
