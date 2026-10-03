---
slug: writers-and-streaming
title: Writers and streaming
tldr: "Spark-style file writers on DataGenerator — write saves CSV, JSON lines or Parquet files; writeStream emits one file per microbatch until a timeout."
summary: "DataGenerator.write (FileBatchWriter) and .writeStream (FileStreamWriter) mirror Spark's writer API — format, mode, option(s), size, then save or trigger+start; every file is a fresh microbatch of the generator's pipeline."
tags: [writers, streaming, files, csv, json, parquet]
sources:
  - rand_engine/file_handlers/**
---

## Scope

- Built-in sinks are local or mounted files only (CSV, JSON lines, Parquet); no Kafka, queue, object-store or database writer exists.
- Every other sink is reached by forwarding `get_df()` DataFrames or `stream_dict` records ([[data-generator]]).

## Batch — `write`

- `generator.write.format(f).mode(m).option(k, v).size(n).save(path)` writes generated rows to files ([[data-generator]]).
- `format` is `csv` (default, no index), `json` (JSON lines, one record per line) or `parquet` (PyArrow engine).
- `option("compression", c)` passes pandas compression; CSV and JSON get a `.<format>.<c>` extension (`gzip` -> `.gz`), Parquet keeps `.parquet`.
- `option("numFiles", k)` with `k > 1` writes `k` files `part_<id>.<ext>` into a directory named after the target file; `mode("overwrite")` (the default) empties that directory first.
- `.size(n)` sets the rows per file; each file is a fresh microbatch of the pipeline.
- `.options(**kw)` sets several options at once.

## Stream — `writeStream`

- `generator.writeStream.format(f).option("timeout", s).trigger(t).size(n).start(path)` writes `part-<uuid>.<ext>` files into a directory named after the target, one microbatch every `t` seconds, until `s` seconds have passed.
- `mode("overwrite")` empties the directory before the first file.

## Filesystem helpers

- `fs_utils` defines `LocalFSUtils` and `DBFSUtils` (Databricks `dbutils`) behind one `ls`/`mkdir`/`rm` interface; the writers use `os` directly.
