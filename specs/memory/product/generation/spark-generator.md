---
slug: spark-generator
title: SparkGenerator
tldr: "The Spark generator: builds a Spark DataFrame from a RandSpec of common methods with native column expressions and no UDF."
summary: "SparkGenerator(spark, F, spec) validates the spec against the common methods, starts from spark.range(size) and adds one column per spec entry through SparkCore expressions; PySpark is the caller's dependency, never the package's."
tags: [spark, pyspark, generator]
sources:
  - rand_engine/main/spark_generator.py
  - rand_engine/core/_spark_core.py
---

## Role

- Supported, not central: Spark users run the same common-method RandSpec on a cluster; the NumPy core needs no Spark ([[data-generator]]).

## Use

- `SparkGenerator(spark, F, spec).size(n).get_df()` — `spark` is the caller's `SparkSession`, `F` is `pyspark.sql.functions`.
- The spec is validated by `CommonValidator` at construction, so only the ten common methods are accepted ([[rand-spec-grammar]], [[generation-methods]]).
- Each column entry needs `kwargs`; `args`, `cols`, `transformers` and `constraints` are pandas-only grammar.

## Behaviour

- Generation starts from `spark.range(size)` and adds one column per spec entry with `withColumn`; the technical `id` column is dropped unless the spec defines `id`.
- Every value comes from a native expression (`rand`, `randn`, `uuid`, `lpad`, `from_unixtime`, `date_format`) or a broadcast join, so generation scales with the cluster and runs no Python UDF.
- `dates` translates the Python `date_format` into the Spark pattern.
- Spark output is not seeded.
- The package never imports PySpark; the caller provides it.
