---
slug: data-generator
title: DataGenerator
tldr: "The pandas generator: validates a RandSpec, seeds NumPy, and returns DataFrames, files, file streams or an endless record stream."
summary: "DataGenerator(spec, seed) is the pandas composition root; a fluent builder (size, transformers, option) feeds get_df, stream_dict, write and writeStream, each running the same pipeline of column generation, per-column transformers, global transformers and PK/FK constraints."
tags: [pandas, numpy, generator, dataframe]
sources:
  - rand_engine/main/data_generator.py
  - rand_engine/main/_rand_generator.py
  - rand_engine/utils/stream_handler.py
---

## Role

- The core of rand-engine: Python + NumPy + pandas, no Spark, Faker, broker or database server needed.
- Sink-agnostic: it returns DataFrames and records the user forwards anywhere; the file writers are the only built-in sink ([[writers-and-streaming]]).
- A `distincts` value pool built with Faker is sampled at NumPy speed, e.g. `distincts=[fake.first_name() for _ in range(1000)]`; Faker stays the user's dependency.

## Construction

- `DataGenerator(random_spec, seed=None)` takes a RandSpec dict or a zero-argument callable returning one, and validates it at once ([[rand-spec-grammar]]).
- `seed` seeds NumPy's global random state (`np.random.seed`) at construction.
- A callable spec is re-evaluated on every batch, so each batch can see fresh spec values.

## Builder

- `.size(n)` sets the row count; `n` may be a callable evaluated per call.
- `.transformers([fn, …])` sets global transformers: DataFrame -> DataFrame functions applied in order after column generation.
- `.option("reset_checkpoint", True)` drops the checkpoint tables before `get_df` ([[pk-fk-constraints]]).
- Each builder method returns the generator, so calls chain.

## Pipeline

1. Evaluate the spec; take its `constraints` out of the column set.
2. Generate every column through the pandas method table ([[generation-methods]]); a multi-column method fans out to its `cols`.
3. Apply each column's `transformers` value by value, in order.
4. Apply the global transformers.
5. Apply the PK/FK constraints ([[pk-fk-constraints]]).

## Outputs

- `.get_df()` — one pandas DataFrame of `size` rows.
- `.stream_dict(min_throughput=1, max_throughput=10)` — an endless generator of record dicts, one microbatch of `size` rows at a time; datetime columns become strings, each record gains `timestamp_created` (epoch seconds, millisecond precision), and the pace stays between the two throughputs in records per second.
- `.write` / `.writeStream` — batch and stream file writers bound to this pipeline ([[writers-and-streaming]]).
