---
slug: writers-and-streaming
title: Writers and streaming
tldr: "DataGenerator writes CSV, JSON lines and Parquet batches or repeated file-stream microbatches through a Spark-style builder."
summary: "The batch writer distributes one requested total row count across numFiles; the stream writer emits size rows per microbatch. CSV and Parquet use PyArrow, JSON uses pandas, and each format accepts only documented options."
tags: [writers, streaming, files, csv, json, parquet]
sources:
  - rand_engine/file_handlers/**
---

## Scope

- Built-in sinks are local or mounted CSV, JSON-lines and Parquet files; callers forward DataFrames or records to every other sink ([[data-generator]]).
- Both writers expose `format`, `mode`, `option` and `options`; unsupported options raise `RandEngineError` before existing output is removed.

## Batch writer

- `generator.write.format(f).mode(m).option(k, v).save(path)` uses the generator's configured size as the total row count.
- `numFiles` splits that total as evenly as possible across parts; offsets follow the cumulative part sizes, so keys do not repeat between files.
- A single file uses the requested path. Multiple files use a directory of `part_<id>` files, emptied first in overwrite mode.

## Stream writer

- `generator.writeStream.trigger(seconds).option("timeout", seconds).start(path)` writes repeated `size`-row microbatches to `part-<uuid>` files.
- Each microbatch advances the row offset; `start` blocks until the timeout expires.

## Formats

- CSV and Parquet convert the DataFrame to an Arrow table; mixed-type object columns fail with the column named. Parquet defaults to Snappy and preserves timezone-aware values and dtypes.
- CSV accepts `sep`, supported compression and `index=False`; compressed streams use gzip, bz2, xz or deflated zip file objects. Timezone-aware columns are rendered to pandas strings before Arrow writes them.
- JSON remains pandas JSON-lines output and accepts its documented orientation, text and compression options.
