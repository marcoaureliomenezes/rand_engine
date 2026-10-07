---
slug: pk-fk-constraints
title: PK/FK key columns
tldr: "Stateless pk and fk column methods create related tables from definitions, seeds and row indexes without a checkpoint store."
summary: "A pk is a sequence or a deterministic permutation of row indexes; an fk deterministically selects a parent row and rebuilds its pk value. Batch parts and stream microbatches advance row offsets, so keys remain consistent without shared state."
tags: [keys, referential-integrity, stateless, pk, fk]
sources:
  - rand_engine/core/_keys.py
  - rand_engine/main/_rand_generator.py
  - rand_engine/validators/advanced_validator.py
---

## Primary keys

- `pk` is a column method with `sequence` and `permuted` styles. Sequence computes `start + row_index * step`; permuted applies a keyed bijection over a declared domain and then adds `start`.
- An optional integer `format` field renders either style as strings. Keys do not depend on the generator seed and are unique while the validated domain and int64 guards hold.

## Foreign keys

- `fk` receives a parent `pk` column spec, `parent_size` and optional non-negative `skew`.
- The child seed, column name, full FK definition and child row index select a parent row. The parent value is rebuilt from its `pk` definition, so parent and child can be generated in separate processes.
- Uniform selection is the default; positive skew applies a Zipf distribution over permuted parent ranks so hot keys are scattered.

## Continuity and boundaries

- `get_df` starts key indexes at zero for every call. `stream_dict` and `writeStream` advance them across microbatches; a multi-file batch advances them across its parts.
- `SparkGenerator` refuses both key methods. No SQL, database integration, checkpoint table, watermark or retained key state participates in relations ([[spark-generator]], [[rand-spec-grammar]]).
