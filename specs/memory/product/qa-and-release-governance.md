---
slug: qa-and-release-governance
title: QA and release governance
category: product
tldr: 'Current suite passes 494 tests at 85.98% coverage; release/version/security gates need explicit restart decisions.'
summary: 'Current quality and release truth from QA and DevOps audits: tests are strong, SDD was not, and release metadata/pipeline gates need normalization.'
tags:
- qa
- release
- pypi
- ci
agent_tier: self-pull
token_estimate: 140
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

QA audit baseline on 2026-06-05:

- Full pytest suite in isolated environment: `494 passed`.
- Coverage: `85.98%`.
- Existing tests cover core generation, validators, DataGenerator, Spark, writers,
  DuckDB/SQLite, templates, and constraints.

Restart quality gaps:

- Specs/memory were placeholders and could not gate tests to acceptance criteria.
- Security jobs are advisory in some workflows.
- Coverage threshold is inconsistent across constitution/workflows.
- No lint/type gate is configured.
- Stale `_cdc_generator.py` can remain broken while tests pass.
- Repo-local `__pycache__` directories existed during audit.

Release truth:

- Stable source/PyPI/GitHub: `0.6.3`.
- Latest prerelease: `0.6.4rc1`.
- README advertises `0.7.0`, which is drift until approved.
