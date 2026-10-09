---
slug: spark-generator
title: SparkGenerator
tldr: "The Spark generator builds a Spark DataFrame from common RandSpec methods with native expressions and no Python UDF."
summary: "SparkGenerator(spark, F, spec) validates the common grammar, starts from spark.range(size), adds native SparkCore columns and refuses the NumPy-only pk and fk methods."
tags: [spark, pyspark, generator]
sources:
  - rand_engine/main/spark_generator.py
  - rand_engine/core/_spark_core.py
---

## Role and use

- `SparkGenerator(spark, F, spec).size(n).get_df()` builds a Spark DataFrame; PySpark is supplied by the caller and is not a runtime dependency.
- Generation starts from `spark.range(size)`, adds one column per spec entry and drops the technical `id` unless the spec defines it.

## Grammar

- The common validator accepts the ten common methods and named `kwargs` ([[rand-spec-grammar]], [[generation-methods]]).
- `pk` and `fk` are refused with guidance to use `DataGenerator`; related keys are NumPy-engine features.
- Correlated pandas methods warn and produce a null string column; `args` is refused.

## Behaviour

- Values come from native Spark expressions and one broadcast lookup join per `distincts` column; no Python UDF runs.
- `dates` translates the supported Python directives `%Y %m %d %H %M %S %f` to Spark patterns.
- Spark output is not seeded, and writing is delegated to the returned DataFrame's own writer.
