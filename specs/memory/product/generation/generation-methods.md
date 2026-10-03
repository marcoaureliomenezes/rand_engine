---
slug: generation-methods
title: Generation methods
tldr: "Ten common methods run on pandas and Spark; four correlated methods (maps, weighted maps, multi-maps, patterns) run on pandas only."
summary: "The method names a RandSpec column may use, what each produces, and which engine runs it — NPCore (vectorized NumPy) and PyCore (correlated tuples, patterns) for pandas, SparkCore (native expressions) for Spark."
tags: [methods, numpy, spark, correlation]
sources:
  - rand_engine/core/**
  - rand_engine/main/_rand_generator.py
---

## Common methods (pandas and Spark)

| method | kwargs | produces |
|---|---|---|
| `integers` | `min`, `max`, `int_type` | random integers in the range, cast to `int_type` |
| `int_zfilled` | `length` | numeric strings zero-padded to `length` |
| `floats` | `min`, `max`, `decimals` | random decimals rounded to `decimals` |
| `floats_normal` | `mean`, `std`, `decimals` | normally distributed decimals |
| `booleans` | `true_prob` | booleans, `True` with probability `true_prob` |
| `distincts` | `distincts` (list) | uniform picks from the list |
| `distincts_prop` | `distincts` (value -> integer weight) | weighted picks |
| `unix_timestamps` | `start`, `end`, `date_format` | epoch seconds between two parsed dates, floored at 1970 |
| `dates` | `start`, `end`, `date_format` | date strings formatted with `date_format` |
| `uuid4` | none | UUID4 strings |

- pandas runs these as `NPCore` NumPy calls, one array per column; `uuid4` and `dates` build values per row.
- Spark runs them as `SparkCore` column expressions; `distincts` joins a broadcast lookup table on a random index; `int_type` maps NumPy names onto Spark integer types.

## Correlated methods (pandas only)

- `distincts_map` — `{category: [values]}` -> `(category, value)` pairs split into two `cols`.
- `distincts_map_prop` — `{category: [(value, weight)]}` -> weighted `(category, value)` pairs in two `cols`.
- `distincts_multi_map` — `{key: [[a1, a2], [b1]]}` -> one row per combination of the key and one pick from each list, split into N `cols`.
- `complex_distincts` — `pattern` with a `replacement` placeholder plus one `{method, kwargs}` template per placeholder -> concatenated strings such as IPs, SKUs and URLs.
- `PyCore` samples these from in-memory tuple lists; `SparkGenerator` does not accept them ([[spark-generator]]).

## Randomness

- pandas methods draw from NumPy's global random state, which `DataGenerator(seed=…)` seeds ([[data-generator]]); `uuid4` draws from Python's `uuid`.
- Spark methods draw from `rand()`/`randn()` and `uuid()` with no seed.
