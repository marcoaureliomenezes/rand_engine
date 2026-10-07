---
slug: templates-and-examples
title: Templates and examples
tldr: "Ready RandSpecs — ten cross-engine CommonRandSpecs, ten pandas-only AdvancedRandSpecs, and a UTC WebServerLogs template."
summary: "Prebuilt specs a user runs without writing a grammar — CommonRandSpecs is exported as RandSpecs and runs on both generators; AdvancedRandSpecs demonstrates correlated pandas methods; WebServerLogs assembles Apache common log lines in UTC."
tags: [templates, examples, rand-specs]
sources:
  - rand_engine/examples/**
  - rand_engine/templates/**
---

## Example specs

- `CommonRandSpecs` (`RandSpecs` in the public API) supplies `customers`, `products`, `orders`, `transactions`, `employees`, `sensors`, `users`, `events`, `sales` and `devices`; each uses common methods and runs on both generators ([[data-generator]], [[spark-generator]]).
- `AdvancedRandSpecs` supplies ten pandas-oriented examples using correlated methods such as maps and patterns ([[generation-methods]]).
- Each example is a classmethod returning a fresh RandSpec dict whose parameter names agree with the validator.

## Templates

- `WebServerLogs.metadata()` returns the columns for an Apache common log entry; its timestamp transformer renders UTC and the final line carries `+0000`.
- `WebServerLogs.transformers()` joins those columns and returns only `log_entry`.
- `rand_engine.templates` re-exports `RandSpecs`; templates do not import Faker, so realistic pools remain user-provided input to `distincts`.
