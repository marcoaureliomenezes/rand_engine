---
slug: index
title: Product catalog
tldr: Index of every product feature with summaries and context metadata.
summary: Consolidated view of every product feature. Entry point for self-pulling a specific feature atom. Maintained by dd-product-engineer at each release CLOSURE.
tags:
  - catalog
  - product
  - index
---

## Atomic view

rand-engine generates synthetic data very fast, for any platform and any sink, from a declarative
RandSpec: the NumPy core ([[data-generator]]) yields pandas DataFrames, record streams and files
([[writers-and-streaming]]) the user forwards to any queue, lake, database or file; Spark is
supported through the same spec ([[spark-generator]]). Correlated columns and pattern strings
([[generation-methods]]), checkpoint-backed PK/FK relations ([[pk-fk-constraints]]) and
ready-made specs ([[templates-and-examples]]) sit on a vectorized NumPy core.

## Users

| User | Description |
|------|-------------|
| Data engineers | Learn, stress-test pipeline throughput and bandwidth, and feed pipeline tests with synthetic data — batch or streaming, to any sink. |
| QA engineers | Build reproducible, relation-aware fixtures without hand-written data. |
| Developers and learners | Mock data for apps and demos from prebuilt specs, guided by validation messages that show a correct example. |

## Feature catalog

### api

| slug | title | tldr |
|------|-------|------|
| `public-api` | Public API | rand_engine exports DataGenerator, SparkGenerator and RandSpecs; every other module is internal. |

### content

| slug | title | tldr |
|------|-------|------|
| `templates-and-examples` | Templates and examples | Ready RandSpecs — ten cross-engine CommonRandSpecs (exported as RandSpecs), ten pandas-only AdvancedRandSpecs, and the WebServerLogs template. |

### generation

| slug | title | tldr |
|------|-------|------|
| `data-generator` | DataGenerator | The pandas generator: validates a RandSpec, seeds NumPy, and returns DataFrames, files, file streams or an endless record stream. |
| `generation-methods` | Generation methods | Ten common methods run on pandas and Spark; four correlated methods (maps, weighted maps, multi-maps, patterns) run on pandas only. |
| `spark-generator` | SparkGenerator | The Spark generator: builds a Spark DataFrame from a RandSpec of common methods with native column expressions and no UDF. |

### output

| slug | title | tldr |
|------|-------|------|
| `writers-and-streaming` | Writers and streaming | Spark-style file writers on DataGenerator — write saves CSV, JSON lines or Parquet files; writeStream emits one file per microbatch until a timeout. |

### relations

| slug | title | tldr |
|------|-------|------|
| `pk-fk-constraints` | PK/FK constraints | PK constraints record generated keys in checkpoint tables; FK constraints fill child columns by sampling keys recorded within a time watermark. |

### spec

| slug | title | tldr |
|------|-------|------|
| `rand-spec-grammar` | RandSpec grammar | A RandSpec is a dict of column name to {method, kwargs or args, cols, transformers}, validated before any row is generated. |

## Capability map

```mermaid
graph TD
  S[RandSpec dict] --> V[Validators]
  V --> DG[DataGenerator]
  V --> SG[SparkGenerator]
  DG --> NP[NPCore / PyCore methods]
  SG --> SC[SparkCore expressions]
  DG --> C[PK/FK constraints]
  C --> DB[(SQLite / DuckDB checkpoints)]
  DG --> W[write / writeStream]
  DG --> SD[stream_dict]
  E[RandSpecs / templates] --> S
  FK[Faker value pools] --> S
  DG --> DF[pandas DataFrame]
  SG --> SDF[Spark DataFrame]
  DF --> U[user-forwarded sinks: queues, lakes, databases]
  SD --> U
  W --> F[(csv / json / parquet files)]
```

## Known limits

- Correlated methods, transformers and constraints run on pandas only; Spark runs the ten common methods.
- Seeds reach the pandas path only; Spark output is unseeded.
- PK/FK relations link generators through time-stamped checkpoint rows in one process.
- Built-in sinks are files only; queues, object storage and databases are reached by forwarding DataFrames or `stream_dict` records.
- pandas generation holds the whole batch in memory in one process.
