---
slug: data-generator
title: DataGenerator
tldr: "The pandas generator validates a RandSpec, proves one row per column, owns its random generator, and returns DataFrames, files, file streams or record streams."
summary: "DataGenerator(spec, seed) is the pandas composition root; construction refuses a spec that validates but cannot generate one row; size, resolved by one decider, and transformers feed get_df, stream_dict, write and writeStream, with one owned NumPy generator, a fixed column-to-modifier order, continuous key offsets and one normalized pandas record path that preserves public Python values."
tags: [pandas, numpy, generator, dataframe]
sources:
  - rand_engine/main/data_generator.py
  - rand_engine/main/_rand_generator.py
  - rand_engine/utils/stream_handler.py
---

## Role

- The NumPy-first composition root: it returns pandas DataFrames and record dicts, while the file writers provide the built-in sinks ([[writers-and-streaming]]).
- A user can build a small value pool with `RandSpecs.faker_pool` and pass it as a `distincts` column; Faker is optional and never called during generation ([[templates-and-examples]]).

## Construction and randomness

- `DataGenerator(random_spec, seed=None)` accepts a RandSpec dict or a zero-argument callable and validates its current value at construction ([[rand-spec-grammar]]).
- After validation, construction generates one row of every column through its method on a private generator that the instance's seed and key seed never feed, then applies the column's modifiers unless the column has embedded transformers; no transformer runs. A column that cannot generate is refused with `SpecValidationError` naming the column, the method and the engine's error type and text.
- Anomaly values must keep their column's dtype, judged twice. At construction, a column without embedded transformers is judged on its method's dtype (`SpecValidationError`); global transformers are set after construction, so anomaly values that fit only after a global transformer changes the dtype are refused there. At generation, modifiers run after the embedded and global transformers, and anomaly values the transformed column cannot keep raise `RandEngineError`, for any column.
- Each instance owns one `numpy.random.Generator` and one key seed, both derived from `seed`; generation never reads or resets NumPy's global random state.
- The same seed, spec, size and writer batch configuration reproduce the same values.
- A callable spec is evaluated once for each `get_df`, each stream microbatch and each final file of a batch save; each evaluation is validated, and an invalid value raises `SpecValidationError` before any row. The one-row check runs only at construction.

## Builder and pipeline

- `.size(n)` sets the row count; `n` may be a callable evaluated by the output operation. `.size` checks nothing: one decider, `resolve_size`, judges the value when an output operation resolves it — `get_df`, `stream_dict`, both writers and `SparkGenerator.get_df` alike.
- An unset size raises `RandEngineError` `No size set: call .size(n) with an int or a callable returning one.`; a value, or a callable's return, that is not a non-negative integer (a bool included; a NumPy integer passes) raises `RandEngineError` `size must be a non-negative integer, got <value>`, before any row. `size(0)` gives an empty frame.
- `.transformers([fn, ...])` sets DataFrame transformers; a global transformer that returns anything but a DataFrame of the same row count raises `RandEngineError`.
- A frame is built in a fixed order: each column through the NumPy method map; per-column transformers; global transformers; the `anomaly_rate` write; the `null_rate` mask, which wins on a shared row ([[generation-methods]]).
- `pk` and `fk` receive the row offset, key seed and column name ([[pk-fk-constraints]]).
- Modifier draws come from the owned generator after every column is built; an absent modifier or one with rate 0 consumes no draw.
- The generator never removes or mutates a key in the caller's spec.

## Outputs

- `.get_df()` returns one DataFrame and begins key row indexes at zero on every call.
- `.stream_dict(min_throughput, max_throughput)` yields records forever; each microbatch advances the key row offset, datetime columns become strings, nulls become Python `None` and each record gains `timestamp_created`.
- After datetime and missing-value normalization, every microbatch converts through pandas records, preserving scalar, nested, mixed, custom and extension values, non-string labels, exact Python types and key order.
- `.write` and `.writeStream` bind the same generator pipeline to the file writers; one batch save distributes its total size across file parts, while stream microbatches each use the configured size ([[writers-and-streaming]]).
