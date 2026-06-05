---
slug: writers-and-streaming
title: writers and streaming
category: product
tldr: 'Batch and stream writers support file outputs, but tests must prove read-back correctness and artifact hygiene.'
summary: 'Current writer truth: batch and streaming facades produce files in common formats; restart work must define correctness, cleanup, overwrite, and tmp-path policy.'
tags:
- writers
- streaming
- files
- qa
agent_tier: self-pull
token_estimate: 110
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

rand-engine includes batch and stream writer facades for generated data. Tests
exercise CSV, JSON, Parquet, compression modes, and streaming flows.

Current QA assessment: writer tests prove execution more than correctness in
some cases. Future accepted behavior must verify:

- Output file readability.
- Row counts.
- Schema and column order where relevant.
- Compression validity.
- Append/overwrite/destructive behavior.
- Partition/file-count semantics.
- Cleanup on interruption.

Tests must write to pytest `tmp_path` or workspace `.dadaia/tmp/`, not persistent
repo-local artifact directories.
