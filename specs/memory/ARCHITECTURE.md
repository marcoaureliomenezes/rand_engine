---
slug: ARCHITECTURE
title: Architecture
tldr: The system's principles, technology stack and structure.
summary: Principles change only with an accepted ADR; Tech Stack and Structure state what rand-engine's code is — a NumPy-first synthetic-data library with pandas and Spark generators, validators, writers and checkpoint-backed PK/FK.
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
- NumPy `^2.1` — the vectorized column engine (`NPCore`); each generator owns one `np.random.default_rng(seed)`, passed to the core as `rng`; keys are computed from the column definition, the seed and the row index.
- pandas `^2.2` — DataFrame assembly, transformers, CSV/JSON/Parquet output.
- PyArrow `^23.0` — the Parquet engine of the batch and stream writers.
- PySpark `^3.5` (test group only) — `SparkGenerator` runs on the caller's `SparkSession` and `pyspark.sql.functions`; the package never imports PySpark.
- pytest `^9.0`, pytest-cov, Faker (test group) — the suite and its fixture data.
- GitHub Actions — test matrix, security scans, RC and stable publishing through PyPI Trusted Publishing.

## Structure

```text
rand_engine/
  __init__.py        public surface: DataGenerator, SparkGenerator, RandSpecs
  main/              composition roots
    data_generator.py      DataGenerator — pandas pipeline, writers, stream_dict
    _rand_generator.py     RandGenerator — method dispatch table, column assembly, transformers
    _constraints_handler.py ConstraintsHandler — PK/FK checkpoint tables
    spark_generator.py     SparkGenerator — Spark dispatch table over spark.range(size)
    _cdc_generator.py      CDC file generator for DBFS; imported by no module
  core/              stateless generation primitives
    _np_core.py            NPCore — vectorized NumPy methods
    _py_core.py            PyCore — correlated tuples and pattern strings
    _spark_core.py         SparkCore — native Spark column expressions
  validators/        RandSpec grammar: CommonValidator, AdvancedValidator, exceptions
  file_handlers/     FileBatchWriter, FileStreamWriter, FileHandler, fs_utils
  integrations/      BaseDBHandler, SQLiteHandler, DuckDBHandler
  examples/          CommonRandSpecs (alias RandSpecs), AdvancedRandSpecs
  templates/         WebServerLogs template, IRandomSpec
  utils/             logger, StreamHandler, Changer
```

- Dependency direction: `main` -> `core`, `validators`, `file_handlers`, `integrations`, `utils`; `core` imports no generator; `examples` are plain dicts with no import of the engine.
- A RandSpec is a dict keyed by column name; each generator owns its own method-name -> function table, and each validator owns its own method catalog.
- Generation is NumPy-first: every column is one array call, assembled into one DataFrame, then transformed.
- The Spark path builds columns as native expressions plus one broadcast join per `distincts` column; it runs no Python UDF.
- Checkpoint handlers hold one class-level connection per `db_path`, so every generator in a process shares the same `:memory:` checkpoint database.
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
