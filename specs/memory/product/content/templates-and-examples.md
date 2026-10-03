---
slug: templates-and-examples
title: Templates and examples
tldr: "Ready RandSpecs — ten cross-engine CommonRandSpecs (exported as RandSpecs), ten pandas-only AdvancedRandSpecs, and the WebServerLogs template."
summary: "Prebuilt specs a user runs without writing a grammar — CommonRandSpecs uses only common methods so the same spec runs on DataGenerator and SparkGenerator; AdvancedRandSpecs adds correlated methods; WebServerLogs pairs a spec with transformers that emit Apache common log lines."
tags: [templates, examples, rand-specs]
sources:
  - rand_engine/examples/**
  - rand_engine/templates/**
  - rand_engine/utils/update.py
---

## Example specs

- `CommonRandSpecs` (`RandSpecs` in the public API) — `customers`, `products`, `orders`, `transactions`, `employees`, `sensors`, `users`, `events`, `sales`, `devices`; common methods only, so each runs on both generators ([[data-generator]], [[spark-generator]]).
- `AdvancedRandSpecs` — `products`, `orders`, `employees`, `devices`, `invoices`, `shipments`, `network_devices`, `vehicles`, `real_estate`, `healthcare`; they use the correlated methods and run on `DataGenerator` only ([[generation-methods]]).
- Each example is a classmethod returning a fresh RandSpec dict.

## Templates

- `rand_engine.templates.web_server_logs.WebServerLogs` implements `IRandomSpec`: `metadata()` returns the spec (IP pattern, request/status correlation, weighted HTTP version, timestamp, size) and `transformers()` returns the global transformers that join them into one `log_entry` column in Apache common log format.
- `rand_engine.templates` re-exports `RandSpecs`.
- No template imports Faker; realistic values come from user-built Faker pools passed as `distincts` ([[generation-methods]]).
- `Changer(cols).updater` is a global transformer that perturbs the named numeric columns and rotates the named object columns, simulating updated records.
