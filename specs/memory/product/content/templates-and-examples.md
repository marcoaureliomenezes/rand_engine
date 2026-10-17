---
slug: templates-and-examples
title: Templates and examples
tldr: "Ready RandSpecs (ten cross-engine, ten pandas-only), a UTC WebServerLogs template, and Faker-pool and Arrow-schema spec builders."
summary: "Prebuilt specs a user runs without writing a grammar — CommonRandSpecs is exported as RandSpecs and runs on both generators; AdvancedRandSpecs demonstrates correlated pandas methods; WebServerLogs assembles Apache common log lines in UTC; faker_pool and from_schema return plain RandSpec fragments from Faker or Arrow field metadata."
tags: [templates, examples, rand-specs, faker, arrow]
sources:
  - rand_engine/examples/**
  - rand_engine/templates/**
---

## Example specs

- `CommonRandSpecs` (`RandSpecs` in the public API) supplies `customers`, `products`, `orders`, `transactions`, `employees`, `sensors`, `users`, `events`, `sales` and `devices`; each uses common methods and runs on both generators ([[data-generator]], [[spark-generator]]).
- `AdvancedRandSpecs` supplies ten pandas-oriented examples using correlated methods such as maps and patterns ([[generation-methods]]).
- Each example is a classmethod returning a fresh RandSpec dict that passes the validator ([[rand-spec-grammar]]).

## Spec builders

- `RandSpecs.faker_pool(provider, locale="en_US", pool_size=100, seed=None)` returns one `distincts` column holding `pool_size` values drawn from a local Faker instance; the same arguments with a `seed` give an equal pool, and no global random state changes. Generation samples that fixed pool through the generator's own random stream, so no Faker call happens at generation time.
- `faker_pool` raises `RandEngineError` for a missing Faker install (the optional extra `rand-engine[faker]`), an unknown provider or locale, a bad `pool_size` or non-scalar provider output.
- `RandSpecs.from_schema(schema, overrides=None)` accepts only a `pyarrow.Schema` and builds a validated RandSpec from field types; it reads no data and infers nothing from names. Duplicate fields, unknown override names and unsupported types raise `SpecValidationError`; the schema and overrides are never mutated.

| Arrow type | generated column |
|---|---|
| `bool` | `booleans` at probability 0.5 |
| signed and unsigned integers | `integers` from 0 to 100 with the matching `int_type` |
| floating point | `floats` from 0 to 1, two decimals |
| `string`, `large_string` | `uuid4` |
| `date32`, `date64` | `dates` spanning years 2000 to 2030 as `%Y-%m-%d` |
| timezone-free `timestamp` | `dates` over the same range as `%Y-%m-%d %H:%M:%S` |
| `null` | `constant` of `None` |

- Every other type (decimal, binary, time, duration, nested, dictionary, timezone-bearing timestamp) has no default and needs a complete override carrying `method`.
- An override with `method` replaces the whole column. One without it keeps the default method, merges `kwargs` key by key and replaces any modifier keys it supplies. Nullability adds no null rate.

## Templates

- `WebServerLogs.metadata()` returns the columns for an Apache common log entry; its timestamp transformer renders UTC and the final line carries `+0000`.
- `WebServerLogs.transformers()` joins those columns and returns only `log_entry`.
- `rand_engine.templates` re-exports `RandSpecs`; its package docstring marks that import deprecated in favour of `from rand_engine import RandSpecs`.
