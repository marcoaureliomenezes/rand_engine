---
slug: writers-and-streaming
title: Writers and streaming
tldr: "DataGenerator writes CSV, JSON lines, Parquet or an output-only SQLite table through a Spark-style builder; file streams support the three file formats."
summary: "The batch writer distributes file output across numFiles with optional row batching, or atomically persists one generated frame to a selected SQLite table. CSV and Parquet use PyArrow, JSON uses pandas, SQLite uses the standard library, and every format accepts only documented options."
tags: [writers, streaming, files, csv, json, parquet, sqlite]
sources:
  - rand_engine/file_handlers/**
---

## Scope

- Built-in sinks are local or mounted CSV, JSON-lines and Parquet files plus an output-only SQLite batch table. Callers forward DataFrames or records to every other sink ([[data-generator]]).
- Both writers expose `format`, `mode`, `option` and `options`; an unsupported or malformed option raises `RandEngineError` before any output is touched.

## Batch writer

- `generator.write.format(f).mode(m).option(k, v).save(path)` uses the generator's configured size as the total row count.
- `numFiles` splits that total as evenly as possible across parts; offsets follow the cumulative part sizes, so keys do not repeat between files. A part that receives zero rows is written as an empty file with the schema of the other parts, else of the method catalog.
- A single file uses the requested path. Multiple files use a directory of `part_<id>` files.
- `maxRowsPerBatch` (absent or `None` disables it; otherwise a positive integer) generates each final file in contiguous row batches of at most that many rows, so no generated frame exceeds it. Global transformers run once per row batch, and keys keep their row-index semantics across batches. Different batch sizes carry no equality promise for ordinary values.
- The spec is evaluated once per final file; one schema holds across a final file's batches, and a batch whose columns or types differ raises `RandEngineError` before the destination changes. Typed nulls take the type of the file's schema, else of the method catalog.
- Output is staged beside the destination and committed only after every file closes, so a failure in a transformer, modifier, schema check or option leaves any existing output intact.
- `mode("append")` adds rows: a single file is rebuilt from its existing content plus the new rows, and a multi-file save adds only new part files beside the existing ones, which are never copied or rewritten. Any other mode overwrites, replacing a part directory as a whole.
- `format("sqlite").option("table", name).mode("overwrite" | "append").save(path)` writes the configured size in one generated frame. `table` is the only option and must be a non-empty NUL-free string; generated labels must be unique NUL-free strings, integers must fit signed 64 bits and unsupported values or modes fail before publication.
- SQLite identifiers are quoted and every value is parameter-bound. Homogeneous scalar columns declare their SQLite type; mixed or all-null columns have no affinity so bound storage classes are preserved. Booleans and integers use INTEGER, floats REAL, strings and ISO dates/datetimes TEXT, bytes BLOB and missing values NULL.
- Overwrite copies an existing database to an adjacent staging file, replaces only the selected table, retains unrelated tables and atomically replaces the destination after commit. Append creates a missing database/table or checks the existing ordered schema, then inserts in one transaction; a mismatch or database failure rolls back.

## Stream writer

- `generator.writeStream.trigger(frequency).option("timeout", seconds).start(path)` writes repeated `size`-row microbatches, sleeping `frequency` seconds (a float, default 1) after each write, to `part-<uuid>` files; overwrite mode empties the directory first, and `maxRowsPerBatch` is not an accepted stream option.
- Each microbatch advances the row offset; `start` blocks until the timeout (default 20 seconds) expires.
- SQLite is batch-only: `writeStream.format("sqlite").start(...)` raises before touching its path.

## Formats

- CSV and Parquet convert the DataFrame to an Arrow table; mixed-type object columns fail with the column named. Parquet defaults to Snappy.
- Parquet reads back equal to the frame in values, timezone-aware ones included, and in dtype for every non-text column. A generated text column keeps its values and the String logical type; it reads back as `pd.StringDtype("pyarrow")` under the default `pd.read_parquet` and as the frame's `string[pyarrow]` with `dtype_backend="pyarrow"`.
- CSV accepts `sep`, `compression` (gzip, bz2, xz, zip) and `index=False`; one header per file, an empty field for a null, a naive timestamp's fraction sized by its column's unit (`ns` nine digits, `us` six, `ms` three, `s` none), and timezone-aware columns rendered to pandas strings before Arrow writes them.
- JSON is pandas JSON-lines output (`orient` is `records` only) and accepts `force_ascii`, `indent` and `compression`; a null is `null`.
- Parquet accepts `compression` only and writes a typed null that keeps the column's logical type.
