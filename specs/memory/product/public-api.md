---
slug: public-api
title: public API
category: product
tldr: 'Supported import surface is DataGenerator, SparkGenerator, and RandSpecs; runtime version policy is unresolved.'
summary: 'Current public API truth for rand-engine, including exported names, compatibility expectations, and release metadata gaps.'
tags:
- api
- semver
- package
agent_tier: self-pull
token_estimate: 130
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

`rand_engine.__all__` exports `DataGenerator`, `SparkGenerator`, and `RandSpecs`.
Treat these as the supported public import surface until an approved release
changes it.

Database handlers, core modules, validators, and writer internals are internal
implementation surfaces even when tests import them directly.

Current gaps:

- The package does not expose `rand_engine.__version__`, while release workflow
  text expects users to print it.
- Some tests describe a smaller public API than `__all__`.
- README/docs examples drift from inspected runtime behavior in places.

Future release work must align public API tests, docs, package metadata, and
semantic versioning before a stable release.
