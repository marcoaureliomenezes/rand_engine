# Memory Catalog - rand-engine

> Product memory index for rand-engine. Each feature atom is current product
> truth, not historical changelog.

## Features by category

### product

| slug | title | tldr |
|------|-------|------|
| `public-api` | public API | Supported import surface is `DataGenerator`, `SparkGenerator`, and `RandSpecs`; runtime version policy is unresolved. |
| `data-generator` | DataGenerator | Pandas/NumPy composition root for deterministic dataframe generation, transforms, constraints, writers, and streams. |
| `rand-spec-grammar` | RandSpec grammar | Declarative dictionary grammar validated by common and advanced validators before generation. |
| `method-registry` | method registry | Current method support is duplicated across validators, Pandas runtime, Spark runtime, examples, and docs; a canonical registry is future work. |
| `correlation-model` | correlation model | Current correlations are in-memory advanced methods; DuckDB-backed correlation is future design work, not current behavior. |
| `constraints-duckdb-checkpoints` | constraints and DuckDB checkpoints | PK/FK consistency uses DuckDB checkpoint tables and watermarks; checkpoint persistence lifecycle has known defects. |
| `spark-generator` | SparkGenerator | Spark supports common methods through expressions; advanced methods are null stubs and must not be treated as implemented behavior. |
| `writers-and-streaming` | writers and streaming | Batch and stream writers support file outputs, but tests must prove read-back correctness and artifact hygiene. |
| `templates-and-examples` | templates and examples | Built-in common/advanced specs and web-server-log template are product assets that require compatibility tests. |
| `qa-and-release-governance` | QA and release governance | Current suite passes 494 tests at 85.98% coverage; release/version/security gates need explicit restart decisions. |
