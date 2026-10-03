---
slug: pk-fk-constraints
title: PK/FK constraints
tldr: "PK constraints record generated keys in checkpoint tables; FK constraints fill child columns by sampling keys recorded within a time watermark."
summary: "ConstraintsHandler gives DataGenerator relation-aware data — a PK constraint writes the generated keys with a creation time into checkpoint_<name>; an FK constraint overwrites its columns with keys sampled from rows created within the watermark; SQLite (default) and DuckDB handlers store the checkpoints."
tags: [constraints, referential-integrity, checkpoint, sqlite, duckdb]
sources:
  - rand_engine/main/_constraints_handler.py
  - rand_engine/integrations/**
  - rand_engine/utils/logger.py
---

## Grammar

- The spec's top-level `constraints` maps a label to `{name, tipo, fields, watermark}` ([[rand-spec-grammar]]).
- `tipo` is `PK` or `FK`; `name` names the checkpoint table `checkpoint_<name>` the two sides share.
- PK `fields` carry SQL types (`["category_id VARCHAR(8)"]`); FK `fields` are bare column names (`["category_id"]`).
- `watermark` is a positive number of seconds.

## Behaviour

- PK: after generation, the frame's key columns plus a `creation_time` (epoch seconds) are inserted into `checkpoint_<name>`, created on first use with those columns as its primary key; an already-recorded key is skipped.
- Each PK write prunes checkpoint rows older than the PK watermark plus a 300-second retention.
- FK: the FK columns of the child frame are overwritten with keys sampled, with replacement, from `checkpoint_<name>` rows created within the last `watermark` seconds (default 10).
- A parent generator runs before its child: relations link through time-stamped checkpoint rows, not through a shared spec.
- `.option("reset_checkpoint", True)` on a generator drops every `checkpoint_*` table before its batch ([[data-generator]]).

## Storage

- The checkpoint store is an in-memory SQLite database by default.
- `SQLiteHandler` and `DuckDBHandler` implement `BaseDBHandler`: `create_table`, `insert_df` (insert-or-ignore), `query_with_pandas`, `list_tables`, `drop_table`.
- Both handlers pool one connection per `db_path` at class level, so every generator in a process shares one `:memory:` checkpoint database.
- `insert_df` accepts only table names made of letters, digits and underscores.
