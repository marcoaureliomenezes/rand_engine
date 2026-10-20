---
slug: benchmarks
title: Performance benchmarks
tldr: "CI enforces same-runner rand-engine regression limits and separately records bounded, validated observations against Faker and dbldatagen."
summary: "The regression coordinator compares long-lived head workers against the latest closed release tag and enforces method, modifier and sink limits; a separate non-gating workflow installs pinned comparison dependencies and the public wheel, validates two named Python and Spark workloads, and retains raw samples, medians, plans and provenance without a winner or threshold."
tags: [performance, benchmarks, ci, regression]
sources:
  - benchmarks/**
  - .github/workflows/benchmarks.yml
  - .github/workflows/comparison.yml
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
- The comparison base is the commit of the highest bare `M.m.p` release tag, the latest closed release, never a mid-release commit or a release candidate; the job summary names that tag and its commit, and a repository without such a tag fails the job. A row absent from the base, or a base failure, is reported, while a head failure is fatal.

## Delivery and gate

- Pull requests to the principal or integration branch, and a manual dispatch, run stress tests and the speed benchmark in one CI job.
- The generated Markdown is placed in the job summary and one updated pull-request comment; Markdown and JSON are uploaded as artifacts.
- Any comparable method or sink row slower than 1.3 times its base fails the job.
- Within the same run, `poisson` and `zipf` may cost at most 1.5 times `distincts_prop`, and `exponential` and `lognormal` at most 1.5 times `floats_normal`.
- A modifier's overhead (its row time minus the unmodified `integers` time) may be at most 1.75 times that unmodified time for `null_rate` and 2.5 times for `anomaly_rate`; a modified column therefore costs at most 2.75 and 3.5 times the plain column. Modifier rows have no base comparison.

## Bounded cross-library observation

- A distinct observational workflow uses a pinned CI-only environment and the installed public, non-editable `rand-engine` wheel; its dedicated requirements do not modify the package dependency declarations or the project lock.
- One contract materializes 100,000 three-field Python dictionaries from rand-engine and Faker. The other fully evaluates 1,000,000 three-field Spark rows at eight partitions from rand-engine and dbldatagen, retaining schemas, null and domain checks, aggregates and executed plans that hash every payload column.
- Each side warms once, then runs three timed samples in AB/BA/AB order. Setup, warm-up and complete output validation stay outside those sample clocks; the versioned JSON retains raw samples, medians, environment and package identity, wheel and harness hashes, validations and plans.
- The workflow is unscheduled and non-required, carries no limit or ranking field and cannot change the internal 1.3 regression authority. The public comparison guide records the actual bounded observations and their limits without inferring a universal winner ([[documentation]]).

## Benchmark record

- A candidate whose code touches a measured path records the CI artifact of its last measured head byte for byte as `docs/benchmarks.json` and `docs/BENCHMARKS.md`; the record commit adds only `docs/` and `tests/`, so the measured paths stay at the recorded head.
- The committed JSON names its head and base commits; tests check that it names the recorded commits, holds every inventory row at both sizes and passes every repo limit.
- The docs site serves `docs/BENCHMARKS.md` as its Benchmarks page ([[documentation]]).
