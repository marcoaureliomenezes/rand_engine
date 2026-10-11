---
slug: writers-and-streaming
title: Writers and streaming
tldr: "DataGenerator writes CSV, JSON lines and Parquet batches, bounded by rows when asked, or repeated file-stream microbatches through a Spark-style builder."
summary: "The batch writer distributes one requested total row count across numFiles, generating each final file in row batches of at most maxRowsPerBatch when set, and commits staged output only on success; the stream writer emits size rows per microbatch. CSV and Parquet use PyArrow, JSON uses pandas, and each format accepts only documented options."
tags: [writers, streaming, files, csv, json, parquet]
sources:
  - rand_engine/file_handlers/**
---

## Scope

- Built-in sinks are local or mounted CSV, JSON-lines and Parquet files; callers forward DataFrames or records to every other sink ([[data-generator]]).
- Both writers expose `format`, `mode`, `option` and `options`; an unsupported or malformed option raises `RandEngineError` before any output is touched.

## Batch writer

- `generator.write.format(f).mode(m).option(k, v).save(path)` uses the generator's configured size as the total row count.
- `numFiles` splits that total as evenly as possible across parts; offsets follow the cumulative part sizes, so keys do not repeat between files. A part that receives zero rows is written as an empty file with the schema of the other parts, else of the method catalog.
- A single file uses the requested path. Multiple files use a directory of `part_<id>` files.
- `maxRowsPerBatch` (absent or `None` disables it; otherwise a positive integer) generates each final file in contiguous row batches of at most that many rows, so no generated frame exceeds it. Global transformers run once per row batch, and keys keep their row-index semantics across batches. Different batch sizes carry no equality promise for ordinary values.
- The spec is evaluated once per final file; one schema holds across a final file's batches, and a batch whose columns or types differ raises `RandEngineError` before the destination changes. Typed nulls take the type of the file's schema, else of the method catalog.
- Output is staged beside the destination and committed only after every file closes, so a failure in a transformer, modifier, schema check or option leaves any existing output intact.
- `mode("append")` adds rows: a single file is rebuilt from its existing content plus the new rows, and a multi-file save adds only new part files beside the existing ones, which are never copied or rewritten. Any other mode overwrites, replacing a part directory as a whole.

## Stream writer

- `generator.writeStream.trigger(seconds).option("timeout", seconds).start(path)` writes repeated `size`-row microbatches to `part-<uuid>` files; overwrite mode empties the directory first, and `maxRowsPerBatch` is not an accepted stream option.
- Each microbatch advances the row offset; `start` blocks until the timeout expires.

## Formats

- CSV and Parquet convert the DataFrame to an Arrow table; mixed-type object columns fail with the column named. Parquet defaults to Snappy and preserves timezone-aware values and dtypes.
- CSV accepts `sep`, `compression` (gzip, bz2, xz, zip) and `index=False`; one header per file, an empty field for a null, and timezone-aware columns rendered to pandas strings before Arrow writes them.
- JSON is pandas JSON-lines output (`orient` is `records` only) and accepts `force_ascii`, `indent` and `compression`; a null is `null`.
- Parquet accepts `compression` only and writes a typed null that keeps the column's logical type.
