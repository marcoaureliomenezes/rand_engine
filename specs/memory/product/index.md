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
([[generation-methods]]), stateless PK/FK relations ([[pk-fk-constraints]]) and
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
| `templates-and-examples` | Templates and examples | Ready RandSpecs (ten cross-engine, ten pandas-only), a UTC WebServerLogs template, and Faker-pool and Arrow-schema spec builders. |

### generation

| slug | title | tldr |
|------|-------|------|
| `data-generator` | DataGenerator | The pandas generator validates a RandSpec, owns its random generator, and returns DataFrames, files, file streams or an endless record stream. |
| `generation-methods` | Generation methods | Ten common methods run on pandas and Spark; distributions, constant, correlated methods, pk, fk and null/anomaly modifiers run on pandas. |
| `spark-generator` | SparkGenerator | The Spark generator builds a Spark DataFrame from the ten common RandSpec methods with native expressions, no Python UDF, and refuses NumPy-only features. |

### output

| slug | title | tldr |
|------|-------|------|
| `writers-and-streaming` | Writers and streaming | DataGenerator writes CSV, JSON lines and Parquet batches, bounded by rows when asked, or repeated file-stream microbatches through a Spark-style builder. |

### quality

| slug | title | tldr |
|------|-------|------|
| `benchmarks` | Performance benchmarks | A CI-only same-runner A/B benchmark times every method, modifier and built-in sink, publishes its table and enforces base, sibling and modifier limits. |

### relations

| slug | title | tldr |
|------|-------|------|
| `pk-fk-constraints` | PK/FK key columns | Stateless pk and fk column methods create related tables from definitions, seeds and row indexes without a checkpoint store. |

### spec

| slug | title | tldr |
|------|-------|------|
| `rand-spec-grammar` | RandSpec grammar | A RandSpec maps output columns to a method, named kwargs and optional cols, transformers or modifiers, validated through one method catalog. |

## Capability map

```mermaid
graph TD
  S[RandSpec dict] --> V[Validators]
  V --> DG[DataGenerator]
  V --> SG[SparkGenerator]
  DG --> NP[NPCore / PyCore methods]
  SG --> SC[SparkCore expressions]
  DG --> C[pk / fk key columns]
  DG --> W[write / writeStream]
  DG --> SD[stream_dict]
  E[RandSpecs / templates] --> S
  B[faker_pool / from_schema] --> S
  DG --> DF[pandas DataFrame]
  SG --> SDF[Spark DataFrame]
  DF --> U[user-forwarded sinks: queues, lakes, databases]
  SD --> U
  W --> F[(csv / json / parquet files)]
```

## Known limits

- Distributions, constants, null and anomaly modifiers, correlated methods, transformers and pk/fk run on pandas only; Spark runs the ten common methods and refuses the rest.
- Seeds reach the pandas path only; Spark output is unseeded.
- PK/FK relations are stateless: parent and child link through definitions, seeds and row indexes, with no stored keys.
- Built-in sinks are files only; queues, object storage and databases are reached by forwarding DataFrames or `stream_dict` records.
- pandas generation runs in one process and holds one frame in memory: the whole size for `get_df`, one row batch at a time per file when `maxRowsPerBatch` is set.
