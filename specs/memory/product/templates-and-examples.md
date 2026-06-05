---
slug: templates-and-examples
title: templates and examples
category: product
tldr: 'Built-in common/advanced specs and web-server-log template are product assets that require compatibility tests.'
summary: 'Current examples/templates truth: RandSpecs examples and templates are part of the user-facing value and must stay synchronized with validators/runtime.'
tags:
- templates
- examples
- rand-specs
agent_tier: self-pull
token_estimate: 90
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

`rand_engine.examples` and `rand_engine.templates` provide built-in RandSpecs and
domain examples. They are product assets, not throwaway demos.

Current test coverage exercises many common and advanced specs, but QA found
advanced example coverage gaps. Restart work must keep examples aligned with:

- Current validator grammar.
- Pandas runtime dispatch.
- Spark support boundaries.
- Public docs and README snippets.
- Seed and output expectations where documented.
