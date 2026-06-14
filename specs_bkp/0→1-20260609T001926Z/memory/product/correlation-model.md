---
slug: correlation-model
title: correlation model
category: product
tldr: 'Current correlations are in-memory advanced methods; DuckDB-backed correlation is future design work, not current behavior.'
summary: 'Correlation truth for restart: PyCore supports in-memory correlated values today; DuckDB is not yet a correlation engine and requires a first-class design spec.'
tags:
- correlation
- duckdb
- advanced-methods
agent_tier: self-pull
token_estimate: 170
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

Current correlation-like behavior is implemented in memory by `PyCore` methods
such as `distincts_map`, `distincts_multi_map`, `distincts_map_prop`, and
`complex_distincts`. These methods sample precomputed Python structures and are
useful for deterministic related values inside generated rows.

DuckDB is not currently a correlation engine. It is available as a DB handler
and as checkpoint state for constraints.

Future DuckDB-backed correlation work must define, before code changes:

- Whether DuckDB owns correlations, constraints, or both.
- External table/source registration.
- Privacy boundary for all external inputs: no production data, PII, unsafe
  fixtures, committed runtime logs, or unlicensed datasets; examples, templates,
  and tests must use synthetic, sanitized, or license-safe public test data.
- Security review before DuckDB/correlation code ingests sensitive production
  data or PII through external sources, persisted checkpoints, logs, examples,
  tests, or templates.
- Relationship graph and table/column typing.
- Conditional and weighted distributions.
- Materialization and persistence lifecycle.
- Query safety and identifier handling.
- Seed determinism across SQL sampling.
- Pandas/Spark parity and unsupported modes.
- Acceptance tests for empty state, invalid identifiers, duplicate keys,
  checkpoint reuse, concurrency, and representative performance.
