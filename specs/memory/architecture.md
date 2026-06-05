---
slug: architecture
title: rand-engine architecture
category: core
tldr: 'Python package with generator facades, vectorized Pandas/NumPy generation, Spark common methods, validators, writers, and DuckDB checkpoint state.'
summary: 'Current architecture truth for rand-engine: public API, package layers, generation flow, validation/runtime drift, relational state boundaries, and ADRs for restart planning.'
tags:
- architecture
- python
- synthetic-data
- duckdb
- spark
agent_tier: self-pull
token_estimate: 830
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

# Architecture: rand-engine

rand-engine is a compact Python library with a small public API and several
internal subsystems: Pandas/NumPy generation, Spark generation, spec validation,
file writing/streaming, example/template specs, and database handlers used for
checkpointed relational state.

## Camadas

```text
rand_engine/
  __init__.py                  # public facade: DataGenerator, SparkGenerator, RandSpecs
  main/
    data_generator.py          # Pandas composition root
    spark_generator.py         # Spark composition root
    _rand_generator.py         # Pandas method dispatch
    _constraints_handler.py    # DuckDB-backed PK/FK checkpoint state
    _cdc_generator.py          # stale/unsupported until classified
  core/
    _np_core.py                # vectorized NumPy primitives
    _py_core.py                # Python advanced/correlation-like tuple methods
    _spark_core.py             # Spark common methods; advanced stubs
  validators/
    common_validator.py        # common RandSpec grammar
    advanced_validator.py      # advanced RandSpec grammar
    exceptions.py              # validation errors
  file_handlers/
    writer.py                  # writer facade
    _writer_batch.py           # batch output
    _writer_stream.py          # stream output
    file_handler.py, fs_utils.py
  integrations/
    _base_handler.py           # partial DB handler base
    _duckdb_handler.py         # DuckDB pool/table/query adapter
    _sqlite_handler.py         # SQLite adapter
  examples/, templates/        # built-in RandSpecs and product examples
  utils/                       # logging, stream utilities, update helper
```

## Fluxo de dados — pipeline asset chain

`DataGenerator` validates the provided spec, seeds NumPy, creates writer facades,
creates a constraints handler, and exposes `get_df()` plus writer/stream entry
points. `get_df()` evaluates lazy size/spec functions, generates first-level
columns through `_rand_generator.py`, applies embedded and dataframe-level
transformers, then applies PK/FK consistency through `_constraints_handler.py`.

The fast path is vectorized: `NPCore` produces arrays for integers, floats,
booleans, weighted distinct values, dates, and timestamps. Pandas dataframe
assembly happens after arrays exist.

Advanced correlation-like behavior currently lives in `PyCore` as in-memory
tuple/list sampling for methods such as `distincts_map`, `distincts_multi_map`,
`distincts_map_prop`, and `complex_distincts`. This is not DuckDB query-planned
correlation.

`SparkGenerator` uses `spark.range(size)` and Spark expressions for common
methods. Advanced Spark methods currently return null placeholders and are not
approved as supported behavior.

## Contratos entre módulos

DuckDB currently provides integration and checkpoint state. `ConstraintsHandler`
stores primary-key candidates in `checkpoint_*` tables and samples foreign-key
values by watermark. Future DuckDB-backed correlation must introduce explicit
ports such as `CheckpointStore`, `RelationStore`, or `CorrelationStore` before
new product semantics are added.

SQLite mirrors part of the handler API, but it is not a drop-in replacement for
DuckDB today. Backend parity must be specified and tested before treating these
handlers as interchangeable.

## Limites conhecidos

- `distincts_external` is accepted by advanced validation but not mapped by the
  Pandas runtime.
- `checkpoint(db_path)` updates an option but does not rewire the already-created
  active constraints handler.
- `DataGenerator` deletes `constraints` from evaluated spec dictionaries and can
  mutate user input.
- Spark advanced methods are null stubs and must either fail explicitly or be
  implemented.
- `_cdc_generator.py` appears stale against the current API and has no effective
  test coverage.
- Method catalogs are duplicated across validators, Pandas runtime, Spark
  runtime, examples, and docs.

## Visão geral

### ADR-001: Public API Baseline

**Date:** 2026-06-05
**Status:** Proposed

**Context:** `rand_engine.__all__` exports `DataGenerator`, `SparkGenerator`, and
`RandSpecs`, while tests/docs disagree on whether Spark is public.

**Decision:** Treat all three exported names as the current public surface until
an approved release narrows or expands it.

**Consequences:** Tests and docs must align to this surface. Runtime version
exposure remains an unresolved release-policy decision.

### ADR-002: DuckDB Is State Infrastructure Today

**Date:** 2026-06-05
**Status:** Proposed

**Context:** The operator wants to improve correlations using DuckDB, but audits
found DuckDB is currently checkpoint/query infrastructure.

**Decision:** Do not treat DuckDB as the canonical correlation engine until a
dedicated design spec defines grammar, lifecycle, safety, determinism, and
engine parity.

**Consequences:** Correlation work starts with specs and tests, not ad hoc SQL
hooks.

### ADR-003: Method Registry Must Become Canonical

**Date:** 2026-06-05
**Status:** Proposed

**Context:** Validators, Pandas dispatch, Spark dispatch, docs, and examples
encode method support separately.

**Decision:** Future implementation should converge on one method registry with
per-engine support metadata.

**Consequences:** This reduces drift and makes unsupported Spark advanced methods
or experimental DuckDB methods explicit.
