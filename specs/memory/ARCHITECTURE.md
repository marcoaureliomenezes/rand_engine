---
slug: ARCHITECTURE
title: Architecture
tldr: The system's principles, technology stack and structure.
summary: Principles change only with an accepted ADR; Tech Stack and Structure state what rand-engine's code is — a NumPy-first synthetic-data library with pandas and Spark generators, validators, Arrow-backed writers and stateless PK/FK key columns.
tags:
  - architecture
  - layers
  - design
---

## Principles

No principle is accepted yet: the repo carries no mechanical check (lint contract, import
contract, contract test) a principle could be measured by. Each principle lands here in the
commit that carries its accepted ADR.

## Tech Stack

- Python `^3.10` library `rand_engine`, built by Poetry (`poetry-core`) and published to PyPI as `rand-engine`; `pyproject.toml` holds the one version.
- NumPy `^2.1` — the vectorized column engine (`NPCore`); each `DataGenerator` owns one `np.random.default_rng(seed)` passed to generation methods; keys are computed from definitions, the key seed, column name and row index.
- pandas `^2.2` — DataFrame assembly, transformers and JSON-lines output.
- PyArrow `^23.0` — CSV and Parquet conversion and output for the batch and stream writers.
- PySpark `^3.5` (test group only) — `SparkGenerator` runs on the caller's `SparkSession` and `pyspark.sql.functions`; the package never imports PySpark.
- pytest `^9.0`, pytest-cov, Faker (test group) — the suite and its fixture data.
- GitHub Actions — test matrix, advisory security scans, same-runner A/B benchmarks, and RC and stable publishing through PyPI Trusted Publishing.

## Structure

```text
rand_engine/
  __init__.py        public surface: DataGenerator, SparkGenerator, RandSpecs
  main/              composition roots
    data_generator.py      DataGenerator — pandas pipeline, writers, stream_dict
    _rand_generator.py     RandGenerator — method dispatch table, column assembly, transformers
    spark_generator.py     SparkGenerator — Spark dispatch table over spark.range(size)
  core/              stateless generation primitives
    _keys.py               stateless PK/FK sequence, permutation and parent selection
    _np_core.py            NPCore — vectorized NumPy methods
    _py_core.py            PyCore — correlated tuples and pattern strings
    _spark_core.py         SparkCore — native Spark column expressions
  validators/        RandSpec grammar: CommonValidator, AdvancedValidator, exceptions
  file_handlers/     FileBatchWriter, FileStreamWriter, FileHandler, fs_utils
  examples/          CommonRandSpecs (alias RandSpecs), AdvancedRandSpecs
  templates/         WebServerLogs template, IRandomSpec
  utils/             logger, StreamHandler
```

- Dependency direction: `main` -> `core`, `validators`, `file_handlers`, `utils`; `validators.common_validator` -> `core._np_core.DATE_DIRECTIVES` for the shared date grammar; `core` imports no generator; `examples` are plain dicts with no import of the engine.
- A RandSpec is a dict keyed by column name; the NumPy path has one method-name -> function map shared by columns and nested templates, while validators own the accepted grammar.
- Generation is NumPy-first: every column is one array call, assembled into one DataFrame, then transformed.
- The Spark path builds columns as native expressions plus one broadcast join per `distincts` column; it runs no Python UDF.
- Relations are stateless `pk` and `fk` column methods; no integration package, database, checkpoint or retained key state is present.
- `img/` sits outside the package: README illustration images and a standalone script.

<!-- dadaia:fixed slop-code -->
### Slop — code (fixed)
- A comment explains a non-obvious why; the what, the history and any spec, task, ADR or version id live in git and the ledgers.
- A docstring states the contract in at most 3 lines; bug history lives in `BUGS.jsonl`.
- Code is born with a real caller in the same change; without a caller it does not exist.
- A fix replaces the old path; it never wraps it and never opens a second path.
- A port exists only with two production adapters; a parameter exists only when it is read.
- Detection: `dd-code-review` SLOP.md S1, S2, S4, S5.
<!-- /dadaia:fixed slop-code -->
