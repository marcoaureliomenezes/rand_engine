---
slug: get-started-cli
title: Get-started CLI
tldr: "The rand-engine console script lists six starters: five runnable Python examples and one opt-in AGENTS.md project context."
summary: "rand-engine list prints six starter slugs; one Case descriptor owns each description, packaged resource, output filename and kind. get-started copies the chosen resource without overwriting: five starters produce runnable <slug>-example.py files, while agent produces AGENTS.md package-use guidance."
tags: [cli, onboarding, scaffolds, examples]
sources:
  - rand_engine/cli.py
  - rand_engine/__main__.py
  - rand_engine/cases/**
---

## Commands

- `rand-engine` (console script) and `python -m rand_engine` run the same parser; it uses only the standard library and never reads stdin ([[public-api]]).
- `rand-engine list` prints one line per case, `<slug>  <description>`, in a fixed order, and exits 0.
- `rand-engine get-started <slug> [--out DIR]` writes the starter's declared filename under `DIR` (default `DIR` is the current directory, created when missing), prints the written path and exits 0. The five runnable starters use `<slug>-example.py`; the Agent starter uses `AGENTS.md`.
- An existing target file is left unchanged: the command prints the path on stderr and exits 1. `get-started` with an unknown or missing slug exits 2 with usage that lists all six slugs; a bare `rand-engine` exits 2 with usage that lists the subcommands `list` and `get-started`.
- One `Case` descriptor owns every starter's description, package resource, target filename and kind. A slug always yields the same bytes from its declared resource under `rand_engine/cases/`.

## Cases

| slug | teaches |
|---|---|
| `test-data` | a DataFrame for pipeline tests with `null_rate` and `anomaly_rate` ([[generation-methods]]) |
| `lake` | `pk`/`fk` related tables written as Parquet under `lake/` in the run directory, read back and joined ([[pk-fk-constraints]], [[writers-and-streaming]]) |
| `kafka` | an event stream printed as JSON lines; a Kafka producer block runs only when the file's `SEND_TO_KAFKA` constant is set to `True`, so no broker or client is needed by default ([[data-generator]]) |
| `databricks` | a Spark notebook on native `SparkGenerator`, with a note on `DataGenerator`-only features and the `spark.createDataFrame` path, which enables Spark's Arrow option first so `pd.NA` text nulls convert ([[spark-generator]]) |
| `faker` | Faker pools sampled at NumPy speed through `RandSpecs.faker_pool`; needs the `rand-engine[faker]` extra ([[templates-and-examples]]) |
| `agent` | concise rand-engine package-use guidance written to `AGENTS.md` for a consuming project; it is context for an agent, not an executable tutorial ([[documentation]]) |

## Scaffold format

- Each runnable scaffold starts with `# Databricks notebook source` and separates cells with `# COMMAND ----------`; both are comments, so the file imports into Databricks and runs with `python <file>`.
- Runnable scaffolds use synthetic data only, generate at most 10^4 rows and write only beneath the directory they run in. Each docs-site tutorial includes its case file verbatim, so the page and the CLI output cannot diverge ([[documentation]]).
- The Agent resource is Markdown. It routes installation, compatibility and the first result to the live Getting started guide; gives supported imports, a first `DataGenerator` path and the `SparkGenerator` boundary; and links the public machine guide and the published copy of the canonical Agent Skill. It tells a user to preserve and merge existing project instructions, and never executes as Python.
