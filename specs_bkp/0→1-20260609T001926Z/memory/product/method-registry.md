---
slug: method-registry
title: method registry
category: product
tldr: 'Current method support is duplicated across validators, Pandas runtime, Spark runtime, examples, and docs; a canonical registry is future work.'
summary: 'Generation method support must become a single source of truth with per-engine metadata for Pandas, Spark, advanced/correlation status, determinism, and validation.'
tags:
- methods
- validators
- spark
- pandas
agent_tier: self-pull
token_estimate: 120
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

rand-engine currently encodes generation method support in several places:

- Common and advanced validators.
- Pandas runtime dispatch in `_rand_generator.py`.
- Spark runtime dispatch in `spark_generator.py` and `_spark_core.py`.
- Examples, templates, README, docs, and tests.

This duplication is accepted current-state debt. A future approved release
should create a canonical registry with metadata such as:

- Pandas support.
- Spark support.
- Advanced/correlation category.
- Accepted arguments and aliases.
- Determinism/seed behavior.
- Constraint/checkpoint compatibility.
- Experimental/deprecated status.

Until then, any method change must audit all maps and examples manually.
