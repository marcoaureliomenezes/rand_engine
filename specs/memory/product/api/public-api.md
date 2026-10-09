---
slug: public-api
title: Public API
tldr: "rand_engine exports DataGenerator, SparkGenerator and RandSpecs; every other module is internal."
summary: "The supported import surface is the three names in rand_engine.__all__, plus the RandEngineError exception family a caller catches; the wheel ships only the rand_engine package."
tags: [api, package, exceptions]
sources:
  - rand_engine/__init__.py
  - rand_engine/validators/exceptions.py
  - img/**
---

## Surface

- `from rand_engine import DataGenerator, SparkGenerator, RandSpecs` is the public surface (`__all__`) — [[data-generator]], [[spark-generator]], [[templates-and-examples]].
- `rand_engine.examples` also exposes `CommonRandSpecs` and `AdvancedRandSpecs`; `RandSpecs` is `CommonRandSpecs`.
- Cores, validators and writers are internal modules, importable but not part of the contract.
- The surface hands back DataFrames, record dicts and files — never a sink client; the caller forwards them to any platform.
- The package exposes no `__version__`; the version lives in `pyproject.toml`.

## Errors

- The library's own exceptions derive from `RandEngineError` (`rand_engine.validators.exceptions`).
- `SpecValidationError` — the spec failed validation at generator construction ([[rand-spec-grammar]]).
- `ColumnGenerationError` — a method raised while building a named column.
- `TransformerError` — a per-column transformer raised; the message names the column and the transformer index.
- `FileWriterError` — declared; no module raises it.

## Distribution

- PyPI distribution `rand-engine`, import package `rand_engine`; the wheel holds only `rand_engine/`.
- `img/` at the repo root holds README illustration images and a standalone script; the package never imports it.
