---
slug: benchmarks
title: Performance benchmarks
tldr: "A CI-only same-runner A/B benchmark measures every generation method and built-in sink, publishes its table and enforces a relative regression limit."
summary: "The benchmark coordinator alternates timed requests between long-lived base and head workers per row, reports method and sink throughput, publishes Markdown and JSON artifacts, and fails when a comparable head row exceeds the configured ratio."
tags: [performance, benchmarks, ci, regression]
sources:
  - benchmarks/**
  - .github/workflows/benchmarks.yml
---

## Coverage

- The sample catalog covers every key in the NumPy generator's method map at two large row sizes, plus CSV, Parquet, JSON and `stream_dict` sinks.
- The script refuses a head method missing from its samples and reports methods added to or deleted from one side of the comparison.

## Measurement

- Base and head run in separate long-lived worker processes on the same CI runner. For every comparable row, the coordinator alternates three requests per side and compares their medians.
- Untimed method-only passes record core time and peak memory after all timed rows. Throughput is reported as rows per microsecond.
- The committed JSON identifies the comparison base for the next run; absence or failure on the base side is reported, while a head failure is fatal.

## Delivery and gate

- Pull requests to the principal or integration branch run stress tests and the speed benchmark in one CI job.
- The generated Markdown is placed in the job summary and one updated pull-request comment; Markdown and JSON are uploaded as artifacts.
- Any comparable method or sink row slower than the configured relative limit fails the job.
