---
slug: ARCHITECTURE
title: Architecture
tldr: The system's principles, technology stack and structure.
summary: Principles change only with an accepted ADR; Tech Stack and Structure state what rand-engine's code is — a NumPy-first synthetic-data library with pandas and Spark generators, validators, Arrow-backed writers, stateless PK/FK key columns, a get-started CLI and a docs site built from its Markdown and docstrings.
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

- Python `>=3.10` library `rand_engine` (`requires-python`, CI-tested on 3.10–3.13), built by Poetry (`poetry-core`) from a static PEP 621 `[project]` table and published to PyPI as `rand-engine`; `pyproject.toml` holds the one version.
- NumPy `^2.1` — the vectorized column engine (`NPCore`); each `DataGenerator` owns one `np.random.default_rng(seed)` passed to generation methods; keys are computed from definitions, the key seed, column name and row index.
- pandas `^2.2` — DataFrame assembly, transformers and JSON-lines output.
- PyArrow `^23.0` — CSV and Parquet conversion and output for the batch and stream writers.
- PySpark `^3.5` (test group only) — `SparkGenerator` runs on the caller's `SparkSession` and `pyspark.sql.functions`; the package never imports PySpark.
- Faker `>=28.4.1,<29` (optional extra `faker`, also in the test group) — backs `RandSpecs.faker_pool` only; generation never calls it.
- pytest `^9.0`, pytest-cov (test group) — the suite and its fixture data.
- ruff `>=0.17.1` (test group) — pydocstyle `D` rules with the numpy convention on the public-surface modules.
- Zensical `==0.0.70` and mkdocstrings-python `==2.0.9` (optional `docs` group, Python `>=3.11`) — the strict docs-site build and its API reference from numpy-style docstrings, over `mkdocs.yml`.
- GitHub Actions — test matrix, advisory security scans, same-runner A/B benchmarks, RC and stable publishing through PyPI Trusted Publishing, and the docs build with its GitHub Pages deploy.

## Structure

```text
rand_engine/
  __init__.py        public surface: DataGenerator, SparkGenerator, RandSpecs; __version__ from installed metadata
  __main__.py        python -m rand_engine -> cli.main
  cli.py             the rand-engine console script: list, get-started
  cases/             <slug>.py.txt — the five get-started scaffolds, shipped as package data
  py.typed           typing marker
  main/              composition roots
    data_generator.py      DataGenerator — pandas pipeline, writers, stream_dict
    _rand_generator.py     RandGenerator — method dispatch, column assembly, transformers, null/anomaly modifiers
    spark_generator.py     SparkGenerator — Spark dispatch table over spark.range(size)
  core/              stateless generation primitives
    _keys.py               stateless PK/FK sequence, permutation and parent selection
    _np_core.py            NPCore — vectorized NumPy methods, alias samplers, float grid helpers
    _py_core.py            PyCore — correlated tuples and pattern strings; METHODS, the NumPy method map
    _spark_core.py         SparkCore — native Spark column expressions
  validators/        RandSpec grammar
    method_specs.py        METHOD_CATALOG — the one method authority
    common_validator.py    CommonValidator — ordinary methods, column keys, Spark intake
    advanced_validator.py  AdvancedValidator — DataGenerator intake, correlated and key methods
    exceptions.py          RandEngineError family
  file_handlers/     writer.py (FileWriter), _writer_batch.py (FileBatchWriter), _writer_stream.py (FileStreamWriter), file_handler.py (per-format file sessions)
  examples/          CommonRandSpecs (alias RandSpecs, with faker_pool and from_schema), AdvancedRandSpecs
  templates/         WebServerLogs template, IRandomSpec
  utils/             StreamHandler
```

- Dependency direction: `main` -> `core`, `validators`, `file_handlers`, `utils`; `validators.method_specs` -> `core._np_core` for date directives and float-domain predicates, and `validators.common_validator` -> `core._np_core` for `width_beyond_double`, the one Spark width predicate `SparkCore.gen_ints` and `float_lattice_bounds` also call, so grammar and engine decide each numeric rule once; `cli` imports only the standard library and reads `cases/` as package resources; `core._keys` and `file_handlers` import only `validators.exceptions`; `examples.common_rand_specs` runs `AdvancedValidator` on `from_schema` output; `core` imports no generator and `examples` import no engine.
- A RandSpec is a dict keyed by column name; the NumPy path has one method-name -> function map shared by columns and nested templates, while `METHOD_CATALOG` owns the accepted grammar: names, parameters, engines and Arrow output types.
- Generation is NumPy-first: every column is one array call, assembled into one DataFrame, then transformed.
- The Spark path builds columns as native expressions plus one broadcast join per `distincts` column; it runs no Python UDF.
- Relations are stateless `pk` and `fk` column methods; no integration package, database, checkpoint or retained key state is present.
- File writers stage output beside the destination and commit it only after every file closes; with `maxRowsPerBatch` a final file is generated one row batch at a time.

<!-- dadaia:fixed slop-code -->
### Slop — code (fixed)
- A docstring or comment follows the root `AGENTS.md` map §1 docstring sentence; a comment explains a non-obvious why.
- Code is born with a real caller in the same change; without a caller it does not exist.
- A fix replaces the old path; it never wraps it and never opens a second path.
- A port exists only with two production adapters; a parameter exists only when it is read.
- Detection: `dd-code-review` SLOP.md S1, S2, S4, S5.
<!-- /dadaia:fixed slop-code -->
