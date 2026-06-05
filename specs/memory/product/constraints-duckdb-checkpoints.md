---
slug: constraints-duckdb-checkpoints
title: constraints and DuckDB checkpoints
category: product
tldr: 'PK/FK consistency uses DuckDB checkpoint tables and watermarks; checkpoint persistence lifecycle has known defects.'
summary: 'Current constraints feature: DuckDB stores generated PK candidates in checkpoint tables, then FK generation samples eligible rows by watermark.'
tags:
- constraints
- duckdb
- checkpoint
- referential-integrity
agent_tier: self-pull
token_estimate: 145
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

Constraints provide stateful referential integrity. The current handler uses
DuckDB to store generated primary-key candidates in checkpoint tables and sample
foreign-key values within a watermark window.

Current behavior is strongest for happy-path PK/FK consistency. QA identified
missing acceptance coverage for:

- Empty checkpoints.
- Expired watermark with no candidate rows.
- Persistent file-backed checkpoint reuse.
- In-memory checkpoint behavior.
- Concurrent or reused checkpoints.
- Invalid identifiers in generated queries.
- Duplicate key behavior.
- Multi-run deterministic behavior.

Known defect: calling `checkpoint(db_path)` after construction updates a stored
path but does not rewire the active constraints handler, so generation may still
use the original in-memory DuckDB connection.
