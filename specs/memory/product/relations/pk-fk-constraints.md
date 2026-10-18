---
slug: pk-fk-constraints
title: PK/FK key columns
tldr: "Stateless pk and fk column methods create related tables from definitions, seeds and row indexes on pandas and Spark, without a checkpoint store."
summary: "A pk is a sequence or deterministic permutation of row indexes; an fk deterministically selects an eligible parent row and rebuilds its pk value. Batch parts, stream microbatches and Spark partitions use source row indexes, so keys remain consistent without shared state."
tags: [keys, referential-integrity, stateless, pk, fk]
sources:
  - rand_engine/core/_keys.py
  - rand_engine/main/_rand_generator.py
  - rand_engine/validators/advanced_validator.py
---

## Primary keys

- `pk` is a column method with `sequence` and `permuted` styles. Sequence computes `start + row_index * step`; permuted applies a keyed bijection over a declared domain and then adds `start`.
- An optional integer-format string template renders either style as strings. A `pk` value does not depend on the generator seed and is unique while the validated domain and int64 guards hold.

## Foreign keys

- `fk` receives a parent `pk` column spec, `parent_size` and optional non-negative `skew`.
- The key seed derived from the generator seed, the column name, the full FK definition and the child row index select a parent row. The parent value is rebuilt from its `pk` definition, so parent and child can be generated in separate processes.
- Uniform selection is the default; positive skew applies a Zipf distribution over permuted parent ranks so hot keys are scattered.
- Optional `born_before` declares `parent_start`, `parent_rate`, `child_start` and `child_rate`. Starts are finite builtin integers or floats; rates are finite, positive builtin integers or floats; booleans, NumPy scalars, Decimal and Fraction values are refused.
- For child row `j`, eligible parents are the inclusive, clamped count whose event time `parent_start + i / parent_rate` is at or before `child_start + j / child_rate`. Exact rational arithmetic keeps accepted large integers and small rates defined. A requested child with no eligible parent raises `RandEngineError` naming the FK column.

## Continuity and boundaries

- `get_df` starts key indexes at zero for every call. `stream_dict` and `writeStream` advance them across microbatches; a multi-file batch advances them across its parts.
- `SparkGenerator` accepts both key methods and applies the shared key authority to the source indexes carried through its partitions. With the same explicit seed and spec, pandas and Spark produce the same key values independent of Spark partition count; the seed affects key columns only ([[spark-generator]], [[rand-spec-grammar]]).
- No database read, lookup SQL, checkpoint table, watermark or retained key state participates in relations. The SQLite writer is an output-only sink and never supplies values to generation ([[writers-and-streaming]]).
