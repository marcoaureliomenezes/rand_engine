---
slug: generation-methods
title: Generation methods
tldr: "Ten common methods run on pandas and Spark; four correlated methods plus pk and fk run on pandas."
summary: "NPCore and PyCore provide the NumPy generator's single method map, including deterministic keys; SparkCore supplies native Spark expressions for the ten common methods."
tags: [methods, numpy, spark, correlation]
sources:
  - rand_engine/core/**
  - rand_engine/main/_rand_generator.py
---

## Common methods

| method | main kwargs | produces |
|---|---|---|
| `integers` | `min`, `max`, `int_type` | inclusive random integers |
| `int_zfilled` | `length` | zero-padded numeric strings |
| `floats` | `min`, `max`, `decimals` | rounded uniform values |
| `floats_normal` | `mean`, `std`, `decimals` | rounded normal values |
| `booleans` | `true_prob` | booleans at the requested probability |
| `distincts` | list `distincts` | uniform choices |
| `distincts_prop` | value-to-weight `distincts` | weighted choices |
| `unix_timestamps` | `start`, `end`, `date_format` | UTC epoch seconds |
| `dates` | `start`, `end`, `date_format` | UTC date strings using `%Y %m %d %H %M %S %f` |
| `uuid4` | none | RFC 4122 version-4 UUID strings |

- On pandas these methods draw from the `numpy.random.Generator` owned by [[data-generator]]. Date rendering is vectorized, and UUID bytes come from that same generator.
- On Spark they are native `SparkCore` expressions; Spark has no seed in this interface ([[spark-generator]]).

## Pandas-only methods

- `distincts_map` and `distincts_map_prop` return `(category, value)` pairs.
- `distincts_multi_map` returns the category followed by one selected value from each declared level; `cols` therefore has exactly levels plus one names.
- `complex_distincts` fills a pattern from templates that use methods in the NumPy engine's method map.
- `pk` emits unique sequence or permuted keys; `fk` rebuilds a parent key selected from the child seed, column, definition and row index ([[pk-fk-constraints]]).

## Dispatch

- The NumPy engine has one method-name-to-callable map shared by normal columns and `complex_distincts` templates.
- `RandGenerator` binds the owned random generator to ordinary methods and binds row/key context to `pk` and `fk`.
