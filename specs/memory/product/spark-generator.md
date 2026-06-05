---
slug: spark-generator
title: SparkGenerator
category: product
tldr: 'Spark supports common methods through expressions; advanced methods are null stubs and must not be treated as implemented behavior.'
summary: 'Current Spark support boundary: SparkGenerator is public, common methods are real, advanced methods are compatibility stubs until an approved release changes them.'
tags:
- spark
- pyspark
- generator
agent_tier: self-pull
token_estimate: 125
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

`SparkGenerator` is exported by the package and treated as public current API.
It creates Spark dataframes with `spark.range(size)` and adds generated columns
through Spark expressions.

Supported current truth:

- Common generation methods are implemented in Spark.
- Tests cover Spark core and generator behavior in the current environment.
- PySpark is a test dependency, not a runtime dependency in `pyproject.toml`.

Unsupported current truth:

- Advanced/correlation methods are mapped but return null placeholders.
- Spark advanced methods must not be advertised as implemented until the runtime,
  validators, docs, and tests are aligned.
