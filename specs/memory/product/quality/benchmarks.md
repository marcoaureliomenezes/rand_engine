---
slug: benchmarks
title: Performance benchmarks
tldr: "CI compares every generation method, two modifiers and four sinks on the same runner, publishes results and enforces regression limits."
summary: "The benchmark coordinator alternates timed requests between long-lived base and head workers per row, reports method, modifier and sink throughput, publishes Markdown and JSON artifacts, and fails when a comparable head row exceeds the base ratio, a new distribution exceeds its sibling method, or a modifier costs more than its overhead limit."
tags: [performance, benchmarks, ci, regression]
sources:
  - benchmarks/**
  - .github/workflows/benchmarks.yml
  - docs/BENCHMARKS.md
  - docs/benchmarks.json
---

## Coverage

- The sample catalog covers every key in the NumPy generator's method map at two large row sizes by default, plus CSV, Parquet, JSON and `stream_dict` sinks.
- Two modifier rows per size time an `integers` column with `null_rate` and with `anomaly_rate`.
- The script refuses a head method missing from its samples and reports methods added to or deleted from one side of the comparison.

## Measurement

- Base and head run in separate long-lived worker processes on the same CI runner. For every comparable row, the coordinator alternates three requests per side and compares their medians.
- Untimed method-only passes record core time and peak memory after all timed rows. Throughput is reported as rows per microsecond.
- The committed JSON identifies the comparison base for the next run; absence or failure on the base side is reported, while a head failure is fatal.

## Delivery and gate

- Pull requests to the principal or integration branch, and a manual dispatch, run stress tests and the speed benchmark in one CI job.
- The generated Markdown is placed in the job summary and one updated pull-request comment; Markdown and JSON are uploaded as artifacts.
- Any comparable method or sink row slower than 1.3 times its base fails the job.
- Within the same run, `poisson` and `zipf` may cost at most 1.5 times `distincts_prop`, and `exponential` and `lognormal` at most 1.5 times `floats_normal`.
- A modifier's overhead (its row time minus the unmodified `integers` time) may be at most 1.75 times that unmodified time for `null_rate` and 2.5 times for `anomaly_rate`; a modified column therefore costs at most 2.75 and 3.5 times the plain column. Modifier rows have no base comparison.

## Benchmark record

- A candidate whose code touches a measured path records the CI artifact of its last measured head byte for byte as `docs/benchmarks.json` and `docs/BENCHMARKS.md`; the record commit adds only `docs/` and `tests/`, so the measured paths stay at the recorded head.
- The committed JSON names its head and base commits and is the next run's comparison base; tests check that it names the recorded commits, holds every inventory row at both sizes and passes every repo limit.
- The docs site serves `docs/BENCHMARKS.md` as its Benchmarks page ([[documentation]]).
