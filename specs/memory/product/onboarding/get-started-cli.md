---
slug: get-started-cli
title: Get-started CLI
tldr: "The rand-engine console script lists five adoption cases and writes any of them as a runnable example file."
summary: "rand-engine list prints the five case slugs with what each teaches; rand-engine get-started <slug> [--out DIR] copies the packaged scaffold to DIR/<slug>-example.py without overwriting. Each scaffold is a Databricks-format source file that also runs under plain python."
tags: [cli, onboarding, scaffolds, examples]
sources:
  - rand_engine/cli.py
  - rand_engine/__main__.py
  - rand_engine/cases/**
---

## Commands

- `rand-engine` (console script) and `python -m rand_engine` run the same parser; it uses only the standard library and never reads stdin ([[public-api]]).
- `rand-engine list` prints one line per case, `<slug>  <description>`, in a fixed order, and exits 0.
- `rand-engine get-started <slug> [--out DIR]` writes `DIR/<slug>-example.py` (default `DIR` is the current directory, created when missing), prints the written path and exits 0. The `-example` suffix keeps the file name from shadowing a package the example imports.
- An existing target file is left unchanged: the command prints the path on stderr and exits 1. `get-started` with an unknown or missing slug exits 2 with usage that lists the five slugs; a bare `rand-engine` exits 2 with usage that lists the subcommands `list` and `get-started`.
- A slug always yields the same bytes: the file is a copy of the packaged `rand_engine/cases/<slug>.py.txt`.

## Cases

| slug | teaches |
|---|---|
| `test-data` | a DataFrame for pipeline tests with `null_rate` and `anomaly_rate` ([[generation-methods]]) |
| `lake` | `pk`/`fk` related tables written as Parquet under `lake/` in the run directory, read back and joined ([[pk-fk-constraints]], [[writers-and-streaming]]) |
| `kafka` | an event stream printed as JSON lines; a Kafka producer block runs only when the file's `SEND_TO_KAFKA` constant is set to `True`, so no broker or client is needed by default ([[data-generator]]) |
| `databricks` | a Spark notebook on native `SparkGenerator`, with a note on `DataGenerator`-only features and the `spark.createDataFrame` path ([[spark-generator]]) |
| `faker` | Faker pools sampled at NumPy speed through `RandSpecs.faker_pool`; needs the `rand-engine[faker]` extra ([[templates-and-examples]]) |

## Scaffold format

- Every scaffold starts with `# Databricks notebook source` and separates cells with `# COMMAND ----------`; both are comments, so the file imports into Databricks and runs with `python <file>`.
- Scaffolds use synthetic data only, generate at most 10^4 rows and write only beneath the directory they run in.
- Each docs-site tutorial includes its case file verbatim, so the page and the CLI output cannot diverge ([[documentation]]).
