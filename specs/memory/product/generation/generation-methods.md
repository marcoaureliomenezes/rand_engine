---
slug: generation-methods
title: Generation methods
tldr: "Ten common methods run on pandas and Spark; stateless pk/fk share one indexed authority; extra distributions, correlated methods, constants and modifiers are pandas-only."
summary: "NPCore and PyCore provide the NumPy generator's method map, and every all-text column they generate is string[pyarrow] with pd.NA nulls; SparkCore supplies native expressions for the ten common methods. Pandas and Spark both call Keys for deterministic pk/fk values, while extra distributions, the four correlated methods, constants and modifiers remain pandas-only."
tags: [methods, numpy, spark, correlation, distributions, modifiers]
sources:
  - rand_engine/core/**
  - rand_engine/main/_rand_generator.py
  - rand_engine/validators/method_specs.py
---

## Common methods

| method | main kwargs | produces |
|---|---|---|
| `integers` | `min`, `max`, `int_type` | inclusive random integers |
| `int_zfilled` | `length` (1 to 18; at most 15 on Spark) | zero-padded numeric strings of `length` digits |
| `floats` | `min`, `max`, `decimals` | uniform values on the decimal grid, inside `[min, max]` |
| `floats_normal` | `mean`, `std`, `decimals` | rounded normal values |
| `booleans` | `true_prob` | booleans at the requested probability |
| `distincts` | list `distincts` | uniform choices |
| `distincts_prop` | value-to-weight `distincts` | weighted choices |
| `unix_timestamps` | `start`, `end`, `date_format` | UTC epoch seconds |
| `dates` | `start`, `end`, `date_format` | UTC date strings using `%Y %m %d %H %M %S %f` |
| `uuid4` | none | RFC 4122 version-4 UUID strings |

- `unix_timestamps` and `dates` draw over the whole `[start, end)` before, across or after 1970; epoch seconds before 1970 are negative. Both engines turn the two parsed bounds into epoch seconds through one shared `epoch_seconds`.
- On pandas these methods draw from the `numpy.random.Generator` owned by [[data-generator]]. `uuid4`, `int_zfilled` and `dates` build their text as fixed-width Arrow rows from those draws; a date-only format renders each distinct day once.
- A column whose generated values are all text — `int_zfilled`, `dates`, `uuid4`, and `distincts`, `distincts_prop` or `constant` with text values — is `string[pyarrow]` (`pd.ArrowDtype(pa.string())`) on every pandas; numeric and boolean columns keep the NumPy dtypes the methods return; a datetime column takes the unit the installed pandas gives Python datetimes, `ns` on pandas 2 and `us` on pandas 3.
- On Spark they are native `SparkCore` expressions; an explicit Spark seed affects key columns only, not these ordinary methods ([[spark-generator]]).
- `integers` defaults to `int32` on pandas and `long` on Spark; its bounds must fit `int_type`.

## Float rules

- One predicate decides `decimals`: an `int` with absolute value at most 308. `exponential` and `lognormal` additionally need `decimals >= 0`; `floats` and `floats_normal` accept negative decimals.
- `floats` draws a uniform integer on the grid `ceil(min*10^d)..floor(max*10^d)` and divides by `10^d`, so every value lies inside the bounds and both representable ends can occur. An empty grid or a span that overflows float64 is refused. Values are float64: an integer bound a double cannot hold comes out as the nearest double.
- A grid with more than 2^53 steps, or a grid end (bound times 10^`decimals`) outside `int64`, is drawn uniformly in `[min, max]` on pandas and Spark alike; rounding at that precision changes nothing.
- Rounding never turns a finite draw into infinity; a draw that is infinite itself, at a distribution's float64 limit, is returned as drawn.
- Spark float methods compute on the float form of their kwargs, so Python ints beyond `int64` never reach a Spark expression.

## NumPy-only methods

- `exponential(scale=1.0, decimals=2)` and `lognormal(mean=0.0, std=1.0, decimals=2)` return rounded `float64`; `scale` is finite and positive, `std` finite and non-negative.
- `poisson(lam=1.0)` and `zipf(a=2.0)` return `int64` from alias-table samplers; `lam` lies in `[0, 10^6]` and `a` is finite and greater than 1. Zipf values beyond the table are drawn exactly from the tail, up to `int64`.
- `constant(value)` repeats an immutable scalar (`None`, bool, int, float, str, bytes, date, datetime, Decimal) and consumes no random draw; a non-null value keeps its natural pandas dtype, `string[pyarrow]` for text, and `None` gives an object column of nulls. The declared Arrow type of a datetime value is the one the pandas -> Arrow conversion writes, so an empty file's schema equals a populated one's.
- `distincts_map` and `distincts_map_prop` return a category column and a value column drawn as one row; every pool must be non-empty.
- `distincts_multi_map` returns the category column followed by one column per declared level; `cols` therefore has exactly levels plus one names.
- A map-family level whose values are all text is `string[pyarrow]`; a level that mixes text with other values, `None` included, is an `object` column holding its Python values, so `None` stays `None`; any other level keeps pandas' inference.
- `complex_distincts` fills a pattern from templates that use ordinary methods in the NumPy engine's method map and returns `string[pyarrow]` text; a pattern without templates repeats its literal.

## Key methods

- `pk` emits unique sequence or permuted keys; `fk` rebuilds a parent key selected from the child seed, column, definition and row index. Both run through the same indexed `Keys` authority on pandas and Spark; `fk.born_before` can restrict each child to parents whose derived event time is not later ([[pk-fk-constraints]]).

## Modifiers

- `null_rate` and `anomaly_rate` with `anomaly_values` are sibling column keys on ordinary pandas columns; `pk`, `fk`, the three map methods, `complex_distincts` and every Spark column refuse them ([[rand-spec-grammar]]).
- Rates are independent per-row probabilities in `[0, 1]`, not exact counts. A positive `anomaly_rate` replaces rows with a uniform pick from the non-empty scalar list `anomaly_values`; the null mask runs last and wins on a shared row.
- A rate of 0, or an absent key, consumes no random draw; a seeded configuration reproduces its masks and values.
- Anomaly values must preserve the column's dtype after transformers or the call raises `RandEngineError`; the write lands in a private copy of the column, never in the caller's or a sibling column's memory.
- Nulls keep the column's logical type: width-matched pandas nullable integers, nullable boolean, `NaN` for floats, `NaT` for datetimes, `pd.NA` for text, whose column stays `string[pyarrow]`, and `None` for objects.

## Dispatch

- The NumPy engine has one method-name-to-callable map shared by normal columns and `complex_distincts` templates.
- `RandGenerator` binds the owned random generator to ordinary methods, binds row/key context to `pk` and `fk`, and applies the modifiers.
- One `RandGenerator` decider makes each generated column `string[pyarrow]` when its values are all text, `pk` and `fk` with a text `format` included; a transformer runs on a plain-object view of the column, so its output takes the dtype the installed pandas infers from the returned Python values: a `pd.Timestamp` result is a datetime column, and on pandas 3 a `str` result is pandas `str` dtype, with `str` subclasses turned into plain `str`.
