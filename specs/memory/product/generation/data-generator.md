---
slug: data-generator
title: DataGenerator
tldr: "The pandas generator validates a RandSpec, owns its random generator, and returns DataFrames, files, file streams or an endless record stream."
summary: "DataGenerator(spec, seed) is the pandas composition root; size and transformers feed get_df, stream_dict, write and writeStream, with one owned NumPy generator and row offsets that keep keys continuous across stream batches and file parts."
tags: [pandas, numpy, generator, dataframe]
sources:
  - rand_engine/main/data_generator.py
  - rand_engine/main/_rand_generator.py
  - rand_engine/utils/stream_handler.py
---

## Role

- The NumPy-first composition root: it returns pandas DataFrames and record dicts, while the file writers provide the built-in sinks ([[writers-and-streaming]]).
- A user can build a small value pool with Faker and pass it to `distincts`; Faker is not a runtime dependency.

## Construction and randomness

- `DataGenerator(random_spec, seed=None)` accepts a RandSpec dict or a zero-argument callable and validates its current value at construction ([[rand-spec-grammar]]).
- Each instance owns one `numpy.random.Generator`; generation does not read or reset NumPy's global random state.
- A callable spec is evaluated once for each generated DataFrame or stream microbatch.

## Builder and pipeline

- `.size(n)` sets the row count; `n` may be a callable evaluated by the output operation.
- `.transformers([fn, ...])` sets DataFrame transformers applied after per-column transformers.
- Each column dispatches through the NumPy method map; `pk` and `fk` additionally receive the row offset, key seed and column name ([[generation-methods]], [[pk-fk-constraints]]).
- The generator never removes or mutates a key in the caller's spec.

## Outputs

- `.get_df()` returns one DataFrame and begins key row indexes at zero on every call.
- `.stream_dict(min_throughput, max_throughput)` yields records forever; each microbatch advances the key row offset, datetime columns become strings and each record gains `timestamp_created`.
- `.write` and `.writeStream` bind the same generator pipeline to the file writers; one batch save distributes its total size across file parts, while stream microbatches each use the configured size ([[writers-and-streaming]]).
