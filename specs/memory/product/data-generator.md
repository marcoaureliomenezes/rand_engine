---
slug: data-generator
title: DataGenerator
category: product
tldr: 'Pandas/NumPy composition root for deterministic dataframe generation, transforms, constraints, writers, and streams.'
summary: 'Current DataGenerator behavior: validates specs, seeds NumPy, generates Pandas dataframes, applies transforms, wires writers/streams, and applies DuckDB-backed constraints.'
tags:
- pandas
- numpy
- generator
- dataframe
agent_tier: self-pull
token_estimate: 160
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

`DataGenerator` is the main Pandas-facing generator. It accepts a RandSpec,
validates it, seeds NumPy, wires batch/stream writer facades, creates a
constraints handler, and exposes `get_df()`.

Generation flow:

- Evaluate size and lazy spec callables.
- Build first-level columns through the Pandas runtime method map.
- Apply embedded transformers and dataframe-level transformers.
- Apply PK/FK consistency through constraints handling.

Product guarantees to protect:

- Fast vectorized simple-column generation.
- Deterministic seeded generation where supported.
- User RandSpecs are immutable inputs.
- Writer/stream options remain explicit and testable.

Known restart defects:

- `checkpoint(db_path)` does not update the already-created active constraints
  handler.
- `DataGenerator` can mutate evaluated spec dictionaries by deleting
  `constraints`.
- Some accepted validator parameters drift from runtime method signatures.
